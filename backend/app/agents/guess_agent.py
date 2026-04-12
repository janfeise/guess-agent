# 游戏核心：猜数字游戏agent

# 导入日志模块
import logging

# 导入 langchain openai 模块中的 ChatOpenAI 类，用于与 OpenAI 的聊天模型进行交互
from langchain_openai import ChatOpenAI

# 导入 utils 的各个模块
from .utils.prompt_loader import PromptLoader
from .utils.memory_policy import MemoryPolicy
from .utils.streaming import (
    build_stream_chunk,
    build_stream_end,
    build_stream_error,
    build_stream_start,
)

logger = logging.getLogger(__name__)

class GuessAgent:
    def __init__(self, settings, prompt_loader, memory_policy):
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
        # 构建agent模型的输入消息列表，包含系统提示、历史对话和当前问题
        system_prompt = self._load_prompt(mode)
        recent_history = self.memory_policy.build_recent_history(history)
        summary = self.memory_policy.build_summary(history)

        messages: list[dict] = []
        messages.append({"role": "system", "content": system_prompt})

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


    def _normalize_answer(self, answer: str) -> str:
        # 对模型生成的答案进行规范化处理
        return answer.strip()

    def _is_model_unavailable_error(self, error: Exception) -> bool:
        error_text = str(error).lower()
        return "model does not exist" in error_text or "20012" in error_text
    
    async def generate_start_word(self, difficulty: str | None = None, subject: str | None = None) -> str:
        # 根据提供的主题和难度，生成一个适合猜数字游戏的起始词
        system_prompt = self.prompt_loader.load_prompt("game_start")
        user_prompt = (
            f"请根据以下约束生成目标词.\n"
            f"难度：{difficulty or 'medium'}\n"
            f"要求：只返回一个词语，不要任何解释或额外文本。"
        )

        if subject:
            user_prompt += f"\n学科领域：{subject}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            response = await self.helper_model.ainvoke(messages)
            start_word = self._normalize_answer(response.content)
            if not start_word:
                raise ValueError("LLM returned an empty start word")
            return start_word
        except Exception as e:
            if self._is_model_unavailable_error(e):
                raise ValueError("当前小助手模型不可用，请联系作者检查模型配置后才试。") from e

            raise ValueError("小助手暂时无法生成开局词，请稍后重试。") from e

    async def answer(self, question: str, history: list[dict], mode: str = 'agent'):
        messages = self._build_messages(question, history, mode)
        model = self._select_model(mode)

        try:
            response = await model.agenerate(messages)
            answer = self._normalize_answer(response.generations[0][0].text)
            return {
                "answer": answer,
                "history": history + [{"question": question, "answer": answer}]
            }
        except Exception as e:
            print(f"Error occurred while generating answer: {e}")
            return "Sorry, I encountered an error while processing your request."


    async def stream_answer(self, question: str, history: list[dict], mode: str = 'agent'):
        # 处理用户问题，调用agent模型生成答案，并以流式方式返回答案和更新后的历史记录
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
            print(f"Error occurred while generating stream answer: {e}")
            yield build_stream_error("Sorry, I encountered an error while processing your request.")
        finally:
            yield build_stream_end()
