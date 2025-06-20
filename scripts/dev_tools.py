#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开发工具脚本
提供常用的开发任务快捷命令
"""

import os
import sys
import subprocess
from pathlib import Path

# 设置环境变量以支持UTF-8输出
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def run_app():
    """运行应用程序"""
    print("Starting BadgePatternTool...")

    project_root = Path(__file__).parent.parent
    main_script = project_root / "src" / "main.py"

    if not main_script.exists():
        print("Error: Main script not found")
        return False

    try:
        subprocess.run([sys.executable, str(main_script)], cwd=project_root)
        return True
    except Exception as e:
        print(f"Error: Failed to start: {e}")
        return False

def run_tests():
    """运行测试"""
    print("Running tests...")

    project_root = Path(__file__).parent.parent
    test_runner = project_root / "tests" / "run_tests.py"

    if not test_runner.exists():
        print("Error: Test runner not found")
        return False

    try:
        result = subprocess.run([sys.executable, str(test_runner)], cwd=project_root)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: Test execution failed: {e}")
        return False

def run_integration_test():
    """运行集成测试"""
    print("Running integration tests...")

    project_root = Path(__file__).parent.parent
    integration_test = project_root / "tests" / "test_integration.py"

    if not integration_test.exists():
        print("Error: Integration test file not found")
        return False

    try:
        result = subprocess.run([sys.executable, str(integration_test)], cwd=project_root)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: Integration test failed: {e}")
        return False

def check_code_quality():
    """检查代码质量"""
    print("Checking code quality...")

    project_root = Path(__file__).parent.parent
    quality_checker = project_root / "scripts" / "code_quality_check.py"

    if not quality_checker.exists():
        print("Error: Code quality checker not found")
        return False

    try:
        result = subprocess.run([sys.executable, str(quality_checker)], cwd=project_root)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: Code quality check failed: {e}")
        return False

def build_app():
    """构建应用程序"""
    print("Building application...")

    project_root = Path(__file__).parent.parent
    build_script = project_root / "scripts" / "build.py"

    if not build_script.exists():
        print("Error: Build script not found")
        return False

    try:
        result = subprocess.run([sys.executable, str(build_script)], cwd=project_root)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: Build failed: {e}")
        return False

def install_deps():
    """安装依赖"""
    print("Installing project dependencies...")

    project_root = Path(__file__).parent.parent
    requirements_file = project_root / "requirements.txt"

    if not requirements_file.exists():
        print("Error: requirements.txt not found")
        return False

    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], cwd=project_root)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: Dependency installation failed: {e}")
        return False

def show_help():
    """显示帮助信息"""
    help_text = """
BadgePatternTool 开发工具

可用命令:
  run          - 运行应用程序
  test         - 运行所有测试
  integration  - 运行集成测试
  quality      - 检查代码质量
  build        - 构建可执行文件
  install      - 安装项目依赖
  help         - 显示此帮助信息

使用方法:
  python scripts/dev_tools.py <command>

示例:
  python scripts/dev_tools.py run
  python scripts/dev_tools.py test
  python scripts/dev_tools.py build
"""
    print(help_text)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    commands = {
        'run': run_app,
        'test': run_tests,
        'integration': run_integration_test,
        'quality': check_code_quality,
        'build': build_app,
        'install': install_deps,
        'help': show_help
    }
    
    if command in commands:
        if command == 'help':
            commands[command]()
        else:
            success = commands[command]()
            if success:
                print(f"Success: {command} command completed")
            else:
                print(f"Error: {command} command failed")
                sys.exit(1)
    else:
        print(f"Error: Unknown command: {command}")
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
