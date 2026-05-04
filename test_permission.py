# -*- coding: utf-8 -*-
"""
数据权限控制测试脚本

验证 GuessGameFSM 的属性是否正确实现只读控制
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app.core.guessGameFSM import GuessGameFSM

def test_readonly_properties():
    """测试只读属性权限控制"""
    fsm = GuessGameFSM()
    
    # 测试 1: 读取（应该成功）
    print("✅ 测试 1: 读取属性（应该成功）")
    print(f"  state: {fsm.state}")
    print(f"  round_count: {fsm.round_count}")
    print(f"  max_rounds: {fsm.max_rounds}")
    
    # 测试 2: 尝试写入 state（应该失败）
    print("\n✅ 测试 2: 尝试写入 state（应该失败）")
    try:
        fsm.state = "user_turn"
        print("  ❌ 错误：state 属性被修改了！（权限控制失败）")
        return False
    except AttributeError as e:
        print(f"  ✅ 正确：收到 AttributeError")
    
    # 测试 3: 尝试写入 round_count（应该失败）
    print("\n✅ 测试 3: 尝试写入 round_count（应该失败）")
    try:
        fsm.round_count = 100
        print("  ❌ 错误：round_count 属性被修改了！（权限控制失败）")
        return False
    except AttributeError as e:
        print(f"  ✅ 正确：收到 AttributeError")
    
    # 测试 4: 尝试写入 max_rounds（应该失败）
    print("\n✅ 测试 4: 尝试写入 max_rounds（应该失败）")
    try:
        fsm.max_rounds = 50
        print("  ❌ 错误：max_rounds 属性被修改了！（权限控制失败）")
        return False
    except AttributeError as e:
        print(f"  ✅ 正确：收到 AttributeError")
    
    # 测试 5: 验证内部状态仍能通过方法修改
    print("\n✅ 测试 5: 内部状态仍能通过方法修改")
    fsm.reset()
    print(f"  reset() 后：state={fsm.state}, round_count={fsm.round_count}")
    
    # 测试 6: 验证游戏流程正常工作
    print("\n✅ 测试 6: 验证游戏流程正常工作")
    event = {"user_intent": GuessGameFSM.Intent.QUESTION}
    result = fsm.handle_event(event)
    print(f"  处理事件后：state={fsm.state}, round_count={fsm.round_count}")
    print(f"  返回格式正确：{all(k in result for k in ['user_current_state', 'user_next_state', 'system_action', 'message'])}")
    
    return True


if __name__ == "__main__":
    print("=" * 70)
    print("数据权限控制测试")
    print("=" * 70)
    
    success = test_readonly_properties()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ 所有权限控制测试通过！数据已完全保护。")
    else:
        print("❌ 权限控制测试失败！")
    print("=" * 70)
    
    sys.exit(0 if success else 1)
