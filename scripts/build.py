#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目构建脚本
用于打包BadgePatternTool为可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# 设置环境变量以支持UTF-8输出
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def check_dependencies():
    """检查构建依赖"""
    print("Checking build dependencies...")

    try:
        import PyInstaller
        print("PyInstaller is installed")
        return True
    except ImportError:
        print("PyInstaller not installed")
        print("Please run: pip install pyinstaller")
        return False

def clean_build_dirs():
    """清理构建目录"""
    print("Cleaning build directories...")

    project_root = Path(__file__).parent.parent
    dirs_to_clean = ["build", "dist"]

    for dir_name in dirs_to_clean:
        dir_path = project_root / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  Cleaned: {dir_name}")

    # 清理Python缓存文件
    for cache_dir in project_root.rglob("__pycache__"):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir)

    for pyc_file in project_root.rglob("*.pyc"):
        pyc_file.unlink()

    print("  Cleaned: Python cache files")

def build_executable():
    """构建可执行文件（使用优化的.spec文件）"""
    print("Building executable...")

    project_root = Path(__file__).parent.parent
    spec_file = project_root / "BadgePatternTool.spec"

    # 检查.spec文件是否存在
    if not spec_file.exists():
        print("BadgePatternTool.spec file not found")
        return False

    try:
        # 使用.spec文件构建
        cmd = [
            "pyinstaller",
            "--clean",                  # 清理临时文件
            "--noconfirm",             # 不询问覆盖
            str(spec_file)
        ]

        print(f"Executing command: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)

        if result.returncode == 0:
            print("Build successful")

            # 检查生成的文件大小
            exe_path = project_root / "dist" / "BadgePatternTool.exe"
            if exe_path.exists():
                file_size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"Executable size: {file_size_mb:.1f} MB")

                # 如果文件过大，给出警告
                if file_size_mb > 60:
                    print("File size is large, consider further optimization")
                elif file_size_mb < 30:
                    print("File size optimization is good")

            return True
        else:
            print("Build failed")
            print("Error output:")
            print(result.stderr)
            if result.stdout:
                print("Standard output:")
                print(result.stdout)
            return False

    except Exception as e:
        print(f"Build process error: {e}")
        return False

def copy_resources():
    """复制资源文件"""
    print("Copying resource files...")

    project_root = Path(__file__).parent.parent
    dist_dir = project_root / "dist"

    if not dist_dir.exists():
        print("dist directory does not exist")
        return False

    # 复制文档
    docs_to_copy = [
        "README.md",
        "CHANGELOG.md",
        "requirements.txt"
    ]

    for doc in docs_to_copy:
        src_path = project_root / doc
        if src_path.exists():
            dst_path = dist_dir / doc
            shutil.copy2(src_path, dst_path)
            print(f"  Copied: {doc}")

    # 复制docs目录
    docs_dir = project_root / "docs"
    if docs_dir.exists():
        dst_docs = dist_dir / "docs"
        shutil.copytree(docs_dir, dst_docs, dirs_exist_ok=True)
        print("  Copied: docs/")

    return True

def optimize_executable():
    """优化可执行文件"""
    print("Optimizing executable...")

    project_root = Path(__file__).parent.parent
    exe_path = project_root / "dist" / "BadgePatternTool.exe"

    if not exe_path.exists():
        print("Executable file not found")
        return False

    try:
        # 获取文件信息
        original_size = exe_path.stat().st_size
        print(f"  Original size: {original_size / 1024 / 1024:.1f} MB")

        # 这里可以添加其他优化步骤，比如：
        # - 使用UPX压缩（如果需要）
        # - 移除不必要的资源
        # - 验证文件完整性

        print("Executable optimization completed")
        return True

    except Exception as e:
        print(f"Optimization failed: {e}")
        return False

def create_installer_info():
    """创建安装说明"""
    print("Creating installation instructions...")

    project_root = Path(__file__).parent.parent
    dist_dir = project_root / "dist"
    exe_path = dist_dir / "BadgePatternTool.exe"

    # 获取文件大小
    file_size_mb = 0
    if exe_path.exists():
        file_size_mb = exe_path.stat().st_size / (1024 * 1024)

    install_info = f"""# BadgePatternTool Installation Guide

## Quick Start

1. **Run the Program**
   - Double-click `BadgePatternTool.exe` to start
   - First run may take a few seconds to load

2. **System Requirements**
   - Windows 7/8/10/11 (64-bit)
   - At least 100MB available disk space
   - Recommended 4GB memory

3. **Usage Instructions**
   - Check detailed documentation in `docs/` directory
   - Refer to `README.md` for feature overview

## File Description

- `BadgePatternTool.exe` - Main program file ({file_size_mb:.1f}MB)
- `README.md` - Project description
- `CHANGELOG.md` - Update log
- `docs/` - Detailed documentation directory

## Performance Optimization

This version includes the following optimizations:
- Removed unnecessary dependency modules
- Optimized startup speed
- Reduced file size
- Improved runtime efficiency

## Issue Feedback

If you encounter problems, please check the documentation or contact the developer.

---
BadgePatternTool v1.5.5 (Optimized)
Build time: {Path(__file__).stat().st_mtime}
"""

    info_file = dist_dir / "Installation_Guide.txt"
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write(install_info)

    print("  Created: Installation_Guide.txt")

def main():
    """主构建函数"""
    print("BadgePatternTool Build Script")
    print("=" * 40)

    # 检查依赖
    if not check_dependencies():
        return False

    # 清理构建目录
    clean_build_dirs()

    # 构建可执行文件
    if not build_executable():
        return False

    # 优化可执行文件
    if not optimize_executable():
        return False

    # 复制资源文件
    if not copy_resources():
        return False

    # 创建安装说明
    create_installer_info()

    print("\n" + "=" * 40)
    print("Build completed successfully!")
    print("Executable file is located in dist/ directory")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
