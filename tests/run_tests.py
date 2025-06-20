#!/usr/bin/env python3
"""
BadgePatternTool 测试运行器
运行所有测试并生成报告
"""

import unittest
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("BadgePatternTool 自动化测试")
    print("=" * 60)
    
    # 发现并运行测试
    loader = unittest.TestLoader()
    start_dir = str(Path(__file__).parent)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)
    print(f"运行测试数量: {result.testsRun}")
    print(f"失败数量: {len(result.failures)}")
    print(f"错误数量: {len(result.errors)}")
    print(f"跳过数量: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    # 计算测试覆盖率
    if result.testsRun > 0:
        success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
        print(f"\n测试成功率: {success_rate:.1f}%")

        if success_rate >= 90:
            print("✅ 测试覆盖度良好")
        elif success_rate >= 70:
            print("⚠️ 测试覆盖度一般，建议增加测试")
        else:
            print("❌ 测试覆盖度不足，需要增加更多测试")

    # 返回是否所有测试都通过
    success = len(result.failures) == 0 and len(result.errors) == 0

    if success:
        print("\n🎉 所有测试通过！")
        print("建议运行以下命令进行更全面的测试:")
        print("  python tests/test_performance.py  # 性能测试")
        print("  python tests/test_common.py       # 公共模块测试")
        print("  python tests/test_ui.py           # UI组件测试")
    else:
        print("\n❌ 部分测试失败，请检查上述错误信息。")

    return success

def run_specific_test(test_module):
    """运行特定测试模块"""
    print(f"运行测试模块: {test_module}")
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_module)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # 运行特定测试
        test_module = sys.argv[1]
        success = run_specific_test(test_module)
    else:
        # 运行所有测试
        success = run_all_tests()
    
    sys.exit(0 if success else 1)
