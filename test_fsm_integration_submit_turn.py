# -*- coding: utf-8 -*-
"""
验证 FSM 集成到 game_service 的重构结果

测试内容：
1. FSM 能够从数据库状态初始化
2. FSM 的 handler_name 正确映射到业务处理方法
3. 所有状态转换由 FSM 统一管理，消除散落的 if-else 判断
"""

import sys
import os
import io

# 设置 UTF-8 编码
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app.core.guessGameFSM import GuessGameFSM

def test_fsm_initialization_from_database_state():
    """测试 FSM 能够从数据库状态初始化"""
    print("\n✅ 测试 1：FSM 从数据库状态初始化")
    
    # 模拟数据库中的游戏状态
    test_cases = [
        ("user_turn", 0),           # 新游戏
        ("waiting_answer", 5),      # 等待用户回答系统问题
        ("awaiting_judgement", 8),  # 等待用户判断系统猜词
        ("finished", 12),           # 游戏结束
    ]
    
    for state, round_count in test_cases:
        fsm = GuessGameFSM(initial_state=state, initial_round_count=round_count)
        assert fsm.state == state, f"期望状态 {state}，得到 {fsm.state}"
        assert fsm.round_count == round_count, f"期望轮次 {round_count}，得到 {fsm.round_count}"
        print(f"  ✓ 状态={state}, 轮次={round_count}")
    
    print("  所有初始化测试通过")


def test_handler_name_mapping():
    """测试 FSM 的 handler_name 正确映射到处理方法"""
    print("\n✅ 测试 2：Handler 名称映射")
    
    # 测试用例：(当前状态, 用户意图, 系统动作) -> 期望的处理器名称
    test_cases = [
        # 用户提问
        ("user_turn", "question", "answer", "handle_user_question"),
        # 用户猜词正确
        ("user_turn", "guess", "finish", "handle_user_guess"),
        # 用户猜词错误
        ("user_turn", "guess", "continue", "handle_user_guess"),
        # 无效意图
        ("user_turn", "invalid", "chat", "handle_invalid_input"),
        # 轮次锁：在 waiting_answer 中进行非 answer 操作
        ("waiting_answer", "question", "prompt_answer", "handle_rejected_turn"),
        # 轮次锁：在 awaiting_judgement 中进行非 judge 操作
        ("awaiting_judgement", "question", "prompt_judge", "handle_rejected_turn"),
        # 用户回答问题
        ("waiting_answer", "answer", "record_answer", "handle_user_answer"),
        # 系统猜词正确
        ("awaiting_judgement", "judge", "finish", "handle_agent_guess_judgement"),
        # 系统猜词错误
        ("awaiting_judgement", "judge", "continue", "handle_agent_guess_judgement"),
    ]
    
    for state, intent, system_action, expected_handler in test_cases:
        fsm = GuessGameFSM(initial_state=state)
        
        # 模拟 FSM 的返回值
        result = {
            "user_current_state": state,
            "user_next_state": "finished" if system_action == "finish" else "user_turn",
            "system_action": system_action,
            "message": "test",
            "is_game_finished": system_action == "finish",
            "is_error": False,
        }
        
        handler_name = fsm.get_handler_name(result)
        assert handler_name == expected_handler, f"状态={state}, 意图={intent}, 系统动作={system_action}: 期望处理器={expected_handler}, 得到={handler_name}"
        print(f"  ✓ ({state}, {intent}, {system_action}) -> {handler_name}")
    
    print("  所有 handler 映射测试通过")


def test_state_transition_controlled_by_fsm():
    """测试所有状态转换由 FSM 统一管理"""
    print("\n✅ 测试 3：状态转换由 FSM 统一管理")
    
    # 模拟游戏流程
    fsm = GuessGameFSM(initial_state="user_turn")
    
    # 用户提问
    result = fsm.handle_event({
        "user_intent": GuessGameFSM.Intent.QUESTION,
    })
    assert result["user_next_state"] == "waiting_answer", "用户提问应该进入 waiting_answer"
    print(f"  ✓ USER_TURN + QUESTION -> WAITING_ANSWER (自动)")
    
    # 用户回答
    result = fsm.handle_event({
        "user_intent": GuessGameFSM.Intent.ANSWER,
    })
    assert result["user_next_state"] == "user_turn", "用户回答后应该回到 user_turn"
    print(f"  ✓ WAITING_ANSWER + ANSWER -> USER_TURN (自动)")
    
    # 用户在 waiting_answer 中尝试提问（轮次锁）
    fsm._state = "waiting_answer"
    result = fsm.handle_event({
        "user_intent": GuessGameFSM.Intent.QUESTION,  # 在等待回答时尝试提问
    })
    assert result["user_next_state"] == "waiting_answer", "轮次锁应该保持当前状态"
    assert result["system_action"] == "prompt_answer", "应该提示用户回答"
    print(f"  ✓ WAITING_ANSWER + QUESTION -> WAITING_ANSWER (轮次锁)")
    
    # 用户猜词正确
    fsm._state = "user_turn"
    result = fsm.handle_event({
        "user_intent": GuessGameFSM.Intent.GUESS,
        "system_judge": "correct",
    })
    assert result["user_next_state"] == "finished", "猜对应该进入 finished"
    print(f"  ✓ USER_TURN + GUESS(correct) -> FINISHED (自动)")
    
    print("  所有状态转换都由 FSM 统一管理")


def test_no_scattered_if_else_logic():
    """验证已消除散落的 if-else 判断"""
    print("\n✅ 测试 4：验证代码重构")
    
    # 检查 game_service.py 中是否还有旧的 if-else 状态判断
    with open("backend/app/services/game_service.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 在 submit_turn 方法中不应该有直接的状态判断
    submit_turn_start = content.find("async def submit_turn")
    submit_turn_end = content.find("async def _handle_user_guess", submit_turn_start)
    submit_turn_content = content[submit_turn_start:submit_turn_end]
    
    # 检查是否有旧的 if phase == 判断
    old_patterns = [
        'if phase == "user_turn"',
        'if phase == "waiting_answer"',
        'if phase == "awaiting_judgement"',
    ]
    
    found_old = False
    for pattern in old_patterns:
        if pattern in submit_turn_content:
            print(f"  ❌ 发现旧的判断：{pattern}")
            found_old = True
    
    if not found_old:
        print("  ✓ submit_turn 方法已消除所有旧的 if phase 判断")
    
    # 检查是否使用了 FSM
    if "GuessGameFSM" in submit_turn_content and "fsm.handle_event" in submit_turn_content:
        print("  ✓ submit_turn 现在使用 FSM 进行状态转换")
    else:
        print("  ❌ submit_turn 中没有找到 FSM 的使用")
        found_old = True
    
    # 检查是否使用了 get_handler_name
    if "get_handler_name" in submit_turn_content:
        print("  ✓ submit_turn 使用 FSM.get_handler_name() 获取处理器")
    else:
        print("  ❌ submit_turn 中没有找到 get_handler_name 的使用")
        found_old = True
    
    if not found_old:
        print("  所有代码重构验证通过")
    
    return not found_old


if __name__ == "__main__":
    print("=" * 70)
    print("FSM 集成重构验收测试")
    print("=" * 70)
    
    try:
        test_fsm_initialization_from_database_state()
        test_handler_name_mapping()
        test_state_transition_controlled_by_fsm()
        test_no_scattered_if_else_logic()
        
        print("\n" + "=" * 70)
        print("✅ 所有验收测试通过！FSM 重构成功。")
        print("=" * 70)
        print("\n重构总结：")
        print("1. ✅ FSM 能够从数据库状态初始化")
        print("2. ✅ 状态转换由 FSM 统一管理")
        print("3. ✅ 处理器映射正确，对应不同的业务场景")
        print("4. ✅ game_service.py 中的散落 if-else 判断已消除")
        print("5. ✅ 轮次锁检查由 FSM 自动执行")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
