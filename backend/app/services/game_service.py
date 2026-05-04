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
			"waiting_answer": False,
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
	def _build_detail_history(history: list[dict], include_hidden: bool = False) -> list[dict]:
		visible_history = []
		for item in history or []:
			if not isinstance(item, dict):
				continue
			if not include_hidden and item.get("visible_to_player") is False:
				continue
			visible_history.append(
				{
					"round_no": item.get("round_no"),
					"actor": item.get("actor"),
					"turn_type": item.get("turn_type"),
					"input_text": item.get("input_text", ""),
					"answer_text": item.get("answer_text", ""),
					"answer_label": item.get("answer_label"),
					"hint": item.get("hint"),
					"confidence": item.get("confidence", 0.0),
				}
			)
		return visible_history

	def _format_game_detail(self, game: dict, user_id: str | None = None) -> dict:
		owner_id = game.get("owner_id")
		if owner_id and owner_id != user_id:
			raise PermissionError(f"User {user_id or 'anonymous'} is not allowed to access game {game.get('game_id')}")

		metadata = dict(game.get("metadata") or {})
		status = (game.get("status") or "").lower()
		include_hidden_history = status == "finished"
		response = {
			"game_id": game.get("game_id"),
			"status": game.get("status", "active"),
			"owner_id": owner_id,
			"difficulty": game.get("difficulty"),
			"user_word": game.get("user_word"),
			"round_count": game.get("round_count", 0),
			"summary": game.get("summary", ""),
			"history": self._build_detail_history(game.get("history", []), include_hidden=include_hidden_history),
			"metadata": metadata,
			"created_at": game.get("created_at"),
			"updated_at": game.get("updated_at"),
		}

		if status == "finished":
			response.update(
				{
					"finished_at": game.get("finished_at"),
					"finish_reason": game.get("finish_reason"),
					"system_word_encrypted": game.get("system_word_encrypted"),
					"target_word_source": game.get("target_word_source"),
				}
			)
			return response

		response["progress"] = {
			"phase": metadata.get("phase", "user_turn"),
			"next_actor": metadata.get("next_actor", "user"),
			"expected_turn_type": metadata.get("expected_turn_type", "question"),
			"waiting_answer": metadata.get("waiting_answer", False),
			"awaiting_judgement": metadata.get("awaiting_judgement", False),
			"pending_question": metadata.get("pending_question", ""),
			"pending_guess": metadata.get("pending_guess", ""),
			"agent_confidence": metadata.get("agent_confidence", 0.0),
			"last_actor": metadata.get("last_actor", "system"),
			"last_intent": metadata.get("last_intent"),
		}
		return response

	async def get_game_details(self, game_id: str, user_id: str | None = None) -> dict:
		game = await self.repository.get_game(game_id)
		if not game:
			raise ValueError(f"Game with id {game_id} not found")
		return self._format_game_detail(game, user_id=user_id)

	async def get_user_game_history(self, user_id: str) -> dict:
		if not user_id or not user_id.strip():
			raise ValueError("userId is required")

		clean_user_id = user_id.strip()
		game_docs = await self.repository.list_games_by_owner(clean_user_id)
		games = []
		for game_doc in game_docs:
			game_id = game_doc.get("game_id")
			if not game_id:
				continue
			try:
				games.append(await self.get_game_details(game_id, user_id=clean_user_id))
			except ValueError:
				continue

		return {
			"user_id": clean_user_id,
			"total": len(games),
			"games": games,
		}

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

	@staticmethod
	def _is_guess_confirmation_question(question: str) -> bool:
		normalized_question = re.sub(r"\s+", "", (question or "").strip())
		if not normalized_question:
			return False

		direct_guess_patterns = [
			r"^我猜你想的词是[:：].+(?:吗|吗？|对吗|对不对)$",
			r"^我猜你(?:是|想的是|想的词是).+(?:吗|吗？|对吗|对不对)$",
			r"^(?:这个人|这位|他|她|它|这个词|这个名字|这个东西|这个角色|这个概念|这个答案)是.+(?:吗|吗？|对吗|对不对)$",
			r"^(?:是不是|是否是).+(?:吗|吗？|对吗|对不对)?$",
		]

		return any(re.match(pattern, normalized_question) for pattern in direct_guess_patterns)

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
		"""
		【重构版本】处理用户提交的回合，使用 FSM 统一管理状态转换。
		
		流程：
		1. 获取游戏数据
		2. 使用 FSM 进行状态转换和轮次锁检查
		3. 根据 FSM 返回的 handler_name 调用相应的业务处理方法
		4. 更新游戏状态和历史
		"""
		from app.core.guessGameFSM import GuessGameFSM
		
		game = await self.repository.get_game(game_id)
		if not game:
			raise ValueError(f"Game with id {game_id} not found")
		if game.get("status") == "finished":
			raise ValueError(f"Game with id {game_id} has already finished")

		metadata = game.get("metadata", {}) or {}
		phase = metadata.get("phase", "user_turn")
		history = game.get("history", [])
		round_count = len(history)

		# 创建 FSM 实例，从数据库状态初始化
		fsm = GuessGameFSM(initial_state=phase, initial_round_count=round_count)

		# 仅在需要猜词判定时再解密系统词，避免轮次锁校验被无关字段阻塞
		system_word = None
		intent_result = await self.agent.parse_user_intent(
			question,
			history,
			system_word,
			current_phase=phase,
			pending_question=metadata.get("pending_question", ""),
			pending_guess=metadata.get("pending_guess", ""),
		)
		intent = intent_result.get("intent", "invalid")

		# ===== 意图修正 =====
		if phase == GuessGameFSM.State.AWAITING_JUDGEMENT:
			if intent == GuessGameFSM.Intent.ANSWER:
				intent = GuessGameFSM.Intent.JUDGE # 在等待判断阶段，用户的回答应该被解析为 judge 意图

		if phase == GuessGameFSM.State.USER_TURN:
			if intent == GuessGameFSM.Intent.ANSWER:
				intent = GuessGameFSM.Intent.INVALID # 在用户回合阶段，用户的回答不应该被解析为 answer 意图，强制修正为 invalid

		logger.info("当前状态: %s, 用户意图: %s, FSM 轮次锁检查中...", phase, intent)
		# 构建事件并让 FSM 处理状态转换
		event = {
			"user_intent": intent,
		}
		
		# 添加额外的事件数据取决于意图类型
		if intent == GuessGameFSM.Intent.GUESS:
			system_word = system_word or self.reveal_target_word(game, self.settings)
			event["system_judge"] = "correct" if self.is_guess_correct(intent_result.get("guess_word", ""), system_word) else "incorrect"
		elif intent == GuessGameFSM.Intent.YIELD_TURN:
			# 根据系统决策设置 system_next_action
			event["system_next_action"] = intent_result.get("system_next_action", GuessGameFSM.SystemAction.ASK_QUESTION)
		elif intent == GuessGameFSM.Intent.JUDGE:
			user_input_lower = question.strip().lower()
			event["user_judge"] = "correct" if user_input_lower in ["是", "正确", "对了", "yes"] else "incorrect"

		# FSM 处理事件，返回转换结果
		fsm_result = fsm.handle_event(event)
		
		# 根据 FSM 的结果获取应该调用的处理器
		handler_name = fsm.get_handler_name(fsm_result)
		
		# 根据 handler_name 调用相应的业务处理方法（FSM 统一管理了状态转换和轮次锁）
		if handler_name == "handle_user_question":
			return await self._handle_user_question(game, question, history, mode)
		elif handler_name == "handle_user_guess":
			return await self._handle_user_guess(game, intent_result)
		elif handler_name == "handle_user_answer":
			return await self._handle_user_answer(game, question, history, intent_result)
		elif handler_name == "handle_agent_guess_judgement":
			return await self._handle_agent_guess_judgement(game, question)
		elif handler_name == "handle_invalid_input":
			if phase == GuessGameFSM.State.USER_TURN and intent_result.get("intent") == "answer":
				return self._reject_turn(game_id, phase, "现在轮到你提问或猜词，不是回答阶段", history)
			if phase == GuessGameFSM.State.AWAITING_ANSWER and intent_result.get("intent") == "question":
				return self._reject_turn(game_id, phase, "请先回答上一轮问题", history)
			return self._reject_turn(game_id, phase, "请输入有效问题或提问", history)
		elif handler_name == "handle_rejected_turn":
			return self._reject_turn(game_id, phase, fsm_result.get("message", "当前轮次不允许该操作"), history)
		elif handler_name == "handle_game_finished":
			return {"game_id": game_id, "status": "finished", "message": "游戏已结束"}
		elif handler_name == "handle_error":
			return {"game_id": game_id, "status": "error", "message": fsm_result.get("message", "系统错误")}
		else:
			# 未知处理器
			return self._reject_turn(game_id, phase, "系统内部错误", history)

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
			waiting_answer=False,
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
			waiting_answer=False,
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
				phase="waiting_answer",
				awaiting_judgement=False,
				waiting_answer=True,
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
				"phase": "waiting_answer",
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
				waiting_answer=False,
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
		pending_question = game.get("metadata", {}).get("pending_question", "")

		if resolved_answer == "yes" and self._is_guess_confirmation_question(pending_question):
			now = datetime.now()
			await self.repository.finish_game(game["game_id"], reason="agent_win_guessed_correctly", finished_at=now)
			return {
				"game_id": game["game_id"],
				"status": "finished",
				"result": "agent_win",
				"message": "系统猜测正确！游戏结束",
			}

		if resolved_answer is None:
			return {
				"game_id": game["game_id"],
				"status": game.get("status", "active"),
				"phase": game.get("metadata", {}).get("phase", "waiting_answer"),
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
			waiting_answer=False,
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
			"message": "回答已记录，现在轮到你提问或猜词。",
		}
