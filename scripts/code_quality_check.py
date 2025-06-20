#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码质量检查工具 - 增强版
检查项目的代码质量、结构规范和潜在问题
包含语法检查、导入规范、复杂度分析、文档字符串检查等功能
"""

import ast
import sys
import os
from pathlib import Path

# 设置环境变量以支持UTF-8输出
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def check_python_syntax(file_path):
    """检查Python语法"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Parse error: {e}"

def check_imports(file_path):
    """检查导入语句规范"""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        import_lines = []
        seen_imports = set()

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                import_lines.append((i, line))

                # 检查重复导入
                if line in seen_imports:
                    issues.append(f"Line {i}: Duplicate import '{line}'")
                else:
                    seen_imports.add(line)

        return issues
    except Exception as e:
        return [f"Import check failed: {e}"]

def check_code_complexity(file_path):
    """检查代码复杂度"""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检查函数长度（放宽标准到100行）
                if hasattr(node, 'lineno') and hasattr(node, 'end_lineno') and node.end_lineno:
                    func_length = node.end_lineno - node.lineno
                    if func_length > 100:
                        issues.append(f"Function {node.name} too long ({func_length} lines)")

                # 检查参数数量（放宽标准到8个）
                if len(node.args.args) > 8:
                    issues.append(f"Function {node.name} has too many parameters ({len(node.args.args)})")

        return issues
    except Exception as e:
        return [f"Complexity check failed: {e}"]

def check_docstrings(file_path):
    """检查文档字符串"""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)

        # 检查模块文档字符串
        if not ast.get_docstring(tree):
            issues.append("Missing module docstring")

        # 检查类和函数文档字符串
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node) and not node.name.startswith('_'):
                    issues.append(f"Missing docstring: {node.name}")

        return issues
    except Exception as e:
        return [f"Docstring check failed: {e}"]

def check_file_structure():
    """检查项目文件结构"""
    project_root = Path(__file__).parent.parent
    required_dirs = ["src", "src/ui", "src/core", "src/utils", "tests", "docs"]
    required_files = [
        "src/main.py", "src/ui/main_window.py", "src/core/image_processor.py",
        "src/core/layout_engine.py", "src/core/export_manager.py",
        "src/utils/config.py", "requirements.txt", "README.md"
    ]

    missing = []
    for item in required_dirs + required_files:
        if not (project_root / item).exists():
            missing.append(item)

    return missing

def run_quality_check():
    """运行完整的质量检查"""
    print("Code Quality Check - BadgePatternTool")
    print("=" * 60)

    project_root = Path(__file__).parent.parent

    # 检查文件结构
    print("\nChecking project structure...")
    missing_items = check_file_structure()
    if missing_items:
        print(f"Missing files/directories: {', '.join(missing_items)}")
    else:
        print("Project structure is complete")

    # 检查Python文件
    print("\nChecking Python code...")
    python_files = list(project_root.glob("src/**/*.py"))
    total_issues = 0

    for file_path in python_files:
        rel_path = file_path.relative_to(project_root)
        print(f"\n  Checking: {rel_path}")

        # 语法检查
        syntax_ok, syntax_error = check_python_syntax(file_path)
        if not syntax_ok:
            print(f"    Error: {syntax_error}")
            total_issues += 1
            continue

        # 导入检查
        import_issues = check_imports(file_path)
        for issue in import_issues:
            print(f"    Warning: {issue}")
            total_issues += 1

        # 复杂度检查
        complexity_issues = check_code_complexity(file_path)
        for issue in complexity_issues:
            print(f"    Warning: {issue}")
            total_issues += 1

        # 文档字符串检查（仅对主要模块）
        if not str(file_path).endswith('__init__.py'):
            doc_issues = check_docstrings(file_path)
            for issue in doc_issues:
                print(f"    Info: {issue}")
                # 文档字符串问题不计入严重问题

        if not import_issues and not complexity_issues:
            print("    Code quality is good")

    # 总结
    print(f"\nCheck completed")
    print(f"Total issues found: {total_issues}")

    if total_issues == 0:
        print("Code quality check passed!")
        return True
    else:
        print("Recommend fixing the found issues")
        return False

if __name__ == "__main__":
    success = run_quality_check()
    sys.exit(0 if success else 1)
