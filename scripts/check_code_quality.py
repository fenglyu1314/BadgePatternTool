#!/usr/bin/env python3
"""
代码质量检查脚本
检查代码规范、导入语句、文档字符串等
"""

import os
import sys
import ast
from pathlib import Path

def check_file_structure():
    """检查文件结构"""
    print("检查项目文件结构...")
    
    project_root = Path(__file__).parent.parent
    required_dirs = [
        "src",
        "src/ui", 
        "src/core",
        "src/utils",
        "docs",
        "tests"
    ]
    
    required_files = [
        "src/main.py",
        "src/ui/main_window.py",
        "src/core/image_processor.py",
        "src/core/layout_engine.py", 
        "src/core/export_manager.py",
        "src/utils/config.py",
        "src/utils/file_handler.py",
        "requirements.txt",
        "README.md",
        "CHANGELOG.md"
    ]
    
    missing_dirs = []
    missing_files = []
    
    # 检查目录
    for dir_path in required_dirs:
        if not (project_root / dir_path).exists():
            missing_dirs.append(dir_path)
    
    # 检查文件
    for file_path in required_files:
        if not (project_root / file_path).exists():
            missing_files.append(file_path)
    
    if missing_dirs:
        print(f"❌ 缺少目录: {', '.join(missing_dirs)}")
        return False
    
    if missing_files:
        print(f"❌ 缺少文件: {', '.join(missing_files)}")
        return False
    
    print("✅ 文件结构检查通过")
    return True

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
    """检查导入语句"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        import_section_ended = False
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # 跳过注释和空行
            if not line or line.startswith('#') or line.startswith('"""') or line.startswith("'''"):
                continue
            
            # 检查导入语句
            if line.startswith('import ') or line.startswith('from '):
                if import_section_ended:
                    issues.append(f"第{i}行: 导入语句应该在文件顶部")
            else:
                if line and not line.startswith('"""') and not line.startswith("'''"):
                    import_section_ended = True
        
        return issues
        
    except Exception as e:
        return [f"检查导入失败: {e}"]

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
                if not ast.get_docstring(node):
                    issues.append(f"缺少文档字符串: {node.name}")
        
        return issues
        
    except Exception as e:
        return [f"检查文档字符串失败: {e}"]

def check_code_quality():
    """检查代码质量"""
    print("BadgePatternTool 代码质量检查")
    print("=" * 50)
    
    # 检查文件结构
    if not check_file_structure():
        return False
    
    project_root = Path(__file__).parent.parent
    python_files = []
    
    # 收集所有Python文件
    for pattern in ["src/**/*.py", "tests/**/*.py"]:
        python_files.extend(project_root.glob(pattern))
    
    total_issues = 0
    
    for file_path in python_files:
        print(f"\n检查文件: {file_path.relative_to(project_root)}")
        
        # 检查语法
        syntax_ok, syntax_error = check_python_syntax(file_path)
        if not syntax_ok:
            print(f"  ❌ {syntax_error}")
            total_issues += 1
            continue
        else:
            print("  ✅ 语法检查通过")
        
        # 检查导入
        import_issues = check_imports(file_path)
        if import_issues:
            for issue in import_issues:
                print(f"  ⚠️  {issue}")
                total_issues += 1
        else:
            print("  ✅ 导入检查通过")
        
        # 检查文档字符串（仅对src目录）
        if "src" in str(file_path):
            doc_issues = check_docstrings(file_path)
            if doc_issues:
                for issue in doc_issues:
                    print(f"  ⚠️  {issue}")
                    total_issues += 1
            else:
                print("  ✅ 文档字符串检查通过")
    
    print("\n" + "=" * 50)
    print(f"代码质量检查完成")
    print(f"发现问题: {total_issues} 个")
    
    if total_issues == 0:
        print("🎉 代码质量良好！")
        return True
    else:
        print("⚠️  建议修复上述问题以提高代码质量")
        return False

if __name__ == "__main__":
    success = check_code_quality()
    sys.exit(0 if success else 1)
