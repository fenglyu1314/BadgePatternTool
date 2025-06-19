#!/usr/bin/env python3
"""
代码质量检查工具 - 增强版
检查项目的代码质量、结构规范和潜在问题
包含语法检查、导入规范、复杂度分析、文档字符串检查等功能
"""

import ast
import sys
from pathlib import Path

def check_python_syntax(file_path):
    """检查Python语法"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"语法错误: {e}"
    except Exception as e:
        return False, f"解析错误: {e}"

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
                    issues.append(f"第{i}行: 重复导入 '{line}'")
                else:
                    seen_imports.add(line)

        return issues
    except Exception as e:
        return [f"检查导入失败: {e}"]

def check_code_complexity(file_path):
    """检查代码复杂度"""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检查函数长度
                if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                    func_length = node.end_lineno - node.lineno
                    if func_length > 50:
                        issues.append(f"函数 {node.name} 过长 ({func_length} 行)")

                # 检查参数数量
                if len(node.args.args) > 6:
                    issues.append(f"函数 {node.name} 参数过多 ({len(node.args.args)} 个)")

        return issues
    except Exception as e:
        return [f"检查复杂度失败: {e}"]

def check_docstrings(file_path):
    """检查文档字符串"""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)

        # 检查模块文档字符串
        if not ast.get_docstring(tree):
            issues.append("缺少模块文档字符串")

        # 检查类和函数文档字符串
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node) and not node.name.startswith('_'):
                    issues.append(f"缺少文档字符串: {node.name}")

        return issues
    except Exception as e:
        return [f"检查文档字符串失败: {e}"]

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
    print("🔍 BadgePatternTool 代码质量检查 - 增强版")
    print("=" * 60)

    project_root = Path(__file__).parent.parent

    # 检查文件结构
    print("\n📁 检查项目结构...")
    missing_items = check_file_structure()
    if missing_items:
        print(f"❌ 缺少文件/目录: {', '.join(missing_items)}")
    else:
        print("✅ 项目结构完整")

    # 检查Python文件
    print("\n🐍 检查Python代码...")
    python_files = list(project_root.glob("src/**/*.py"))
    total_issues = 0

    for file_path in python_files:
        rel_path = file_path.relative_to(project_root)
        print(f"\n  检查: {rel_path}")

        # 语法检查
        syntax_ok, syntax_error = check_python_syntax(file_path)
        if not syntax_ok:
            print(f"    ❌ {syntax_error}")
            total_issues += 1
            continue

        # 导入检查
        import_issues = check_imports(file_path)
        for issue in import_issues:
            print(f"    ⚠️  {issue}")
            total_issues += 1

        # 复杂度检查
        complexity_issues = check_code_complexity(file_path)
        for issue in complexity_issues:
            print(f"    ⚠️  {issue}")
            total_issues += 1

        # 文档字符串检查（仅对主要模块）
        if not str(file_path).endswith('__init__.py'):
            doc_issues = check_docstrings(file_path)
            for issue in doc_issues:
                print(f"    ℹ️  {issue}")
                # 文档字符串问题不计入严重问题

        if not import_issues and not complexity_issues:
            print("    ✅ 代码质量良好")

    # 总结
    print(f"\n📊 检查完成")
    print(f"总计发现 {total_issues} 个问题")

    if total_issues == 0:
        print("🎉 代码质量检查通过！")
        return True
    else:
        print("⚠️  建议修复发现的问题")
        return False

if __name__ == "__main__":
    success = run_quality_check()
    sys.exit(0 if success else 1)
