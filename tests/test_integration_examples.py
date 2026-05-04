# -*- coding: utf-8 -*-
"""
状态机集成测试示例

这个脚本演示了多种游戏场景，可以直接运行查看结果。

运行方式：
    python tests/test_integration_examples.py
"""

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


def print_result(result, title=""):
    """打印结果"""
    if title:
        print(f"\n>>> {title}")
    print(f"  当前状态: {result['user_current_state']}")
    print(f"  下一状态: {result['user_next_state']}")
    print(f"  系统动作: {result['system_action']}")
    print(f"  提示信息: {result['message']}")
    print(f"  游戏结束: {result['is_game_finished']}")


def scenario_1_user_wins_by_guessing():
    """场景 1：用户通过直接猜词赢得游戏"""
    print("\n" + "="*70)
    print("场景 1：用户通过直接猜词赢得游戏")
    print("="*70)
    
    fsm = GuessGameFSM()
    
    # 游戏开始
    print(f"\n初始状态: {fsm.state}")
    print(f"初始轮次: {fsm.round_count}")
    
    # 第一次事件：START → USER_TURN（初始化）
    print("\n第 1 步：初始化游戏")
    event_init = {"user_intent": GuessGameFSM.Intent.QUESTION}
    result_init = fsm.handle_event(event_init)
    print(f"  当前状态: {fsm.state}")
    print(f"  轮次: {fsm.round_count}")
    
    # 用户直接猜词（正确）
    print("\n第 2 步：用户猜词（正确）")
    event = {
        "user_intent": GuessGameFSM.Intent.GUESS,
        "system_judge": "correct"
    }
    result = fsm.handle_event(event)
    print_result(result, "用户猜词（正确）")
    print(f"当前轮次: {fsm.round_count}")
    
    assert result['user_next_state'] == GuessGameFSM.State.FINISHED
    assert result['is_game_finished']
    print("\n✅ 场景 1 通过")


def scenario_2_user_wins_after_interaction():
    """场景 2：用户通过多轮交互后赢得游戏"""
    print("\n" + "="*70)
    print("场景 2：用户通过多轮交互后赢得游戏")
    print("="*70)
    
    fsm = GuessGameFSM()
    
    # 第 1 轮：用户提问
    print(f"\n初始状态: {fsm.state}")
    event1 = {"user_intent": GuessGameFSM.Intent.QUESTION}
    result1 = fsm.handle_event(event1)
    print_result(result1, "第 1 轮：用户提问")
    print(f"轮次: {fsm.round_count}/{fsm.max_rounds}")
    
    # 用户回答
    event2 = {"user_intent": GuessGameFSM.Intent.ANSWER}
    result2 = fsm.handle_event(event2)
    print_result(result2, "用户回答系统问题")
    print(f"轮次: {fsm.round_count}/{fsm.max_rounds}")
    
    # 第 2 轮：用户猜词（错误）
    event3 = {
        "user_intent": GuessGameFSM.Intent.GUESS,
        "system_judge": "incorrect"
    }
    result3 = fsm.handle_event(event3)
    print_result(result3, "第 2 轮：用户猜词（错误）")
    print(f"轮次: {fsm.round_count}/{fsm.max_rounds}")
    
    # 第 3 轮：用户猜词（正确）
    event4 = {
        "user_intent": GuessGameFSM.Intent.GUESS,
        "system_judge": "correct"
    }
    result4 = fsm.handle_event(event4)
    print_result(result4, "第 3 轮：用户猜词（正确）")
    print(f"轮次: {fsm.round_count}/{fsm.max_rounds}")
    
    assert result4['user_next_state'] == GuessGameFSM.State.FINISHED
    assert fsm.round_count == 3
    print("\n✅ 场景 2 通过")


def scenario_3_system_wins():
    """场景 3：系统通过正确猜词赢得游戏"""
    print("\n" + "="*70)
    print("场景 3：系统通过正确猜词赢得游戏")
    print("="*70)
    
    fsm = GuessGameFSM()
    fsm._state = GuessGameFSM.State.USER_TURN
    
    # 用户让行，系统猜词
    print(f"\n初始状态: {fsm.state}")
    event1 = {
        "user_intent": GuessGameFSM.Intent.YIELD_TURN,
        "system_next_action": GuessGameFSM.SystemAction.MAKE_GUESS
    }
    result1 = fsm.handle_event(event1)
    print_result(result1, "用户让行，系统猜词")
    print(f"轮次: {fsm.round_count}/{fsm.max_rounds}")
    
    # 用户确认系统猜词正确
    event2 = {
        "user_intent": GuessGameFSM.Intent.JUDGE,
        "user_judge": "correct"
    }
    result2 = fsm.handle_event(event2)
    print_result(result2, "用户确认系统猜词正确")
    
    assert result2['user_next_state'] == GuessGameFSM.State.FINISHED
    assert fsm.round_count == 1
    print("\n✅ 场景 3 通过")


def scenario_4_turn_lock():
    """场景 4：轮次锁演示"""
    print("\n" + "="*70)
    print("场景 4：轮次锁演示 - WAITING_ANSWER 中的强制回答")
    print("="*70)
    
    fsm = GuessGameFSM()
    fsm._state = GuessGameFSM.State.WAITING_ANSWER
    
    print(f"\n初始状态: {fsm.state}")
    
    # 尝试猜词（非法）
    print("\n用户尝试在 WAITING_ANSWER 中猜词（非法，触发轮次锁）:")
    event1 = {
        "user_intent": GuessGameFSM.Intent.GUESS,
        "system_judge": "incorrect"
    }
    result1 = fsm.handle_event(event1)
    print_result(result1)
    assert result1['user_next_state'] == GuessGameFSM.State.WAITING_ANSWER
    assert result1['system_action'] == "prompt_answer"
    
    # 再次尝试提问（仍然非法）
    print("\n用户再次尝试提问（仍然非法）:")
    event2 = {"user_intent": GuessGameFSM.Intent.QUESTION}
    result2 = fsm.handle_event(event2)
    print_result(result2)
    assert result2['user_next_state'] == GuessGameFSM.State.WAITING_ANSWER
    
    # 最后回答（合法）
    print("\n用户最后回答系统问题（合法）:")
    event3 = {"user_intent": GuessGameFSM.Intent.ANSWER}
    result3 = fsm.handle_event(event3)
    print_result(result3)
    assert result3['user_next_state'] == GuessGameFSM.State.USER_TURN
    
    print("\n✅ 场景 4 通过 - 轮次锁工作正常")


def scenario_5_round_limit():
    """场景 5：达到轮次限制自动结束游戏"""
    print("\n" + "="*70)
    print("场景 5：达到轮次限制自动结束游戏")
    print("="*70)
    
    fsm = GuessGameFSM()
    fsm._round_count = 19  # 设置为接近上限
    fsm._state = GuessGameFSM.State.USER_TURN
    
    print(f"\n当前轮次: {fsm.round_count}")
    print(f"最大轮次: {fsm.max_rounds}")
    print(f"剩余轮次: {fsm.get_remaining_rounds()}")
    
    # 进行一个操作，轮次变为 20
    print("\n用户猜词（错误），轮次变为 20:")
    event1 = {
        "user_intent": GuessGameFSM.Intent.GUESS,
        "system_judge": "incorrect"
    }
    result1 = fsm.handle_event(event1)
    print(f"轮次更新后: {fsm.round_count}/{fsm.max_rounds}")
    print(f"剩余轮次: {fsm.get_remaining_rounds()}")
    
    # 再进行一个操作，应该返回 FINISHED（因为达到限制）
    print("\n再次进行操作（应该自动返回 FINISHED）:")
    event2 = {"user_intent": GuessGameFSM.Intent.QUESTION}
    result2 = fsm.handle_event(event2)
    print_result(result2, "游戏因轮次限制自动结束")
    
    assert result2['user_next_state'] == GuessGameFSM.State.FINISHED
    print("\n✅ 场景 5 通过 - 轮次限制正常工作")


def scenario_6_invalid_input():
    """场景 6：异常输入处理"""
    print("\n" + "="*70)
    print("场景 6：异常输入处理")
    print("="*70)
    
    fsm = GuessGameFSM()
    
    # 测试 1：None 事件
    print("\n测试 1：None 事件")
    result1 = fsm.handle_event(None)
    print_result(result1)
    assert result1['is_error']
    print("✅ None 事件被正确处理为错误")
    
    # 测试 2：空字典
    print("\n测试 2：空字典事件")
    fsm = GuessGameFSM()
    result2 = fsm.handle_event({})
    print_result(result2)
    assert result2['is_error']
    print("✅ 空字典被正确处理为错误")
    
    # 测试 3：未知意图
    print("\n测试 3：未知意图值")
    fsm = GuessGameFSM()
    result3 = fsm.handle_event({"user_intent": "unknown_intent"})
    print_result(result3)
    assert result3['is_error']
    print("✅ 未知意图被正确处理为错误")
    
    # 测试 4：闲聊（INVALID）
    print("\n测试 4：用户闲聊（INVALID 意图）")
    fsm = GuessGameFSM()
    fsm._state = GuessGameFSM.State.USER_TURN
    result4 = fsm.handle_event({"user_intent": GuessGameFSM.Intent.INVALID})
    print_result(result4)
    assert not result4['is_error']
    assert result4['system_action'] == "chat"
    print("✅ 闲聊被正确处理")
    
    print("\n✅ 场景 6 通过 - 异常输入处理正常")


def scenario_7_game_reset():
    """场景 7：游戏重置"""
    print("\n" + "="*70)
    print("场景 7：游戏重置")
    print("="*70)
    
    fsm = GuessGameFSM()
    
    # 进行一些操作
    print("\n进行一些游戏操作...")
    fsm._state = GuessGameFSM.State.USER_TURN
    event = {"user_intent": GuessGameFSM.Intent.QUESTION}
    fsm.handle_event(event)
    
    print(f"操作后 - 状态: {fsm.state}, 轮次: {fsm.round_count}")
    
    # 重置
    print("\n调用 reset()...")
    fsm.reset()
    
    print(f"重置后 - 状态: {fsm.state}, 轮次: {fsm.round_count}")
    assert fsm.state == GuessGameFSM.State.START
    assert fsm.round_count == 0
    
    print("\n✅ 场景 7 通过 - 游戏重置正常")


def scenario_8_complex_game():
    """场景 8：复杂的多轮游戏"""
    print("\n" + "="*70)
    print("场景 8：复杂的多轮游戏")
    print("="*70)
    
    fsm = GuessGameFSM()
    
    # 第一次事件：初始化游戏（START → USER_TURN）
    print(f"\n初始化：{fsm.state} → USER_TURN")
    init_event = {"user_intent": GuessGameFSM.Intent.QUESTION}
    fsm.handle_event(init_event)
    print(f"当前状态：{fsm.state}，轮次：{fsm.round_count}")
    
    operations = [
        ("用户提问", {"user_intent": GuessGameFSM.Intent.QUESTION}, GuessGameFSM.State.WAITING_ANSWER),
        ("用户回答", {"user_intent": GuessGameFSM.Intent.ANSWER}, GuessGameFSM.State.USER_TURN),
        ("用户猜词失败", {
            "user_intent": GuessGameFSM.Intent.GUESS,
            "system_judge": "incorrect"
        }, GuessGameFSM.State.USER_TURN),
        ("用户让行求助", {
            "user_intent": GuessGameFSM.Intent.YIELD_TURN,
            "system_next_action": GuessGameFSM.SystemAction.ASK_QUESTION
        }, GuessGameFSM.State.WAITING_ANSWER),
        ("用户再次回答", {"user_intent": GuessGameFSM.Intent.ANSWER}, GuessGameFSM.State.USER_TURN),
        ("用户猜词成功", {
            "user_intent": GuessGameFSM.Intent.GUESS,
            "system_judge": "correct"
        }, GuessGameFSM.State.FINISHED),
    ]
    
    for i, (title, event, expected_state) in enumerate(operations, 1):
        print(f"\n步骤 {i}: {title}")
        result = fsm.handle_event(event)
        print(f"  事件: {event}")
        print(f"  状态: {fsm.state}")
        print(f"  轮次: {fsm.round_count}")
        assert fsm.state == expected_state, f"期望 {expected_state}，但得到 {fsm.state}"
    
    print(f"\n最终状态: {fsm.state}")
    print(f"最终轮次: {fsm.round_count}")
    print("\n✅ 场景 8 通过 - 复杂游戏流程正常")


def main():
    """运行所有场景"""
    print("\n" + "="*70)
    print("状态机集成测试 - 场景演示")
    print("="*70)
    
    scenarios = [
        scenario_1_user_wins_by_guessing,
        scenario_2_user_wins_after_interaction,
        scenario_3_system_wins,
        scenario_4_turn_lock,
        scenario_5_round_limit,
        scenario_6_invalid_input,
        scenario_7_game_reset,
        scenario_8_complex_game,
    ]
    
    passed = 0
    failed = 0
    
    for scenario in scenarios:
        try:
            scenario()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ 场景失败: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ 场景出错: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # 总结
    print("\n" + "="*70)
    print("集成测试总结")
    print("="*70)
    print(f"总共运行: {len(scenarios)} 个场景")
    print(f"成功: {passed} ✅")
    print(f"失败: {failed} ❌")
    
    if failed == 0:
        print("\n🎉 所有集成测试通过！")
        return 0
    else:
        print("\n⚠️ 有一些集成测试失败")
        return 1


if __name__ == "__main__":
    import sys
    
    # 检查是否指定了输出文件参数
    output_file = None
    for arg in sys.argv[1:]:
        if arg.startswith('--output='):
            output_file = arg.split('=')[1]
    
    # 如果指定了输出文件，重定向输出到文件（使用 UTF-8 编码）
    if output_file:
        output_handle = open(output_file, 'w', encoding='utf-8')
        sys.stdout = output_handle
        sys.stderr = output_handle
    
    try:
        sys.exit(main())
    finally:
        if output_file:
            output_handle.close()
