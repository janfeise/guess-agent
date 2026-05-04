# Guess Game FSM：有限状态机【修复版本】
# 修复日期：2026-05-03
# 修复内容：
# 1. 清晰化事件参数（移除 system_action 混淆）
# 2. 添加 YIELD_TURN 完整处理
# 3. 简化 GUESS 逻辑
# 4. 统一返回格式
# 5. 内部轮次管理
# 6. 完整事件验证
# 7. 改进错误处理

class GuessGameFSM:
    # 定义状态
    class State:
        START = 'start'  # 游戏开始
        USER_TURN = 'user_turn'  # 用户回合
        WAITING_ANSWER = 'waiting_answer'  # 等待用户回答
        AWAITING_JUDGEMENT = 'awaiting_judgement'  # 等待用户判断猜词是否正确
        FINISHED = 'finished'  # 游戏结束
        ERROR = 'error'  # 错误状态

    # 定义用户意图
    class Intent:
        QUESTION = 'question'  # 用户提问
        GUESS = 'guess'  # 用户猜词
        ANSWER = 'answer'  # 用户回答系统提问
        JUDGE = 'judge'  # 用户对系统的猜测进行判定
        YIELD_TURN = 'yield_turn'  # 用户放弃回合，让系统继续提问/猜测
        INVALID = 'invalid'  # 无效事件

    # 定义系统动作
    class SystemAction:
        ASK_QUESTION = 'ask_question'  # 系统提问
        MAKE_GUESS = 'make_guess'  # 系统猜词

    def __init__(self, initial_state: str = None, initial_round_count: int = 0):
        """
        初始化状态机。
        
        Args:
            initial_state: 初始状态字符串（如 'user_turn'），用于从数据库恢复状态
            initial_round_count: 初始轮次计数
        """
        self._state = initial_state or self.State.START  # 初始状态为游戏开始（私有属性）
        self._round_count = initial_round_count  # 游戏轮次计数（私有属性）
        self._max_rounds = 20  # 游戏最大轮次限制（私有属性）

    # ========== 属性访问控制（只读 Property） ==========
    
    @property
    def state(self):
        """
        获取当前游戏状态（只读）。
        
        Returns:
            str: 当前状态值
        """
        return self._state
    
    @property
    def round_count(self):
        """
        获取当前轮次计数（只读）。
        
        Returns:
            int: 当前轮次数
        """
        return self._round_count
    
    @property
    def max_rounds(self):
        """
        获取最大轮次限制（只读）。
        
        Returns:
            int: 最大轮次限制
        """
        return self._max_rounds


    # ========== 验证与检查 ==========
    
    def _validate_event(self, event):
        """
        验证事件的完整性和合法性。
        
        Args:
            event: 事件字典
            
        Raises:
            ValueError: 如果事件不合法
        """
        if not event or not isinstance(event, dict):
            raise ValueError("Event must be a non-empty dictionary")
        
        if "user_intent" not in event:
            raise ValueError("Event must contain 'user_intent' field")
        
        if event["user_intent"] not in [
            self.Intent.QUESTION,
            self.Intent.GUESS,
            self.Intent.ANSWER,
            self.Intent.JUDGE,
            self.Intent.YIELD_TURN,
            self.Intent.INVALID
        ]:
            raise ValueError(f"Unknown user_intent: {event.get('user_intent')}")
    
    def _check_round_limit(self):
        """检查是否超过轮次限制。"""
        if self._round_count >= self._max_rounds:
            return True
        return False
    
    # ========== 状态转换逻辑 ==========
    def __next_state(self, event):
        """
        【修复版本】计算下一个状态，仅基于用户意图和判定结果。
        
        关键改进：
        1. 移除 system_action 检查，仅基于 user_intent
        2. 完整处理 YIELD_TURN
        3. 简化 GUESS 处理逻辑
        4. 处理 INVALID 意图
        5. 轮次限制检查
        
        Args:
            event: 事件字典
        """
        # 检查轮次限制（任何状态都应该检查）
        if self._check_round_limit():
            return self.State.FINISHED
        
        # ===== START 状态 =====
        if self._state == self.State.START:
            return self.State.USER_TURN
        
        # ===== USER_TURN 状态 =====
        if self._state == self.State.USER_TURN:
            user_intent = event.get("user_intent")
            
            # 用户提问或让行 → 等待用户回答
            if user_intent == self.Intent.QUESTION or user_intent == self.Intent.YIELD_TURN:
                # 当系统决策为提问时，进入等待回答状态
                if event.get("system_next_action") == self.SystemAction.MAKE_GUESS:
                    return self.State.AWAITING_JUDGEMENT
                else:
                    # 默认：进入等待回答状态
                    return self.State.WAITING_ANSWER
            
            # 用户猜词
            elif user_intent == self.Intent.GUESS:
                system_judge = event.get("system_judge")
                if system_judge == "correct":
                    return self.State.FINISHED
                else:
                    return self.State.USER_TURN
            
            # 无效意图 → 保持当前状态
            elif user_intent == self.Intent.INVALID:
                return self.State.USER_TURN
            
            # 其他意图在 USER_TURN 不合法
            else:
                return self.State.USER_TURN
        
        # ===== WAITING_ANSWER 状态 =====
        if self._state == self.State.WAITING_ANSWER:
            user_intent = event.get("user_intent")
            
            # 用户回答系统提问 → 回到用户回合
            if user_intent == self.Intent.ANSWER:
                return self.State.USER_TURN
            
            # 用户没有回答（其他意图）→ 轮次锁，保持等待状态
            else:
                return self.State.WAITING_ANSWER
        
        # ===== AWAITING_JUDGEMENT 状态 =====
        if self._state == self.State.AWAITING_JUDGEMENT:
            user_intent = event.get("user_intent")
            user_judge = event.get("user_judge")
            
            # 用户判定系统猜测
            if user_intent == self.Intent.JUDGE:
                if user_judge == "correct":
                    return self.State.FINISHED
                else:
                    return self.State.USER_TURN
            
            # 用户没有判定（其他意图）→ 轮次锁，保持等待状态
            else:
                return self.State.AWAITING_JUDGEMENT
        
        # ===== FINISHED 状态 =====
        if self._state == self.State.FINISHED:
            return self.State.FINISHED
        
        # ===== ERROR 状态 =====
        if self._state == self.State.ERROR:
            if event.get("recovery_action") == "resume":
                return self.State.USER_TURN
            elif event.get("recovery_action") == "abort":
                return self.State.FINISHED
            else:
                return self.State.ERROR
        
        # 未知状态 → 返回 ERROR
        return self.State.ERROR
            
    
    # ========== 系统动作逻辑 ==========
    
    def __action(self, event):
        """
        【修复版本】根据状态和事件生成系统动作。统一返回格式。
        
        Returns:
            dict: 统一格式 {"system_action": "action", "message": "msg"}
        """
        # ===== START 状态 =====
        if self._state == self.State.START:
            return {
                "system_action": "init",
                "message": "游戏开始！请提问或猜词。"
            }
        
        # ===== USER_TURN 状态 =====
        if self._state == self.State.USER_TURN:
            user_intent = event.get("user_intent")
            
            if user_intent == self.Intent.QUESTION:
                return {
                    "system_action": "answer",
                    "message": "系统回答用户的提问。"
                }
            
            elif user_intent == self.Intent.GUESS:
                system_judge = event.get("system_judge")
                if system_judge == "correct":
                    return {
                        "system_action": "finish",
                        "message": "用户猜测正确，游戏结束！"
                    }
                else:
                    return {
                        "system_action": "continue",
                        "message": "猜测错误，继续游戏。"
                    }
            
            elif user_intent == self.Intent.YIELD_TURN:
                system_next_action = event.get("system_next_action")
                if system_next_action == self.SystemAction.MAKE_GUESS:
                    return {
                        "system_action": "make_guess",
                        "message": "系统进行猜测。"
                    }
                else:
                    return {
                        "system_action": "ask_question",
                        "message": "系统提问。"
                    }
            
            elif user_intent == self.Intent.INVALID:
                return {
                    "system_action": "chat",
                    "message": "系统进行闲聊回复。"
                }
            
            else:
                return {
                    "system_action": "reject",
                    "message": "当前阶段不支持该操作。"
                }
        
        # ===== WAITING_ANSWER 状态 =====
        if self._state == self.State.WAITING_ANSWER:
            user_intent = event.get("user_intent")
            
            if user_intent == self.Intent.ANSWER:
                return {
                    "system_action": "record_answer",
                    "message": "记录用户回答。"
                }
            
            else:
                return {
                    "system_action": "prompt_answer",
                    "message": "请先回答上一轮问题"
                }
        
        # ===== AWAITING_JUDGEMENT 状态 =====
        if self._state == self.State.AWAITING_JUDGEMENT:
            user_intent = event.get("user_intent")
            
            if user_intent == self.Intent.JUDGE:
                user_judge = event.get("user_judge")
                if user_judge == "correct":
                    return {
                        "system_action": "finish",
                        "message": "系统猜测正确，游戏结束！"
                    }
                else:
                    return {
                        "system_action": "continue",
                        "message": "系统猜测错误，继续游戏。"
                    }
            
            else:
                return {
                    "system_action": "prompt_judge",
                    "message": "请先判定系统的猜测是否正确。"
                }
        
        # ===== FINISHED 状态 =====
        if self._state == self.State.FINISHED:
            return {
                "system_action": "finish",
                "message": "游戏已结束。"
            }
        
        # ===== ERROR 状态 =====
        if self._state == self.State.ERROR:
            return {
                "system_action": "error",
                "message": "系统发生错误，请重试。"
            }
        
        # 默认
        return {
            "system_action": "error",
            "message": "未知状态。"
        }
    
    # ========== 统一接口 ==========
    
    def __result(self, current_state, next_state, action):
        """
        【修复版本】统一封装返回结果。
        
        Returns:
            dict: 包含状态转换和动作信息的结果字典
        """
        return {
            "user_current_state": current_state,
            "user_next_state": next_state,
            "system_action": action.get("system_action"),
            "message": action.get("message"),
            "is_game_finished": next_state == self.State.FINISHED,
            "is_error": next_state == self.State.ERROR,
        }
    
    def handle_event(self, event):
        """
        【修复版本】处理事件，执行状态转换和动作。
        
        Args:
            event (dict): 事件字典，包含 user_intent 等字段
            
        Returns:
            dict: 状态转换结果
        """
        # 1. 验证事件
        try:
            self._validate_event(event)
        except ValueError as e:
            return {
                "user_current_state": self._state,
                "user_next_state": self.State.ERROR,
                "system_action": "error",
                "message": f"事件验证失败: {str(e)}",
                "is_game_finished": False,
                "is_error": True,
            }
        
        # 2. 记录当前状态
        current_state = self._state
        
        # 3. 计算下一状态
        try:
            next_state = self.__next_state(event)
        except Exception as e:
            next_state = self.State.ERROR
        
        # 4. 生成系统动作
        try:
            action = self.__action(event)
        except Exception as e:
            action = {"system_action": "error", "message": f"动作生成失败: {str(e)}"}
        
        # 5. 更新状态和轮次
        self._state = next_state
        # 在用户回合结束时增加轮次计数
        if self._should_increment_round(current_state, next_state, intent_INVALID=event.get("user_intent") == self.Intent.INVALID):
            self._round_count += 1
        
        # 6. 返回结果
        return self.__result(current_state, next_state, action)
    
    # ========== 辅助方法 ==========
    
    def reset(self):
        """重置状态机（开始新游戏）。"""
        self._state = self.State.START
        self._round_count = 0
    
    def get_state(self):
        """获取当前状态（通过方法）。"""
        return self._state
    
    def get_round_count(self):
        """获取当前轮次（通过方法）。"""
        return self._round_count
    
    def get_remaining_rounds(self):
        """获取剩余轮次。"""
        return max(0, self._max_rounds - self._round_count)
    
    def is_finished(self):
        """检查游戏是否结束。"""
        return self._state == self.State.FINISHED
    
    def is_error(self):
        """检查状态机是否处于错误状态。"""
        return self._state == self.State.ERROR

    def get_handler_name(self, result: dict) -> str:
        """
        根据状态转换结果，返回应该调用的处理器名称。
        
        这个方法帮助 game_service 知道应该调用哪个业务处理方法。
        
        Args:
            result: handle_event 返回的结果字典
            
        Returns:
            str: 处理器名称（如 'handle_user_question', 'handle_user_guess' 等）
        """
        current_state = result.get("user_current_state")
        next_state = result.get("user_next_state")
        system_action = result.get("system_action")
        
        # 如果有错误，返回错误处理器
        if next_state == self.State.ERROR:
            return "handle_error"
        
        # 根据当前状态和系统动作推断处理器（按优先级顺序检查）
        
        # 当前状态为 USER_TURN，系统动作为 finish -> 用户正确猜词
        if current_state == self.State.USER_TURN and system_action == "finish":
            return "handle_user_guess"
        
        # 当前状态为 USER_TURN，系统动作为 continue -> 用户猜词错误
        if current_state == self.State.USER_TURN and system_action == "continue":
            return "handle_user_guess"
        
        # 当前状态为 AWAITING_JUDGEMENT，系统动作为 finish -> 系统猜词正确
        if current_state == self.State.AWAITING_JUDGEMENT and system_action == "finish":
            return "handle_agent_guess_judgement"
        
        # 当前状态为 AWAITING_JUDGEMENT，系统动作为 continue -> 系统猜词错误
        if current_state == self.State.AWAITING_JUDGEMENT and system_action == "continue":
            return "handle_agent_guess_judgement"
        
        # 当前状态为 USER_TURN，系统动作为 answer -> 处理用户提问
        if current_state == self.State.USER_TURN and system_action == "answer":
            return "handle_user_question"
        
        # 当前状态为 USER_TURN，系统动作为 make_guess -> 系统要开始猜词
        if current_state == self.State.USER_TURN and system_action == "make_guess":
            return "handle_user_question"
        
        # 当前状态为 USER_TURN，系统动作为 ask_question -> 系统继续提问
        if current_state == self.State.USER_TURN and system_action == "ask_question":
            return "handle_user_question"
        
        # 当前状态为 USER_TURN，系统动作为 chat -> 无效意图
        if current_state == self.State.USER_TURN and system_action == "chat":
            return "handle_invalid_input"
        
        # 当前状态为 USER_TURN，系统动作为 reject/prompt -> 轮次锁拒绝
        if current_state == self.State.USER_TURN and system_action in ("reject", "prompt_answer", "prompt_judge"):
            return "handle_rejected_turn"
        
        # 当前状态为 WAITING_ANSWER，系统动作为 record_answer -> 处理用户回答
        if current_state == self.State.WAITING_ANSWER and system_action == "record_answer":
            return "handle_user_answer"
        
        # 当前状态为 WAITING_ANSWER，系统动作为 prompt -> 轮次锁拒绝
        if current_state == self.State.WAITING_ANSWER and system_action == "prompt_answer":
            return "handle_rejected_turn"
        
        # 当前状态为 AWAITING_JUDGEMENT，系统动作为 prompt -> 轮次锁拒绝
        if current_state == self.State.AWAITING_JUDGEMENT and system_action == "prompt_judge":
            return "handle_rejected_turn"
        
        # START 状态
        if current_state == self.State.START and system_action == "init":
            return "handle_game_initialized"
        
        # 如果游戏结束（但不是因为当前操作），需要特殊处理
        if next_state == self.State.FINISHED and system_action not in ("finish", "continue"):
            return "handle_game_finished"
        
        return "handle_unknown"

    def _should_increment_round(self, state, next_state, intent_INVALID=False):
        """判断轮次计数是否应该增加。"""
        if intent_INVALID:
            return False # 无效事件不增加轮次
        if state == self.State.USER_TURN:
            return next_state in [self.State.WAITING_ANSWER, self.State.AWAITING_JUDGEMENT, self.State.FINISHED, self.State.USER_TURN]

        if state == self.State.WAITING_ANSWER:
            return next_state == self.State.USER_TURN

        if state == self.State.AWAITING_JUDGEMENT:
            return next_state == self.State.USER_TURN

        return False