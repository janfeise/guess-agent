# -*- coding: utf-8 -*-
"""
状态机单元测试

测试修复后的 GuessGameFSM 的所有功能：
- 状态转换正确性
- 意图处理完整性
- 轮次管理准确性
- 边界条件处理
- 异常处理能力

运行方式：
    python -m pytest tests/test_fsm.py -v
    或
    python -m unittest tests.test_fsm -v
    或
    python tests/test_fsm.py
"""

import unittest
import sys
import os
import io

# 设置 UTF-8 编码以支持中文和 Unicode 符号（包括输出重定向）
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到 Python 路径，使脚本能正确导入 backend 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.guessGameFSM import GuessGameFSM


class TestStateTransitions(unittest.TestCase):
    """测试状态转换"""
    
    def setUp(self):
        """每个测试用例前运行"""
        self.fsm = GuessGameFSM()
    
    def test_TC_1_1_START_initialization(self):
        """TC-1.1: 验证游戏初始化"""
        self.assertEqual(self.fsm.state, GuessGameFSM.State.START)
        self.assertEqual(self.fsm.round_count, 0)
        self.assertEqual(self.fsm.max_rounds, 20)
    
    def test_TC_1_2_START_to_USER_TURN(self):
        """TC-1.2: START → USER_TURN 转换（通过 handle_event）"""
        event = {"user_intent": GuessGameFSM.Intent.QUESTION}
        result = self.fsm.handle_event(event)
        
        # 验证状态转换
        self.assertEqual(result["user_current_state"], GuessGameFSM.State.START)
        # 注：START 在处理任何意图前先转到 USER_TURN
        # 但实际上 __next_state 中 START 总是返回 USER_TURN
        # 然后 USER_TURN 再根据意图转换
        
    def test_TC_1_3_USER_TURN_QUESTION_to_WAITING_ANSWER(self):
        """TC-1.3: USER_TURN + QUESTION → WAITING_ANSWER"""
        # 先从 START 转到 USER_TURN
        self.fsm._state = GuessGameFSM.State.USER_TURN
        
        event = {"user_intent": GuessGameFSM.Intent.QUESTION}
        result = self.fsm.handle_event(event)
        
        self.assertEqual(result["user_current_state"], GuessGameFSM.State.USER_TURN)
        self.assertEqual(result["user_next_state"], GuessGameFSM.State.WAITING_ANSWER)
        self.assertEqual(result["system_action"], "answer")
        self.assertEqual(self.fsm.round_count, 1)
        self.assertFalse(result["is_game_finished"])
    
    def test_TC_1_4_USER_TURN_GUESS_correct(self):
        """TC-1.4: USER_TURN + GUESS(correct) → FINISHED"""
        self.fsm._state = GuessGameFSM.State.USER_TURN
        
        event = {
            "user_intent": GuessGameFSM.Intent.GUESS,
            "system_judge": "correct"
        }
        result = self.fsm.handle_event(event)
        
        self.assertEqual(result["user_next_state"], GuessGameFSM.State.FINISHED)
        self.assertEqual(result["system_action"], "finish")
        self.assertTrue(result["is_game_finished"])
        self.assertEqual(self.fsm.round_count, 1)
    
    def test_TC_1_5_USER_TURN_GUESS_incorrect(self):
        """TC-1.5: USER_TURN + GUESS(incorrect) → USER_TURN"""
        self.fsm._state = GuessGameFSM.State.USER_TURN
        
        event = {
            "user_intent": GuessGameFSM.Intent.GUESS,
            "system_judge": "incorrect"
        }
        result = self.fsm.handle_event(event)
        
        self.assertEqual(result["user_next_state"], GuessGameFSM.State.USER_TURN)
        self.assertEqual(result["system_action"], "continue")
        self.assertEqual(self.fsm.round_count, 1)
    
    def test_TC_1_6_USER_TURN_YIELD_TURN_ask(self):
        """TC-1.6: USER_TURN + YIELD_TURN(ask) → WAITING_ANSWER"""
        self.fsm._state = GuessGameFSM.State.USER_TURN
        
        event = {
            "user_intent": GuessGameFSM.Intent.YIELD_TURN,
            "system_next_action": GuessGameFSM.SystemAction.ASK_QUESTION
        }
        result = self.fsm.handle_event(event)
        
        self.assertEqual(result["user_next_state"], GuessGameFSM.State.WAITING_ANSWER)
        self.assertEqual(result["system_action"], "ask_question")
        self.assertEqual(self.fsm.round_count, 1)
    
    def test_TC_1_7_USER_TURN_YIELD_TURN_guess(self):
        """TC-1.7: USER_TURN + YIELD_TURN(guess) → AWAITING_JUDGEMENT"""
        self.fsm._state = GuessGameFSM.State.USER_TURN
        
        event = {
            "user_intent": GuessGameFSM.Intent.YIELD_TURN,
            "system_next_action": GuessGameFSM.SystemAction.MAKE_GUESS
        }
        result = self.fsm.handle_event(event)
        
        self.assertEqual(result["user_next_state"], GuessGameFSM.State.AWAITING_JUDGEMENT)
        self.assertEqual(result["system_action"], "make_guess")
        self.assertEqual(self.fsm.round_count, 1)
    
    def test_TC_1_8_WAITING_ANSWER_ANSWER_to_USER_TURN(self):
        """TC-1.8: WAITING_ANSWER + ANSWER → USER_TURN"""
        self.fsm._state = GuessGameFSM.State.WAITING_ANSWER
        
        event = {"user_intent": GuessGameFSM.Intent.ANSWER}
        result = self.fsm.handle_event(event)
        
        self.assertEqual(result["user_next_state"], GuessGameFSM.State.USER_TURN)
        self.assertEqual(result["system_action"], "record_answer")
        self.assertEqual(self.fsm.round_count, 1)
    
    def test_TC_1_9_AWAITING_JUDGEMENT_JUDGE_correct(self):
        """TC-1.9: AWAITING_JUDGEMENT + JUDGE(correct) → FINISHED"""
        self.fsm._state = GuessGameFSM.State.AWAITING_JUDGEMENT
        
        event = {
            "user_intent": GuessGameFSM.Intent.JUDGE,
            "user_judge": "correct"
        }
        result = self.fsm.handle_event(event)
        
        self.assertEqual(result["user_next_state"], GuessGameFSM.State.FINISHED)
        self.assertEqual(result["system_action"], "finish")
        self.assertTrue(result["is_game_finished"])
    
    def test_TC_1_10_AWAITING_JUDGEMENT_JUDGE_incorrect(self):
        """TC-1.10: AWAITING_JUDGEMENT + JUDGE(incorrect) → USER_TURN"""
        self.fsm._state = GuessGameFSM.State.AWAITING_JUDGEMENT
        
        event = {
            "user_intent": GuessGameFSM.Intent.JUDGE,
            "user_judge": "incorrect"
        }
        result = self.fsm.handle_event(event)
        
        self.assertEqual(result["user_next_state"], GuessGameFSM.State.USER_TURN)
        self.assertEqual(result["system_action"], "continue")


class TestTurnLock(unittest.TestCase):
    """测试轮次锁（Turn Lock）"""
    
    def setUp(self):
        self.fsm = GuessGameFSM()
    
    def test_TC_2_1_WAITING_ANSWER_turn_lock(self):
        """TC-2.1: WAITING_ANSWER 中的轮次锁"""
        self.fsm._state = GuessGameFSM.State.WAITING_ANSWER
        
        # 发送非法意图（应该是 ANSWER）
        event1 = {"user_intent": GuessGameFSM.Intent.QUESTION}
        result1 = self.fsm.handle_event(event1)
        
        # 状态应该保持 WAITING_ANSWER（轮次锁）
        self.assertEqual(result1["user_next_state"], GuessGameFSM.State.WAITING_ANSWER)
        self.assertEqual(result1["system_action"], "prompt_answer")
        
        # 再次尝试非法意图
        event2 = {"user_intent": GuessGameFSM.Intent.GUESS, "system_judge": "correct"}
        result2 = self.fsm.handle_event(event2)
        
        # 仍然保持 WAITING_ANSWER
        self.assertEqual(result2["user_next_state"], GuessGameFSM.State.WAITING_ANSWER)
        
        # 最后发送合法意图
        event3 = {"user_intent": GuessGameFSM.Intent.ANSWER}
        result3 = self.fsm.handle_event(event3)
        
        # 现在应该转移到 USER_TURN
        self.assertEqual(result3["user_next_state"], GuessGameFSM.State.USER_TURN)
    
    def test_TC_2_2_AWAITING_JUDGEMENT_turn_lock(self):
        """TC-2.2: AWAITING_JUDGEMENT 中的轮次锁"""
        self.fsm._state = GuessGameFSM.State.AWAITING_JUDGEMENT
        
        # 发送非法意图（应该是 JUDGE）
        event1 = {"user_intent": GuessGameFSM.Intent.ANSWER}
        result1 = self.fsm.handle_event(event1)
        
        # 状态应该保持 AWAITING_JUDGEMENT
        self.assertEqual(result1["user_next_state"], GuessGameFSM.State.AWAITING_JUDGEMENT)
        self.assertEqual(result1["system_action"], "prompt_judge")
        
        # 最后发送合法意图
        event2 = {
            "user_intent": GuessGameFSM.Intent.JUDGE,
            "user_judge": "incorrect"
        }
        result2 = self.fsm.handle_event(event2)
        
        # 现在应该转移到 USER_TURN
        self.assertEqual(result2["user_next_state"], GuessGameFSM.State.USER_TURN)


class TestRoundManagement(unittest.TestCase):
    """测试轮次管理"""
    
    def setUp(self):
        self.fsm = GuessGameFSM()
    
    def test_TC_3_1_round_count_increment(self):
        """TC-3.1: 轮次计数正确性"""
        self.assertEqual(self.fsm.round_count, 0)
        
        # 第 1 轮：USER_TURN → WAITING_ANSWER
        self.fsm._state = GuessGameFSM.State.USER_TURN
        event1 = {"user_intent": GuessGameFSM.Intent.QUESTION}
        self.fsm.handle_event(event1)
        self.assertEqual(self.fsm.round_count, 1)
        
        # 第 2 轮：WAITING_ANSWER → USER_TURN
        event2 = {"user_intent": GuessGameFSM.Intent.ANSWER}
        self.fsm.handle_event(event2)
        self.assertEqual(self.fsm.round_count, 2)
        
        # 第 3 轮：USER_TURN → USER_TURN（猜错）
        event3 = {
            "user_intent": GuessGameFSM.Intent.GUESS,
            "system_judge": "incorrect"
        }
        self.fsm.handle_event(event3)
        self.assertEqual(self.fsm.round_count, 3)
        
        # 第 4 轮：USER_TURN → FINISHED（猜对）
        event4 = {
            "user_intent": GuessGameFSM.Intent.GUESS,
            "system_judge": "correct"
        }
        self.fsm.handle_event(event4)
        self.assertEqual(self.fsm.round_count, 4)
    
    def test_TC_3_2_round_limit_max_rounds(self):
        """TC-3.2: 轮次限制（20 轮上限）"""
        # 设置轮次为 19（即将达到上限）
        self.fsm._round_count = 19
        self.fsm._state = GuessGameFSM.State.USER_TURN
        
        # 发送意图，会导致离开 USER_TURN，轮次变为 20
        event = {
            "user_intent": GuessGameFSM.Intent.GUESS,
            "system_judge": "incorrect"
        }
        result = self.fsm.handle_event(event)
        
        # 轮次更新到 20
        self.assertEqual(self.fsm.round_count, 20)
        
        # 下一次转换时，由于 >= max_rounds，应该返回 FINISHED
        result2 = self.fsm.handle_event(event)
        self.assertEqual(result2["user_next_state"], GuessGameFSM.State.FINISHED)
    
    def test_TC_3_3_remaining_rounds(self):
        """TC-3.3: 剩余轮次查询"""
        # 初始状态
        self.assertEqual(self.fsm.get_remaining_rounds(), 20)
        
        # 进行 5 轮后
        self.fsm._round_count = 5
        self.assertEqual(self.fsm.get_remaining_rounds(), 15)
        
        # 进行到第 20 轮
        self.fsm._round_count = 20
        self.assertEqual(self.fsm.get_remaining_rounds(), 0)
        
        # 超过 20 轮（不应该发生，但要检查边界）
        self.fsm._round_count = 25
        self.assertEqual(self.fsm.get_remaining_rounds(), 0)
    
    def test_TC_3_4_custom_max_rounds(self):
        """TC-3.4: 自定义最大轮次"""
        # 修改最大轮次
        self.fsm._max_rounds = 10
        
        # 设置轮次为 9
        self.fsm._round_count = 9
        self.assertEqual(self.fsm.get_remaining_rounds(), 1)
        
        # 当 round_count >= 10 时应该结束
        self.fsm._round_count = 10
        self.fsm._state = GuessGameFSM.State.USER_TURN
        event = {"user_intent": GuessGameFSM.Intent.QUESTION}
        result = self.fsm.handle_event(event)
        
        # 由于已经达到上限，应该返回 FINISHED
        self.assertEqual(result["user_next_state"], GuessGameFSM.State.FINISHED)


class TestIntentHandling(unittest.TestCase):
    """测试意图处理"""
    
    def setUp(self):
        self.fsm = GuessGameFSM()
    
    def test_TC_4_1_INVALID_intent_USER_TURN(self):
        """TC-4.1: INVALID 意图处理（USER_TURN）"""
        self.fsm._state = GuessGameFSM.State.USER_TURN
        
        event = {"user_intent": GuessGameFSM.Intent.INVALID}
        result = self.fsm.handle_event(event)
        
        # 应该保持在 USER_TURN，但不增加轮次
        self.assertEqual(result["user_next_state"], GuessGameFSM.State.USER_TURN)
        self.assertEqual(result["system_action"], "chat")
        self.assertEqual(self.fsm.round_count, 0)  # 不应该增加轮次
    
    def test_TC_4_2_INVALID_intent_in_various_states(self):
        """TC-4.2: INVALID 意图在各个状态下的处理"""
        # WAITING_ANSWER + INVALID → WAITING_ANSWER（轮次锁）
        self.fsm._state = GuessGameFSM.State.WAITING_ANSWER
        event = {"user_intent": GuessGameFSM.Intent.INVALID}
        result = self.fsm.handle_event(event)
        self.assertEqual(result["user_next_state"], GuessGameFSM.State.WAITING_ANSWER)
        
        # AWAITING_JUDGEMENT + INVALID → AWAITING_JUDGEMENT（轮次锁）
        self.fsm._state = GuessGameFSM.State.AWAITING_JUDGEMENT
        result = self.fsm.handle_event(event)
        self.assertEqual(result["user_next_state"], GuessGameFSM.State.AWAITING_JUDGEMENT)
    
    def test_TC_4_3_QUESTION_with_system_next_action(self):
        """TC-4.3: QUESTION 意图带 system_next_action"""
        self.fsm._state = GuessGameFSM.State.USER_TURN
        
        # QUESTION 默认进入 WAITING_ANSWER
        event1 = {"user_intent": GuessGameFSM.Intent.QUESTION}
        result1 = self.fsm.handle_event(event1)
        self.assertEqual(result1["user_next_state"], GuessGameFSM.State.WAITING_ANSWER)
        
        # QUESTION + system_next_action=make_guess 进入 AWAITING_JUDGEMENT
        self.fsm._state = GuessGameFSM.State.USER_TURN
        event2 = {
            "user_intent": GuessGameFSM.Intent.QUESTION,
            "system_next_action": GuessGameFSM.SystemAction.MAKE_GUESS
        }
        result2 = self.fsm.handle_event(event2)
        self.assertEqual(result2["user_next_state"], GuessGameFSM.State.AWAITING_JUDGEMENT)


class TestExceptionHandling(unittest.TestCase):
    """测试异常处理"""
    
    def setUp(self):
        self.fsm = GuessGameFSM()
    
    def test_TC_5_1_None_event(self):
        """TC-5.1: None 事件"""
        result = self.fsm.handle_event(None)
        
        self.assertEqual(result["user_next_state"], GuessGameFSM.State.ERROR)
        self.assertTrue(result["is_error"])
        self.assertIn("验证失败", result["message"])
    
    def test_TC_5_2_empty_dict_event(self):
        """TC-5.2: 空字典事件"""
        result = self.fsm.handle_event({})
        print("返回结果:", result)
        
        self.assertEqual(result["user_next_state"], GuessGameFSM.State.ERROR)
        self.assertTrue(result["is_error"])
        # 检查是否包含验证相关的关键词（具体消息内容可能因实现而异）
        self.assertTrue("验证" in result["message"] or "Event" in result["message"] or "empty" in result["message"])
    
    def test_TC_5_3_missing_user_intent(self):
        """TC-5.3: 缺少 user_intent 字段"""
        result = self.fsm.handle_event({"system_judge": "correct"})
        
        self.assertEqual(result["user_next_state"], GuessGameFSM.State.ERROR)
        self.assertTrue(result["is_error"])
    
    def test_TC_5_4_unknown_user_intent(self):
        """TC-5.4: 未知 user_intent 值"""
        result = self.fsm.handle_event({"user_intent": "unknown_intent"})
        
        self.assertEqual(result["user_next_state"], GuessGameFSM.State.ERROR)
        self.assertTrue(result["is_error"])
        self.assertIn("Unknown", result["message"])
    
    def test_TC_5_5_non_dict_event(self):
        """TC-5.5: 非字典事件"""
        # 字符串
        result1 = self.fsm.handle_event("not a dict")
        self.assertTrue(result1["is_error"])
        
        # 列表
        result2 = self.fsm.handle_event([])
        self.assertTrue(result2["is_error"])
        
        # 数字
        result3 = self.fsm.handle_event(123)
        self.assertTrue(result3["is_error"])
    
    def test_TC_5_6_result_format_consistency(self):
        """TC-5.6: 异常时的返回格式也应该一致"""
        result = self.fsm.handle_event(None)
        
        # 应该包含所有必需字段
        self.assertIn("user_current_state", result)
        self.assertIn("user_next_state", result)
        self.assertIn("system_action", result)
        self.assertIn("message", result)
        self.assertIn("is_game_finished", result)
        self.assertIn("is_error", result)


class TestCompleteGameFlow(unittest.TestCase):
    """测试完整游戏流程"""
    
    def setUp(self):
        self.fsm = GuessGameFSM()
    
    def test_TC_6_1_complete_game_user_wins(self):
        """TC-6.1: 完整游戏流程（用户胜）"""
        # 初始化：START 状态会在第一次事件时转到 USER_TURN
        self.assertEqual(self.fsm.state, GuessGameFSM.State.START)
        
        # 第 1 轮：START 自动转到 USER_TURN（初始化）
        # 注：START → USER_TURN 的转换不增加轮次
        print("状态机：", self.fsm.state)
        event1 = {"user_intent": GuessGameFSM.Intent.QUESTION}
        result1 = self.fsm.handle_event(event1)
        # START 优先转到 USER_TURN，在同一事件中完成该转换
        self.assertEqual(result1["user_next_state"], GuessGameFSM.State.USER_TURN)
        self.assertEqual(self.fsm.state, GuessGameFSM.State.USER_TURN)
        # START 转换不增加轮次，轮次仍为 0
        self.assertEqual(self.fsm.round_count, 0)
        
        # 第 2 轮：USER_TURN + QUESTION → WAITING_ANSWER（轮次增加到 1）
        event1b = {"user_intent": GuessGameFSM.Intent.QUESTION}
        result1b = self.fsm.handle_event(event1b)
        self.assertEqual(result1b["user_next_state"], GuessGameFSM.State.WAITING_ANSWER)
        self.assertEqual(self.fsm.round_count, 1)
        
        # 第 3 轮：WAITING_ANSWER + ANSWER → USER_TURN（轮次增加到 2）
        event2 = {"user_intent": GuessGameFSM.Intent.ANSWER}
        result2 = self.fsm.handle_event(event2)
        self.assertEqual(result2["user_next_state"], GuessGameFSM.State.USER_TURN)
        self.assertEqual(self.fsm.round_count, 2)
        
        # 第 4 轮：USER_TURN + GUESS(correct) → FINISHED（轮次增加到 3）
        event3 = {
            "user_intent": GuessGameFSM.Intent.GUESS,
            "system_judge": "correct"
        }
        result3 = self.fsm.handle_event(event3)
        self.assertEqual(result3["user_next_state"], GuessGameFSM.State.FINISHED)
        self.assertTrue(result3["is_game_finished"])
        self.assertEqual(self.fsm.round_count, 3)
    
    def test_TC_6_2_complete_game_system_wins(self):
        """TC-6.2: 完整游戏流程（系统胜）"""
        self.fsm._state = GuessGameFSM.State.USER_TURN
        
        # USER_TURN + YIELD_TURN(guess) → AWAITING_JUDGEMENT
        event1 = {
            "user_intent": GuessGameFSM.Intent.YIELD_TURN,
            "system_next_action": GuessGameFSM.SystemAction.MAKE_GUESS
        }
        result1 = self.fsm.handle_event(event1)
        self.assertEqual(result1["user_next_state"], GuessGameFSM.State.AWAITING_JUDGEMENT)
        self.assertEqual(self.fsm.round_count, 1)
        
        # AWAITING_JUDGEMENT + JUDGE(correct) → FINISHED
        event2 = {
            "user_intent": GuessGameFSM.Intent.JUDGE,
            "user_judge": "correct"
        }
        result2 = self.fsm.handle_event(event2)
        self.assertEqual(result2["user_next_state"], GuessGameFSM.State.FINISHED)
        self.assertTrue(result2["is_game_finished"])
        self.assertEqual(self.fsm.round_count, 1)
    
    def test_TC_6_3_game_reset(self):
        """TC-6.3: 游戏重置"""
        # 进行几轮游戏
        self.fsm._state = GuessGameFSM.State.USER_TURN
        event = {"user_intent": GuessGameFSM.Intent.QUESTION}
        self.fsm.handle_event(event)
        self.assertEqual(self.fsm.round_count, 1)
        self.assertEqual(self.fsm.state, GuessGameFSM.State.WAITING_ANSWER)
        
        # 重置
        self.fsm.reset()
        
        # 验证重置结果
        self.assertEqual(self.fsm.state, GuessGameFSM.State.START)
        self.assertEqual(self.fsm.round_count, 0)


class TestReturnValueConsistency(unittest.TestCase):
    """测试返回值一致性"""
    
    def setUp(self):
        self.fsm = GuessGameFSM()
    
    def test_TC_7_1_return_value_format(self):
        """TC-7.1: 返回值格式统一"""
        # 正常流程
        self.fsm._state = GuessGameFSM.State.USER_TURN
        event = {"user_intent": GuessGameFSM.Intent.QUESTION}
        result = self.fsm.handle_event(event)
        
        # 验证所有必需字段都存在
        required_fields = [
            "user_current_state",
            "user_next_state",
            "system_action",
            "message",
            "is_game_finished",
            "is_error"
        ]
        for field in required_fields:
            self.assertIn(field, result, f"缺少字段: {field}")
        
        # 验证值不为 None
        for field in required_fields:
            self.assertIsNotNone(result[field], f"字段为 None: {field}")
    
    def test_TC_7_2_system_action_valid_values(self):
        """TC-7.2: system_action 是有效的枚举值"""
        valid_actions = {
            "init", "answer", "finish", "continue", "ask_question", "make_guess",
            "chat", "reject", "record_answer", "prompt_answer", "prompt_judge", "error"
        }
        
        # 测试多个转换，验证 system_action 总是有效值
        states_and_events = [
            (GuessGameFSM.State.START, {"user_intent": GuessGameFSM.Intent.QUESTION}),
            (GuessGameFSM.State.USER_TURN, {"user_intent": GuessGameFSM.Intent.QUESTION}),
            (GuessGameFSM.State.WAITING_ANSWER, {"user_intent": GuessGameFSM.Intent.ANSWER}),
            (GuessGameFSM.State.AWAITING_JUDGEMENT, {
                "user_intent": GuessGameFSM.Intent.JUDGE,
                "user_judge": "correct"
            }),
        ]
        
        for state, event in states_and_events:
            self.fsm._state = state
            result = self.fsm.handle_event(event)
            self.assertIn(result["system_action"], valid_actions,
                         f"无效的 system_action: {result['system_action']}")
    
    def test_TC_7_3_boolean_fields_consistency(self):
        """TC-7.3: 布尔字段的一致性"""
        # 游戏未结束时
        self.fsm._state = GuessGameFSM.State.USER_TURN
        event1 = {"user_intent": GuessGameFSM.Intent.QUESTION}
        result1 = self.fsm.handle_event(event1)
        self.assertFalse(result1["is_game_finished"])
        self.assertFalse(result1["is_error"])
        
        # 游戏结束时
        self.fsm._state = GuessGameFSM.State.USER_TURN
        event2 = {
            "user_intent": GuessGameFSM.Intent.GUESS,
            "system_judge": "correct"
        }
        result2 = self.fsm.handle_event(event2)
        self.assertTrue(result2["is_game_finished"])
        self.assertFalse(result2["is_error"])
        
        # 错误时
        result3 = self.fsm.handle_event(None)
        self.assertFalse(result3["is_game_finished"])
        self.assertTrue(result3["is_error"])


class TestHelperMethods(unittest.TestCase):
    """测试辅助方法"""
    
    def setUp(self):
        self.fsm = GuessGameFSM()
    
    def test_get_state(self):
        """测试 get_state() 方法"""
        self.assertEqual(self.fsm.get_state(), GuessGameFSM.State.START)
        
        self.fsm._state = GuessGameFSM.State.FINISHED
        self.assertEqual(self.fsm.get_state(), GuessGameFSM.State.FINISHED)
    
    def test_is_finished(self):
        """测试 is_finished() 方法"""
        self.assertFalse(self.fsm.is_finished())
        
        self.fsm._state = GuessGameFSM.State.FINISHED
        self.assertTrue(self.fsm.is_finished())
    
    def test_is_error(self):
        """测试 is_error() 方法"""
        self.assertFalse(self.fsm.is_error())
        
        self.fsm._state = GuessGameFSM.State.ERROR
        self.assertTrue(self.fsm.is_error())
    
    def test_get_round_count(self):
        """测试 get_round_count() 方法"""
        self.assertEqual(self.fsm.get_round_count(), 0)
        
        self.fsm._round_count = 5
        self.assertEqual(self.fsm.get_round_count(), 5)


def run_all_tests():
    """运行所有测试并生成报告"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestStateTransitions))
    suite.addTests(loader.loadTestsFromTestCase(TestTurnLock))
    suite.addTests(loader.loadTestsFromTestCase(TestRoundManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestIntentHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestExceptionHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestCompleteGameFlow))
    suite.addTests(loader.loadTestsFromTestCase(TestReturnValueConsistency))
    suite.addTests(loader.loadTestsFromTestCase(TestHelperMethods))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印总结
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)
    print(f"运行测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ 所有测试通过！")
        return 0
    else:
        print("\n❌ 存在失败的测试")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_all_tests())
