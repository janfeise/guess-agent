# 游戏service层，负责处理游戏相关的业务逻辑

import logging
import re
import secrets
import uuid
from datetime import datetime

from app.agents.utils.streaming import build_stream_chunk, build_stream_end
from app.core.constants import validate_start_word
from app.core.security import decrypt, encrypt
from cryptography.fernet import InvalidToken

from .utils.turn_lock import TurnLock

logger = logging.getLogger(__name__)


class GameService:
	def __init__(self, settings, agent, repository, memory_policy):
		self.settings = settings
		self.agent = agent
		self.repository = repository
		self.memory_policy = memory_policy

	@staticmethod
	def _preview_text(text: str | None, limit: int = 120) -> str:
		value = (text or "").strip().replace("\n", " ")
		if len(value) <= limit:
			return value
		return value[:limit] + "..."

	@staticmethod
	def _build_initial_metadata() -> dict:
		return {
			"phase": "user_turn",
			"game_mode": "dual_word_isolated",
			"reasoning_scope": "user_word",
			"next_actor": "user",
			"expected_turn_type": "question",
			"last_actor": "system",
			"last_intent": None,
			"awaiting_judgement": False,
			"awaiting_answer": False,
			"pending_guess": "",
			"pending_question": "",
			"agent_confidence": 0.0,
		}

	@staticmethod
	def _make_history_item(
		*,
		round_no: int,
		actor: str,
		turn_type: str,
		input_text: str,
		answer_text: str = "",
		answer_label: str | None = None,
		hint: str | None = None,
		confidence: float = 0.0,
		result: str = "",
		source_word_owner: str = "user",
		visible_to_agent: bool = True,
		visible_to_player: bool = True,
	) -> dict:
		item = {
			"round_no": round_no,
			"actor": actor,
			"turn_type": turn_type,
			"input_text": input_text,
			"answer_text": answer_text,
			"confidence": confidence,
			"result": result,
			"source_word_owner": source_word_owner,
			"visible_to_agent": visible_to_agent,
			"visible_to_player": visible_to_player,
		}
		if answer_label is not None:
			item["answer_label"] = answer_label
		if hint is not None:
			item["hint"] = hint
		return item

	@staticmethod
	def _get_turn_lock_state(game: dict) -> dict:
		metadata = game.get("metadata", {}) or {}
		return {
			"phase": metadata.get("phase", "user_turn"),
			"next_actor": metadata.get("next_actor", "user"),
			"expected_turn_type": metadata.get("expected_turn_type", "question"),
			"last_actor": metadata.get("last_actor", "system"),
			"last_intent": metadata.get("last_intent"),
		}

	@staticmethod
	def _is_turn_allowed(phase: str, intent: str) -> bool:
		if phase == "awaiting_answer":
			return intent == "answer"
		if phase == "awaiting_judgement":
			return intent in {"judge", "answer"}
		if phase == "user_turn":
			return intent in {"question", "guess"}
		return intent == "question"

	@staticmethod
	def _reject_turn(game_id: str, phase: str, message: str, history: list[dict] | None = None):
		return {
			"game_id": game_id,
			"status": "active",
			"phase": phase,
			"message": message,
			"history": history or [],
		}

	@staticmethod
	def build_reasoning_history(history: list[dict], target_owner: str) -> list[dict]:
		reasoning_history = []
		for item in history or []:
			if not isinstance(item, dict):
				continue
			if item.get("source_word_owner") != target_owner:
				continue
			if not item.get("visible_to_agent", True):
				continue
			reasoning_history.append(
				{
					"round_no": item.get("round_no"),
					"actor": item.get("actor"),
					"turn_type": item.get("turn_type"),
					"input_text": item.get("input_text", ""),
					"answer_text": item.get("answer_text", ""),
					"answer_label": item.get("answer_label"),
					"confidence": item.get("confidence", 0.0),
				}
			)
		return reasoning_history

	@staticmethod
	def normalize_guess_text(text: str) -> str:
		return (text or "").strip().lower()

	@staticmethod
	def is_guess_correct(user_guess: str, target_word: str) -> bool:
		return GameService.normalize_guess_text(user_guess) == GameService.normalize_guess_text(target_word)

	@staticmethod
	def sanitize_history_for_client(history: list[dict]) -> list[dict]:
		"""
		清理 history 中的敏感字段，避免向客户端泄露答案。
		移除 result 字段中包含的 LLM reasoning 和其他敏感信息。
		"""
		sanitized = []
		for item in history:
			clean_item = dict(item)
			# 移除 result 字段（可能包含答案的推理过程）
			if "result" in clean_item:
				del clean_item["result"]
			sanitized.append(clean_item)
		return sanitized

	@staticmethod
	def reveal_target_word(game_doc: dict, settings) -> str:
		system_password_encrypted = game_doc["system_password_encrypted"]
		system_password = decrypt(system_password_encrypted, settings.encryption_secret)
		try:
			return decrypt(game_doc["system_word_encrypted"], system_password)
		except InvalidToken:
			logger.warning("系统词解密失败，尝试兼容旧数据格式: game_id=%s", game_doc.get("game_id"))
			return decrypt(game_doc["system_word_encrypted"], system_password_encrypted)

	@staticmethod
	def _normalize_answer_candidate(text: str) -> str:
		return re.sub(r"\s+", "", (text or "").strip().lower())

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

	@classmethod
	def _resolve_user_answer(cls, user_input: str, intent_result: dict | None = None) -> str | None:
		candidate = cls._normalize_answer_candidate((intent_result or {}).get("normalized_text") or user_input)
		parsed_answer = (intent_result or {}).get("answer")

		if parsed_answer in {"yes", "no", "unknown"} and (intent_result or {}).get("intent") == "answer":
			return parsed_answer
		if not candidate:
			return None
		if any(marker in candidate for marker in ("?", "？", "吗", "么", "是否")):
			return None

		yes_tokens = {"是", "是的", "对", "对的", "没错", "yes", "y", "true", "正确"}
		no_tokens = {"不是", "不", "不对", "不是的", "no", "n", "false", "否"}
		unknown_tokens = {"不知道", "不清楚", "不晓得", "unknown", "无法判断"}

		if candidate in yes_tokens or candidate.startswith(("是", "对", "没错", "正确")):
			return "yes"
		if candidate in no_tokens or candidate.startswith(("不是", "不对", "并不是", "不属于", "没有", "非")):
			return "no"
		if candidate in unknown_tokens:
			return "unknown"
		return None

	async def create_game(self, owner_id=None, user_word: str | None = None, difficulty: str | None = None):
		if not user_word:
			raise ValueError("开局词不能为空")

		normalized_user_word = validate_start_word(user_word)
		game_id = str(uuid.uuid4())
		now = datetime.now()

		target_word = await self.agent.generate_start_word(difficulty=difficulty)
		normalized_system_word = validate_start_word(target_word)
		system_password = secrets.token_hex(16)
		system_password_encrypted = encrypt(system_password, self.settings.encryption_secret)
		system_word_encrypted = encrypt(normalized_system_word, system_password)

		game_doc = {
			"game_id": game_id,
			"owner_id": owner_id,
			"status": "active",
			"history": [],
			"summary": "",
			"round_count": 0,
			"created_at": now,
			"updated_at": now,
			"metadata": self._build_initial_metadata(),
			"difficulty": difficulty or "medium",
			"user_word": normalized_user_word,
			"system_word": normalized_system_word,
			"system_word_encrypted": system_word_encrypted,
			"system_password_encrypted": system_password_encrypted,
			"target_word_source": "helper_llm",
		}

		await self.repository.create_game(game_doc)
		return {
			"game_id": game_id,
			"status": "active",
			"round_count": 0,
			"difficulty": difficulty or "medium",
			"user_word": normalized_user_word,
			"system_word_encrypted": system_word_encrypted,
			"created_at": now,
		}

	async def get_game(self, game_id: str):
		game = await self.repository.get_game(game_id)
		if not game:
			raise ValueError(f"Game with id {game_id} not found")
		return game

	async def submit_turn_stream(self, game_id: str, question: str, mode: str = "agent"):
		game = await self.repository.get_game(game_id)
		if not game:
			raise ValueError(f"Game with id {game_id} not found")
		if game.get("status") == "finished":
			raise ValueError(f"Game with id {game_id} has already finished")

		history = game.get("history", [])
		yield build_stream_chunk()
		full_answer_text = ""

		try:
			async for chunk in self.agent.stream_answer(question, history, mode):
				if chunk.get("type") == "chunk":
					full_answer_text += chunk.get("content", "")

			updated_history = history + [
				self._make_history_item(
					round_no=len(history) + 1,
					actor="user",
					turn_type="question",
					input_text=question,
					answer_text=full_answer_text,
					source_word_owner="user",
					visible_to_agent=False,
					visible_to_player=True,
				)
			]
			await self.repository.update_game_history(
				game_id,
				history=updated_history,
				summary=self.memory_policy.build_summary(updated_history),
				round_count=len(updated_history),
			)
			yield build_stream_end()
		except Exception as exc:
			logger.exception("流式回合处理失败: %s", exc)
			yield build_stream_chunk("Sorry, I encountered an error while processing your request.")
			raise

	async def end_game(self, game_id: str, reason: str = "manual"):
		game = await self.repository.get_game(game_id)
		if not game:
			raise ValueError(f"Game with id {game_id} not found")
		if game.get("status") == "finished":
			return game

		now = datetime.now()
		await self.repository.finish_game(game_id, reason=reason, finished_at=now)
		return {
			"game_id": game_id,
			"status": "finished",
			"finished_at": now,
			"reason": reason,
		}

	async def submit_turn(self, game_id: str, question: str, mode: str = "agent", turn_type: str = "input"):
		game = await self.repository.get_game(game_id)
		if not game:
			raise ValueError(f"Game with id {game_id} not found")
		if game.get("status") == "finished":
			raise ValueError(f"Game with id {game_id} has already finished")

		metadata = game.get("metadata", {}) or {}
		phase = metadata.get("phase", "user_turn")
		history = game.get("history", [])

		intent_result = await self.agent.parse_user_intent(question, history)
		intent = intent_result.get("intent", "invalid")

		# 轮次锁校验：根据 phase 判断当前允许的意图
		if phase == "awaiting_judgement":
			if intent not in {"judge", "answer"}:
				return self._reject_turn(game_id, phase, "请先判断系统猜测是否正确", history)
			return await self._handle_agent_guess_judgement(game, question)

		if phase == "awaiting_answer":
			if intent != "answer":
				return self._reject_turn(game_id, phase, "请先回答上一轮问题", history)
			return await self._handle_user_answer(game, question, history, intent_result)

		# user_turn 阶段：只允许 question 和 guess
		if phase == "user_turn":
			if intent == "invalid":
				return self._reject_turn(game_id, phase, "请输入有效问题或提问", history)
			if intent == "guess":
				return await self._handle_user_guess(game, intent_result)
			if intent == "answer":
				return self._reject_turn(game_id, phase, "现在轮到你提问或猜词，不是回答阶段", history)
			if intent == "question":
				return await self._handle_user_question(game, question, history, mode)

		return self._reject_turn(game_id, phase, "当前轮次状态异常", history)

	async def _handle_user_guess(self, game: dict, intent_result: dict):
		target_word = self.reveal_target_word(game, self.settings)
		user_guess = intent_result.get("guess_word", "")

		if self.is_guess_correct(user_guess, target_word):
			now = datetime.now()
			await self.repository.finish_game(game["game_id"], reason="user_win", finished_at=now)
			return {
				"game_id": game["game_id"],
				"status": "finished",
				"result": "user_win",
				"message": f"恭喜你猜对了！目标词是：{target_word}",
			}

		updated_history = game.get("history", []) + [
			self._make_history_item(
				round_no=game.get("round_count", 0) + 1,
				actor="user",
				turn_type="guess",
				input_text=user_guess,
				answer_text="wrong_guess",
				result="guess_incorrect",
				source_word_owner="system",
				visible_to_agent=False,
				visible_to_player=True,
			)
		]

		await self.repository.update_game_state(
			game["game_id"],
			history=updated_history,
			summary=self.memory_policy.build_summary(updated_history),
			round_count=len(updated_history),
			phase="user_turn",
			awaiting_judgement=False,
			awaiting_answer=False,
			pending_guess="",
			pending_question="",
			agent_confidence=0.0,
			last_actor="user",
			last_intent="guess",
			game_mode=game.get("metadata", {}).get("game_mode"),
			reasoning_scope=game.get("metadata", {}).get("reasoning_scope"),
			next_actor="user",
			expected_turn_type="question",
		)

		return {
			"game_id": game["game_id"],
			"status": game.get("status"),
			"phase": "user_turn",
			"result": "guess_incorrect",
			"message": f"很遗憾，{user_guess} 不是目标词，游戏继续。现在轮到你继续提问或猜词。",
			"history": updated_history,
		}

	async def _handle_agent_guess_judgement(self, game: dict, user_input: str):
		pending_guess = game.get("metadata", {}).get("pending_guess", "")
		judgment_text = user_input.strip().lower()

		if judgment_text in ["是", "正确", "对了", "yes"]:
			now = datetime.now()
			await self.repository.finish_game(game["game_id"], reason="agent_win_guessed_correctly", finished_at=now)
			return {
				"game_id": game["game_id"],
				"status": "finished",
				"result": "agent_win",
				"message": "系统猜测正确！游戏结束",
			}

		history = game.get("history", []) + [
			self._make_history_item(
				round_no=game.get("round_count", 0) + 1,
				actor="user",
				turn_type="judge_agent_guess",
				input_text=user_input,
				answer_text="agent_guess_wrong",
				result=f"pending_guess={pending_guess}",
				source_word_owner="user",
				visible_to_agent=True,
				visible_to_player=True,
			)
		]

		# 轮次锁：系统猜测错误后，回到 user_turn
		await self.repository.update_game_state(
			game["game_id"],
			history=history,
			summary=self.memory_policy.build_summary(history),
			round_count=len(history),
			phase="user_turn",
			awaiting_judgement=False,
			awaiting_answer=False,
			pending_guess="",
			pending_question="",
			agent_confidence=0.0,
			last_actor="user",
			last_intent="answer",
			game_mode=game.get("metadata", {}).get("game_mode"),
			reasoning_scope=game.get("metadata", {}).get("reasoning_scope"),
			next_actor="user",
			expected_turn_type="question",
		)

		return {
			"game_id": game["game_id"],
			"status": "active",
			"message": f"系统猜测 {pending_guess} 不正确，游戏继续。现在轮到你提问或猜词。",
			"history": history,
			"phase": "user_turn",
		}

	async def _handle_user_question(self, game: dict, question: str, history: list[dict], mode: str = "agent"):
		target_word = self.reveal_target_word(game, self.settings)
		answer_result = await self.agent.answer_question(question, target_word)

		if isinstance(answer_result, dict):
			answer_label = answer_result.get("answer", "unknown")
			answer_text = answer_result.get("response_text") or self._compose_user_response(
				answer_label,
				answer_result.get("hint", ""),
			)
			answer_reason = answer_result.get("reason", "")
			answer_hint = answer_result.get("hint", "")
			answer_confidence = answer_result.get("confidence", 0.0)
		else:
			answer_label = "unknown"
			answer_text = str(answer_result)
			answer_reason = ""
			answer_hint = ""
			answer_confidence = 0.0

		# 用户问题的回答加入 history（在 agent 不可见的 raw_history 中）
		raw_history = history + [
			self._make_history_item(
				round_no=game.get("round_count", 0) + 1,
				actor="user",
				turn_type="question",
				input_text=question,
				answer_text=answer_text,
				answer_label=answer_label,
				hint=answer_hint,
				confidence=answer_confidence,
				result="user_asked_question",
				source_word_owner="system",
				visible_to_agent=False,
				visible_to_player=True,
			)
		]

		# 系统决策：是继续提问还是开始猜测
		summary = self.memory_policy.build_summary(raw_history)
		agent_decision = await self.agent.decide_agent_action(raw_history, summary)
		agent_action = agent_decision.get("action", "ask")

		# 系统的决策加入 history
		updated_history = raw_history

		if agent_action == "ask":
			# 系统决定继续询问
			agent_question = agent_decision.get("question", "请继续提供更多信息。")
			updated_history = updated_history + [
				self._make_history_item(
					round_no=len(updated_history) + 1,
					actor="system",
					turn_type="question",
					input_text=agent_question,
					answer_text="pending",
					result="system_asks_question",
					source_word_owner="system",
					visible_to_agent=True,
					visible_to_player=True,
				)
			]

			# 更新游戏状态：等待用户回答系统问题
			await self.repository.update_game_state(
				game["game_id"],
				history=updated_history,
				summary=self.memory_policy.build_summary(updated_history),
				round_count=len(updated_history),
				phase="awaiting_answer",
				awaiting_judgement=False,
				awaiting_answer=True,
				pending_guess="",
				pending_question=agent_question,
				agent_confidence=agent_decision.get("confidence", 0.0),
				last_actor="system",
				last_intent="question",
				game_mode=game.get("metadata", {}).get("game_mode"),
				reasoning_scope=game.get("metadata", {}).get("reasoning_scope"),
				next_actor="user",
				expected_turn_type="answer",
			)

			return {
				"game_id": game["game_id"],
				"status": game.get("status", "active"),
				"phase": "awaiting_answer",
				"answer": answer_label,
				"response_text": answer_text,
				"answer_text": answer_text,
				"hint": answer_hint,
				"confidence": answer_confidence,
				"system_question": agent_question,
				"history": updated_history,
				"message": f"我的下一个问题是：{agent_question}",
			}

		else:  # agent_action == "guess"
			# 系统决定开始猜测
			guess_word = agent_decision.get("guess_word", "unknown")
			updated_history = updated_history + [
				self._make_history_item(
					round_no=len(updated_history) + 1,
					actor="system",
					turn_type="guess",
					input_text=guess_word,
					answer_text="pending",
					result="system_makes_guess",
					source_word_owner="system",
					visible_to_agent=True,
					visible_to_player=True,
				)
			]

			# 更新游戏状态：等待用户判断系统猜测
			await self.repository.update_game_state(
				game["game_id"],
				history=updated_history,
				summary=self.memory_policy.build_summary(updated_history),
				round_count=len(updated_history),
				phase="awaiting_judgement",
				awaiting_judgement=True,
				awaiting_answer=False,
				pending_guess=guess_word,
				pending_question="",
				agent_confidence=agent_decision.get("confidence", 0.0),
				last_actor="system",
				last_intent="guess",
				game_mode=game.get("metadata", {}).get("game_mode"),
				reasoning_scope=game.get("metadata", {}).get("reasoning_scope"),
				next_actor="user",
				expected_turn_type="judge",
			)

			return {
				"game_id": game["game_id"],
				"status": game.get("status", "active"),
				"phase": "awaiting_judgement",
				"answer": answer_label,
				"response_text": answer_text,
				"answer_text": answer_text,
				"hint": answer_hint,
				"confidence": answer_confidence,
				"system_guess": guess_word,
				"history": updated_history,
				"message": f"我猜你想的词是：{guess_word}。对吗？（是/不是）",
			}

	async def _handle_user_answer(self, game: dict, user_input: str, history: list[dict], intent_result: dict | None = None):
		resolved_answer = self._resolve_user_answer(user_input, intent_result)

		if resolved_answer is None:
			return {
				"game_id": game["game_id"],
				"status": game.get("status", "active"),
				"phase": game.get("metadata", {}).get("phase", "awaiting_answer"),
				"message": "请回答是、否或不知道",
				"history": history,
			}

		# 用户回答记入 history
		updated_history = history + [
			self._make_history_item(
				round_no=game.get("round_count", 0) + 1,
				actor="user",
				turn_type="answer",
				input_text=user_input,
				answer_text=resolved_answer,
				result="user_answer_recorded",
				source_word_owner="user",
				visible_to_agent=True,
				visible_to_player=True,
			)
		]

		# 轮次锁：用户回答后直接回到 user_turn，不立即进行下一步决策
		# 系统的决策应该只在用户提问时发生，不是在用户回答后
		await self.repository.update_game_state(
			game["game_id"],
			history=updated_history,
			summary=self.memory_policy.build_summary(updated_history),
			round_count=len(updated_history),
			phase="user_turn",
			awaiting_judgement=False,
			awaiting_answer=False,
			pending_guess="",
			pending_question="",
			agent_confidence=0.0,
			last_actor="user",
			last_intent="answer",
			game_mode=game.get("metadata", {}).get("game_mode"),
			reasoning_scope=game.get("metadata", {}).get("reasoning_scope"),
			next_actor="user",
			expected_turn_type="question",
		)

		return {
			"game_id": game["game_id"],
			"status": game.get("status", "active"),
			"phase": "user_turn",
			"answer": resolved_answer,
			"history": updated_history,
			"message": "回答已记录，现在轮到你继续提问或直接猜答案。",
		}
