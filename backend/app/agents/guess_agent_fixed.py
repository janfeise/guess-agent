# 游戏核心：猜词游戏 agent

import json
import logging
import re

from langchain_openai import ChatOpenAI

from .utils.memory_policy import MemoryPolicy
from .utils.prompt_loader import PromptLoader
from .utils.streaming import (
    build_stream_chunk,
    build_stream_end,
    build_stream_error,
    build_stream_start,
)
from ..core.subject_pool import SubjectPool

logger = logging.getLogger(__name__)


class GuessAgent:
    def __init__(self, settings, prompt_loader: PromptLoader, memory_policy: MemoryPolicy):
        self.settings = settings
        self.prompt_loader = prompt_loader
        self.memory_policy = memory_policy
        self.agent_model = self._build_agent_model()
        self.helper_model = self._build_helper_model()

    def _build_agent_model(self):
        return ChatOpenAI(
            model=self.settings.agent_model_name,
            temperature=self.settings.agent_model_temperature,
            api_key=self.settings.agent_model_api_key,
            base_url=self.settings.agent_model_base_url,
        )

    def _build_helper_model(self):
        return ChatOpenAI(
            model=self.settings.helper_model_name,
            temperature=self.settings.helper_model_temperature,
            api_key=self.settings.helper_model_api_key,
            base_url=self.settings.helper_model_base_url,
        )

    def _load_prompt(self, mode):
        if mode == "helper":
            return self.prompt_loader.load_prompt("helper_system")
        return self.prompt_loader.load_prompt("guess_system")

    def _select_model(self, mode: str):
        if mode == "helper":
            return self.helper_model
        return self.agent_model

    def _build_messages(self, question: str, history: list[dict], mode: str):
        system_prompt = self._load_prompt(mode)
        recent_history = self.memory_policy.build_recent_history(history)
        summary = self.memory_policy.build_summary(history)

        messages: list[dict] = [{"role": "system", "content": system_prompt}]

        if summary:
            messages.append({"role": "system", "content": f"历史对话摘要：{summary}"})

        for item in recent_history:
            user_question = item.get("question", "")
            assistant_answer = item.get("answer", "")
            if user_question:
                messages.append({"role": "user", "content": user_question})
            if assistant_answer:
                messages.append({"role": "assistant", "content": assistant_answer})

        messages.append({"role": "user", "content": question})
        return messages

    @staticmethod
    def _build_last_turn_context(history: list[dict]) -> str:
        if not history:
            return ""

        last_turn = history[-1]
        if not isinstance(last_turn, dict):
            return ""

        question_text = last_turn.get("input_text") or last_turn.get("question") or last_turn.get("pending_question") or ""
        answer_text = last_turn.get("answer_text") or last_turn.get("answer") or ""
        if not question_text and not answer_text:
            return ""

        lines = ["最近一轮对话："]
        if question_text:
            lines.append(f"Agent：{question_text}")
        if answer_text:
            lines.append(f"User：{answer_text}")
        return "\n".join(lines)

    @staticmethod
    def _normalize_reasoning_history(history: list[dict]) -> list[dict]:
        normalized = []
        for item in history or []:
            if not isinstance(item, dict):
                continue
            if item.get("visible_to_agent") is False:
                continue
            normalized.append(item)
        return normalized

    @staticmethod
    def _format_history_entry(item: dict) -> str:
        parts = []
        round_no = item.get("round_no")
        if round_no is not None:
            parts.append(f"round={round_no}")
        actor = item.get("actor")
        if actor:
            parts.append(f"actor={actor}")
        turn_type = item.get("turn_type")
        if turn_type:
            parts.append(f"turn_type={turn_type}")
        source_word_owner = item.get("source_word_owner")
        if source_word_owner:
            parts.append(f"source={source_word_owner}")
        input_text = item.get("input_text")
        if input_text:
            parts.append(f"input={input_text}")
        answer_text = item.get("answer_text")
        if answer_text:
            parts.append(f"answer={answer_text}")
        answer_label = item.get("answer_label")
        if answer_label:
            parts.append(f"label={answer_label}")
        confidence = item.get("confidence")
        if confidence is not None:
            parts.append(f"confidence={confidence}")
        return " | ".join(parts)

    @classmethod
    def _format_history_for_prompt(cls, history: list[dict]) -> str:
        if not history:
            return "[]"

        lines = ["["]
        for item in history:
            lines.append(f"  {cls._format_history_entry(item)}")
        lines.append("]")
        return "\n".join(lines)

    def _normalize_answer(self, answer: str) -> str:
        return (answer or "").strip()

    @staticmethod
    def _compose_user_response(answer_label: str, hint: str | None = None) -> str:
        hint_text = (hint or "").strip()
        if answer_label == "yes":
            return f"是哦，{hint_text}哦" if hint_text else "是哦"
        if answer_label == "no":
            return f"不是哦，{hint_text}哦" if hint_text else "不是哦"
        if hint_text:
            return f"{hint_text}，我还不太确定哦"
        return "这个我还不太确定哦"

    @staticmethod
    def _normalize_intent_text(text: str) -> str:
        return re.sub(r"\s+", "", (text or "").strip().lower())

    @classmethod
    def _infer_local_answer(cls, normalized_text: str) -> str | None:
        if not normalized_text:
            return None

        if any(marker in normalized_text for marker in ("?", "？", "吗", "么", "是否")):
            return None

        yes_tokens = {"是", "是的", "对", "对的", "没错", "yes", "y", "true", "正确"}
        no_tokens = {"不是", "不", "不对", "不是的", "no", "n", "false", "否"}
        unknown_tokens = {"不知道", "不清楚", "不晓得", "unknown", "无法判断"}

        if normalized_text in yes_tokens:
            return "yes"
        if normalized_text in no_tokens:
            return "no"
        if normalized_text in unknown_tokens:
            return "unknown"

        if normalized_text.startswith(("不是", "不对", "并不是", "不属于", "没有", "非")):
            return "no"

        if normalized_text.startswith(("是", "对", "没错", "正确")):
            return "yes"

        return None

    @staticmethod
    def _looks_like_question(normalized_text: str) -> bool:
        if not normalized_text:
            return False

        question_markers = ("?", "？", "吗", "么", "是否", "能否", "可否", "是不是", "能不能", "可不可以", "请问")
        return any(marker in normalized_text for marker in question_markers)

    @staticmethod
    def _looks_like_guess(normalized_text: str) -> bool:
        if not normalized_text:
            return False

        guess_markers = ("我猜", "猜是", "应该是", "大概是", "可能是", "也许是")
        return any(marker in normalized_text for marker in guess_markers)

    @classmethod
    def _infer_local_intent(cls, user_input: str) -> dict | None:
        normalized = cls._normalize_intent_text(user_input)
        if not normalized:
            return None

        answer = cls._infer_local_answer(normalized)
        if answer is not None:
            return {
                "intent": "answer",
                "normalized_text": normalized,
                "guess_word": "",
                "answer": answer,
                "confidence": 0.95,
                "reason": "local_answer_heuristic",
            }

        if cls._looks_like_guess(normalized):
            guess_word = normalized.replace("我猜", "").replace("猜是", "").replace("应该是", "").strip("。！？!? ")
            return {
                "intent": "guess",
                "normalized_text": normalized,
                "guess_word": guess_word,
                "answer": "unknown",
                "confidence": 0.7,
                "reason": "local_guess_heuristic",
            }

        if cls._looks_like_question(normalized):
            return {
                "intent": "question",
                "normalized_text": normalized,
                "guess_word": "",
                "answer": "unknown",
                "confidence": 0.7,
                "reason": "local_question_heuristic",
            }

        return None

    def _is_model_unavailable_error(self, error: Exception) -> bool:
        error_text = str(error).lower()
        return "model does not exist" in error_text or "20012" in error_text

    def _parse_json_response(self, content: str, fallback: dict | None = None) -> dict:
        default_result = fallback or {}
        if not content:
            logger.warning("Agent 返回空内容，使用兜底结果")
            return default_result

        candidates = [content.strip()]
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", content, re.IGNORECASE | re.DOTALL)
        if match:
            candidates.insert(0, match.group(1).strip())

        for candidate in candidates:
            try:
                parsed = json.loads(candidate)
            except json.JSONDecodeError:
                continue

            if isinstance(parsed, dict):
                return parsed

        logger.warning("Agent 返回非 JSON 内容，使用兜底结果: %s", content[:120])
        return default_result

    @staticmethod
    def _format_json_for_log(payload) -> str:
        try:
            return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
        except TypeError:
            return json.dumps(str(payload), ensure_ascii=False, indent=2)

    def _log_llm_request(self, stage: str, messages: list[dict]) -> None:
        logger.info("LLM 请求 [%s]:\n%s", stage, self._format_json_for_log(messages))

    def _log_llm_response(self, stage: str, raw_content: str, parsed_content: dict | None = None) -> None:
        logger.info("LLM 原始返回 [%s]: %s", stage, raw_content or "")
        if parsed_content is not None:
            logger.info("LLM JSON 格式化结果 [%s]:\n%s", stage, self._format_json_for_log(parsed_content))

    async def generate_start_word(self, difficulty: str | None = None, subject: str | None = None) -> str:
        system_prompt = self.prompt_loader.load_prompt("game_start")
        subjects_info = SubjectPool.get_subjects_formatted_prompt_segment()
        full_system_prompt = f"{system_prompt}\n\n可选学科范围：{subjects_info}"
        user_prompt = (
            f"请根据以下约束生成目标词.\n"
            f"难度：{difficulty or 'medium'}\n"
            f"要求：只返回一个词语，不要任何解释或额外文本。"
        )

        if subject:
            user_prompt += f"\n学科领域：{subject}"

        messages = [
            {"role": "system", "content": full_system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = await self.helper_model.ainvoke(messages)
            start_word = self._normalize_answer(response.content)
            if not start_word:
                raise ValueError("LLM returned an empty start word")
            return start_word
        except Exception as e:
            logger.exception("生成开局词失败: %s", e)
            if self._is_model_unavailable_error(e):
                raise ValueError("当前小助手模型不可用，请联系作者检查模型配置后才试。") from e
            raise ValueError("小助手暂时无法生成开局词，请稍后重试。") from e

    async def answer(self, question: str, history: list[dict], mode: str = "agent"):
        messages = self._build_messages(question, history, mode)
        model = self._select_model(mode)

        try:
            response = await model.agenerate(messages)
            answer = self._normalize_answer(response.generations[0][0].text)
            return {
                "answer": answer,
                "history": history + [{"question": question, "answer": answer}],
            }
        except Exception as e:
            logger.exception("生成回答失败: %s", e)
            return "Sorry, I encountered an error while processing your request."

    async def stream_answer(self, question: str, history: list[dict], mode: str = "agent"):
        messages = self._build_messages(question, history, mode)
        model = self._select_model(mode)

        yield build_stream_start()

        try:
            full_answer_chunks: list[dict] = []
            async for chunk in model.astream(messages):
                chunk_text = self._normalize_answer(chunk.generations[0][0].text)
                full_answer_chunks.append({"role": "assistant", "content": chunk_text})
                yield build_stream_chunk(chunk_text)
        except Exception as e:
            logger.exception("生成流式回答失败: %s", e)
            yield build_stream_error("Sorry, I encountered an error while processing your request.")
        finally:
            yield build_stream_end()

    async def parse_user_intent(self, user_input: str, history: list[dict]) -> dict:
        last_turn_context = self._build_last_turn_context(history)
        messages = [
            {"role": "system", "content": self.prompt_loader.load_prompt("turn_router")},
        ]

        if last_turn_context:
            messages.append({"role": "user", "content": last_turn_context})

        messages.append({"role": "user", "content": f"请根据最近一轮对话分析用户输入的意图：{user_input}"})

        try:
            self._log_llm_request("parse_user_intent", messages)
            response = await self.agent_model.ainvoke(messages)
            raw_content = response.content or ""
            self._log_llm_response("parse_user_intent/raw", raw_content)
            parsed = self._parse_json_response(
                raw_content,
                fallback={
                    "intent": "invalid",
                    "reason": "fallback_parse_failed",
                    "raw_content": raw_content,
                },
            )
            parsed.setdefault("intent", "invalid")
            parsed.setdefault("normalized_text", self._normalize_intent_text(user_input))
            parsed.setdefault("guess_word", "")
            parsed.setdefault("answer", "unknown")

            local_intent = self._infer_local_intent(user_input)
            if local_intent is not None and (
                parsed.get("intent") == "invalid" or local_intent["intent"] == "answer"
            ):
                parsed.update(local_intent)

            if parsed.get("intent") == "invalid" and not parsed.get("reason"):
                parsed["reason"] = "invalid_input"

            self._log_llm_response("parse_user_intent/parsed", raw_content, parsed)
            return parsed
        except Exception as e:
            logger.exception("解析用户意图失败: %s", e)
            local_intent = self._infer_local_intent(user_input)
            if local_intent is not None:
                return local_intent
            return {
                "intent": "invalid",
                "reason": "llm_error",
                "normalized_text": self._normalize_intent_text(user_input),
                "guess_word": "",
                "answer": "unknown",
            }

    async def answer_question(self, question: str, answer: str) -> dict:
        messages = [
            {"role": "system", "content": self.prompt_loader.load_prompt("guess_system")},
            {"role": "system", "content": f"真实答案：{answer}"},
            {"role": "user", "content": question},
        ]

        try:
            self._log_llm_request("answer_question", messages)
            response = await self.agent_model.ainvoke(messages)
            raw_content = response.content or ""
            self._log_llm_response("answer_question/raw", raw_content)
            parsed = self._parse_json_response(
                raw_content,
                fallback={
                    "answer": "unknown",
                    "response_text": raw_content.strip() or "这个我还不太确定哦",
                    "hint": "",
                    "confidence": 0.0,
                    "reason": "fallback_parse_failed",
                },
            )
            parsed["answer"] = parsed.get("answer", "unknown") if parsed.get("answer") in {"yes", "no", "unknown"} else "unknown"
            parsed.setdefault("response_text", self._compose_user_response(parsed.get("answer", "unknown"), parsed.get("hint", "")))
            parsed.setdefault("hint", "")
            parsed.setdefault("confidence", 0.0)
            parsed.setdefault("reason", "")
            if not parsed.get("response_text"):
                parsed["response_text"] = self._compose_user_response(parsed.get("answer", "unknown"), parsed.get("hint", ""))
            self._log_llm_response("answer_question/parsed", raw_content, parsed)
            return parsed
        except Exception as e:
            logger.exception("判断用户回答失败: %s", e)
            return {
                "answer": "unknown",
                "response_text": "这个我还不太确定哦",
                "hint": "",
                "confidence": 0.0,
                "reason": "llm_error",
            }

    async def decide_agent_action(self, history: list[dict], summary: str) -> dict:
        reasoning_history = self._normalize_reasoning_history(history)
        messages = [
            {"role": "system", "content": self.prompt_loader.load_prompt("agent_decision")},
            {"role": "user", "content": f"历史对话：\n{self._format_history_for_prompt(reasoning_history)}\n对话摘要：{summary}"},
        ]

        try:
            self._log_llm_request("decide_agent_action", messages)
            response = await self.agent_model.ainvoke(messages)
            raw_content = response.content or ""
            self._log_llm_response("decide_agent_action/raw", raw_content)
            parsed = self._parse_json_response(
                raw_content,
                fallback={
                    "action": "question",
                    "question": "请继续提供更多信息。",
                    "confidence": 0.0,
                    "raw_content": raw_content,
                },
            )
            parsed.setdefault("action", "question")
            if parsed.get("action") == "guess":
                parsed.setdefault("guess_word", "")
            else:
                parsed.setdefault("question", "请继续提供更多信息。")
            parsed.setdefault("confidence", 0.0)
            self._log_llm_response("decide_agent_action/parsed", raw_content, parsed)
            return parsed
        except Exception as e:
            logger.exception("决定 agent 行动失败: %s", e)
            return {
                "action": "question",
                "question": "请继续提供更多信息。",
                "confidence": 0.0,
            }
