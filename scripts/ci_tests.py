#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CI环境测试运行器
专门为GitHub Actions等CI环境设计的测试运行器
跳过需要GUI的测试，只运行核心逻辑测试
"""

import os
import sys
import unittest
from pathlib import Path

# 设置环境变量以支持UTF-8输出
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "tests"))

def is_ci_environment():
    """检查是否在CI环境中运行"""
    ci_indicators = [
        'CI', 'CONTINUOUS_INTEGRATION', 'GITHUB_ACTIONS',
        'TRAVIS', 'CIRCLECI', 'JENKINS_URL', 'GITLAB_CI'
    ]
    return any(os.getenv(indicator) for indicator in ci_indicators)

def run_import_tests():
    """运行导入测试"""
    print("Import Test Runner")
    print("=" * 50)

    if is_ci_environment():
        print("Detected CI environment - running import tests only")
    else:
        print("Local environment detected - running import tests")

    # 测试核心模块导入
    modules_to_test = [
        'common.constants',
        'common.error_handler',
        'common.imports',
        'common.path_utils',
        'core.export_manager',
        'core.image_processor',
        'core.layout_engine',
        'utils.config',
        'utils.file_handler',
    ]

    import_errors = 0

    for module_name in modules_to_test:
        try:
            print(f"Testing import: {module_name}")
            __import__(module_name)
            print(f"  OK: {module_name}")
        except ImportError as e:
            print(f"  IMPORT ERROR: {module_name} - {e}")
            import_errors += 1
        except Exception as e:
            print(f"  ERROR: {module_name} - {e}")
            import_errors += 1

    # 输出总结
    print("\n" + "=" * 50)
    print("Import Test Summary")
    print("=" * 50)
    print(f"Modules tested: {len(modules_to_test)}")
    print(f"Import errors: {import_errors}")

    if import_errors == 0:
        print("All core modules imported successfully!")
        return True
    else:
        print("Some modules failed to import - check output above")
        return False

def run_syntax_check():
    """运行语法检查"""
    print("\nRunning syntax check...")
    print("-" * 30)
    
    src_dir = project_root / "src"
    python_files = list(src_dir.glob("**/*.py"))
    
    syntax_errors = 0
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                compile(f.read(), str(py_file), 'exec')
            print(f"  OK: {py_file.relative_to(project_root)}")
        except SyntaxError as e:
            print(f"  SYNTAX ERROR: {py_file.relative_to(project_root)} - {e}")
            syntax_errors += 1
        except Exception as e:
            print(f"  ERROR: {py_file.relative_to(project_root)} - {e}")
            syntax_errors += 1
    
    if syntax_errors == 0:
        print("All Python files have valid syntax")
        return True
    else:
        print(f"Found {syntax_errors} syntax errors")
        return False

def main():
    """主函数"""
    print("BadgePatternTool CI Test Suite")
    print("=" * 60)
    
    # 运行语法检查
    syntax_ok = run_syntax_check()
    
    # 运行导入测试
    tests_ok = run_import_tests()
    
    # 总结
    print("\n" + "=" * 60)
    print("Final Result")
    print("=" * 60)
    
    if syntax_ok and tests_ok:
        print("All checks passed - ready for CI/CD")
        return 0
    else:
        if not syntax_ok:
            print("Syntax check failed")
        if not tests_ok:
            print("Some tests failed")
        print("Please fix issues before proceeding")
        return 1

if __name__ == '__main__':
    sys.exit(main())
