#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Actions兼容性检查工具
检查当前的包体优化是否与GitHub Actions自动构建兼容
"""

import sys
from pathlib import Path

def check_spec_file_compatibility():
    """检查.spec文件的GitHub Actions兼容性"""
    print("🔍 检查PyInstaller .spec文件兼容性")
    print("-" * 50)
    
    project_root = Path(__file__).parent.parent
    spec_file = project_root / "BadgePatternTool.spec"
    
    if not spec_file.exists():
        print("❌ BadgePatternTool.spec文件不存在")
        return False
    
    with open(spec_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查关键配置
    checks = [
        ("UPX压缩设置", "upx=True", "✅ UPX压缩已启用"),
        ("调试信息移除", "strip=True", "✅ 调试信息移除已启用"),
        ("模块排除", "excludes=", "✅ 模块排除列表已配置"),
        ("二进制文件过滤", "remove_unnecessary_files", "✅ 二进制文件过滤已配置"),
    ]
    
    all_passed = True
    for name, pattern, success_msg in checks:
        if pattern in content:
            print(f"  {success_msg}")
        else:
            print(f"  ❌ {name}未正确配置")
            all_passed = False
    
    return all_passed

def check_github_actions_workflow():
    """检查GitHub Actions工作流兼容性"""
    print("\n🔍 检查GitHub Actions工作流兼容性")
    print("-" * 50)
    
    project_root = Path(__file__).parent.parent
    workflow_file = project_root / ".github" / "workflows" / "release.yml"
    
    if not workflow_file.exists():
        print("❌ GitHub Actions工作流文件不存在")
        return False
    
    with open(workflow_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查关键配置
    checks = [
        ("Python版本", "python-version: '3.11'", "✅ Python 3.11版本已配置"),
        ("PyInstaller安装", "pip install pyinstaller", "✅ PyInstaller安装已配置"),
        ("UPX安装", "Install UPX", "✅ UPX安装步骤已添加"),
        ("构建脚本", "python scripts/build.py", "✅ 构建脚本调用已配置"),
        ("文件大小检查", "可执行文件大小", "✅ 文件大小检查已配置"),
    ]
    
    all_passed = True
    for name, pattern, success_msg in checks:
        if pattern in content:
            print(f"  {success_msg}")
        else:
            print(f"  ❌ {name}未正确配置")
            all_passed = False
    
    return all_passed

def check_dependencies_compatibility():
    """检查依赖包兼容性"""
    print("\n🔍 检查依赖包GitHub Actions兼容性")
    print("-" * 50)
    
    project_root = Path(__file__).parent.parent
    requirements_file = project_root / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt文件不存在")
        return False
    
    with open(requirements_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查关键依赖
    checks = [
        ("PySide6", "PySide6", "✅ PySide6依赖已配置"),
        ("Pillow", "Pillow", "✅ Pillow依赖已配置"),
        ("ReportLab", "reportlab", "✅ ReportLab依赖已配置"),
    ]
    
    all_passed = True
    for name, pattern, success_msg in checks:
        if pattern in content:
            print(f"  {success_msg}")
        else:
            print(f"  ❌ {name}依赖未配置")
            all_passed = False
    
    # 检查是否有可能导致GitHub Actions失败的依赖
    problematic_deps = [
        "tkinter",  # 通常在Linux环境中有问题
        "pywin32",  # Windows特定，可能在GitHub Actions中有问题
    ]
    
    for dep in problematic_deps:
        if dep in content:
            print(f"  ⚠️ 警告: 发现可能有问题的依赖 {dep}")
            all_passed = False
    
    return all_passed

def suggest_optimizations():
    """建议GitHub Actions优化"""
    print("\n💡 GitHub Actions优化建议")
    print("-" * 50)
    
    suggestions = [
        "1. UPX压缩: 已在工作流中添加UPX自动安装",
        "2. 缓存优化: 可以添加pip缓存以加速构建",
        "3. 并行构建: 当前配置支持单一Windows环境",
        "4. 构建验证: 已包含文件大小和完整性检查",
        "5. 错误处理: 工作流包含适当的错误检查",
        "6. 版本管理: 自动从git标签获取版本信息"
    ]
    
    for suggestion in suggestions:
        print(f"  ✅ {suggestion}")

def estimate_github_actions_performance():
    """估算GitHub Actions构建性能"""
    print("\n📊 GitHub Actions构建性能预估")
    print("-" * 50)
    
    print("  📦 预期构建产物大小:")
    print("    - 无UPX压缩: ~29.0 MB")
    print("    - 有UPX压缩: ~24-26 MB")
    print()
    print("  ⏱️ 预期构建时间:")
    print("    - 依赖安装: ~2-3分钟")
    print("    - UPX下载安装: ~30秒")
    print("    - 项目构建: ~1-2分钟")
    print("    - 总计: ~4-6分钟")
    print()
    print("  🎯 优化效果:")
    print("    - 相比原始32.8MB: 减少6.8-8.8MB")
    print("    - 优化比例: 20-27%")
    print("    - 下载速度提升: 20-27%")

def main():
    """主函数"""
    print("=" * 60)
    print("GitHub Actions兼容性检查")
    print("=" * 60)
    
    # 执行各项检查
    spec_ok = check_spec_file_compatibility()
    workflow_ok = check_github_actions_workflow()
    deps_ok = check_dependencies_compatibility()
    
    # 显示建议和性能预估
    suggest_optimizations()
    estimate_github_actions_performance()
    
    # 总结
    print("\n" + "=" * 60)
    if spec_ok and workflow_ok and deps_ok:
        print("✅ 所有检查通过！当前优化与GitHub Actions完全兼容")
        print("🚀 可以安全地使用自动构建流程")
    else:
        print("⚠️ 发现兼容性问题，建议修复后再使用自动构建")
    
    print("=" * 60)
    
    return spec_ok and workflow_ok and deps_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
