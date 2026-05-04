#!/usr/bin/env python3
"""
状态机测试快速启动脚本

用途：方便快速运行各种测试
运行方式：python run_tests.py [options]

选项：
    --unit              运行单元测试
    --integration       运行集成测试
    --all              运行所有测试（默认）
    --coverage         运行并显示覆盖率
    --specific CLASS   运行特定的测试类
    --help             显示帮助信息
"""

import sys
import subprocess
import os
from pathlib import Path


# 设置项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


def print_header(text):
    """打印标题"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def run_command(cmd, description=""):
    """运行命令"""
    if description:
        print_header(description)
    
    print(f"运行: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    return result.returncode == 0


def run_unit_tests():
    """运行单元测试"""
    print_header("运行单元测试")
    
    # 尝试使用 pytest，如果没有就用 unittest
    try:
        cmd = [sys.executable, "-m", "pytest", "tests/test_fsm.py", "-v", "--tb=short"]
        return run_command(cmd)
    except:
        cmd = [sys.executable, "-m", "unittest", "tests.test_fsm", "-v"]
        return run_command(cmd)


def run_integration_tests():
    """运行集成测试"""
    print_header("运行集成测试")
    
    cmd = [sys.executable, "tests/test_integration_examples.py"]
    return run_command(cmd)


def run_all_tests():
    """运行所有测试"""
    unit_success = run_unit_tests()
    integration_success = run_integration_tests()
    
    print_header("测试总结")
    print(f"单元测试：{'✅ 通过' if unit_success else '❌ 失败'}")
    print(f"集成测试：{'✅ 通过' if integration_success else '❌ 失败'}")
    print(f"\n总体：{'✅ 所有测试通过！' if (unit_success and integration_success) else '❌ 有测试失败'}")
    
    return unit_success and integration_success


def run_with_coverage():
    """运行测试并显示覆盖率"""
    print_header("运行测试并计算覆盖率")
    
    # 检查是否安装了 coverage
    try:
        import coverage
    except ImportError:
        print("❌ 需要安装 coverage 模块")
        print("安装命令: pip install coverage")
        return False
    
    # 运行覆盖率检查
    commands = [
        ([sys.executable, "-m", "coverage", "run", "-m", "pytest", "tests/test_fsm.py"],
         "运行 pytest 并收集覆盖率"),
        ([sys.executable, "-m", "coverage", "report", "-m"],
         "显示覆盖率报告"),
        ([sys.executable, "-m", "coverage", "html"],
         "生成 HTML 覆盖率报告"),
    ]
    
    all_success = True
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            all_success = False
    
    if all_success:
        print("\n✅ 覆盖率报告已生成")
        print("📊 HTML 报告位置: htmlcov/index.html")
    
    return all_success


def run_specific_test_class(class_name):
    """运行特定的测试类"""
    print_header(f"运行测试类: {class_name}")
    
    cmd = [sys.executable, "-m", "unittest", f"tests.test_fsm.{class_name}", "-v"]
    return run_command(cmd)


def show_help():
    """显示帮助信息"""
    print("""
状态机测试快速启动脚本

用法: python run_tests.py [选项]

选项:
    --unit              只运行单元测试
    --integration       只运行集成测试
    --all              运行所有测试（默认）
    --coverage         运行测试并显示覆盖率
    --specific CLASS   运行特定的测试类（例如：TestStateTransitions）
    --help             显示此帮助信息

例子:
    python run_tests.py                           # 运行所有测试
    python run_tests.py --unit                   # 只运行单元测试
    python run_tests.py --coverage               # 运行并显示覆盖率
    python run_tests.py --specific TestStateTransitions  # 运行特定测试类

可用的测试类:
    - TestStateTransitions          状态转换测试
    - TestTurnLock                  轮次锁测试
    - TestRoundManagement           轮次管理测试
    - TestIntentHandling            意图处理测试
    - TestExceptionHandling         异常处理测试
    - TestCompleteGameFlow          完整游戏流程测试
    - TestReturnValueConsistency    返回值一致性测试
    - TestHelperMethods             辅助方法测试
    """)


def main():
    """主函数"""
    print_header("状态机测试启动脚本")
    
    # 检查参数
    if len(sys.argv) < 2:
        # 默认运行所有测试
        success = run_all_tests()
    elif sys.argv[1] == "--help":
        show_help()
        return 0
    elif sys.argv[1] == "--unit":
        success = run_unit_tests()
    elif sys.argv[1] == "--integration":
        success = run_integration_tests()
    elif sys.argv[1] == "--all":
        success = run_all_tests()
    elif sys.argv[1] == "--coverage":
        success = run_with_coverage()
    elif sys.argv[1] == "--specific":
        if len(sys.argv) < 3:
            print("❌ 缺少测试类名")
            print("用法: python run_tests.py --specific <CLASS_NAME>")
            return 1
        success = run_specific_test_class(sys.argv[2])
    else:
        print(f"❌ 未知的选项: {sys.argv[1]}")
        print("使用 --help 查看帮助信息")
        return 1
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
