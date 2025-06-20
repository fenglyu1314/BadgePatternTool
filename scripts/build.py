#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project build script
Package BadgePatternTool as executable file
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Set environment variable to support UTF-8 output
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def check_dependencies():
    """Check build dependencies"""
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
    """Clean build directories"""
    print("Cleaning build directories...")

    project_root = Path(__file__).parent.parent
    dirs_to_clean = ["build", "dist"]

    for dir_name in dirs_to_clean:
        dir_path = project_root / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  Cleaned: {dir_name}")

    # Clean Python cache files
    for cache_dir in project_root.rglob("__pycache__"):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir)

    for pyc_file in project_root.rglob("*.pyc"):
        pyc_file.unlink()

    print("  Cleaned: Python cache files")

def build_executable():
    """Build executable file (using optimized .spec file)"""
    print("Building executable...")

    project_root = Path(__file__).parent.parent
    spec_file = project_root / "BadgePatternTool.spec"

    # Check if .spec file exists
    if not spec_file.exists():
        print("BadgePatternTool.spec file not found")
        return False

    try:
        # Build using .spec file
        cmd = [
            "pyinstaller",
            "--clean",                  # Clean temporary files
            "--noconfirm",             # No confirmation for overwrite
            str(spec_file)
        ]

        print(f"Executing command: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, encoding='utf-8', errors='ignore')

        if result.returncode == 0:
            print("Build successful")

            # Check generated file size
            exe_path = project_root / "dist" / "BadgePatternTool.exe"
            if exe_path.exists():
                file_size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"Executable size: {file_size_mb:.1f} MB")

                # Warning if file is too large
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
    """Copy essential user resource files"""
    print("Copying essential user files...")

    project_root = Path(__file__).parent.parent
    dist_dir = project_root / "dist"

    if not dist_dir.exists():
        print("dist directory does not exist")
        return False

    # Create user guide
    create_user_guide(dist_dir)

    # Skip development documentation, not needed for end users
    print("  Skipped: Development documentation (not needed for end users)")

    return True

def create_user_guide(dist_dir):
    """Create Chinese user guide"""
    print("Creating Chinese user guide...")

    # Get exe file size
    exe_path = dist_dir / "BadgePatternTool.exe"
    file_size_mb = 0
    if exe_path.exists():
        file_size_mb = exe_path.stat().st_size / (1024 * 1024)

    user_guide = f"""# BadgePatternTool 徽章图案工具

专业的徽章制作工具，用于图片处理和版面设计。

## 🚀 快速开始

### 1. 运行程序
- 双击 `BadgePatternTool.exe` 启动程序
- 首次运行可能需要几秒钟加载时间

### 2. 导入图片
- 点击"导入图片"按钮添加您的照片
- 支持 JPG、PNG、BMP、GIF 格式
- 可以一次导入多张图片

### 3. 编辑图片
- 点击任意图片进入编辑模式
- 拖拽移动图片位置，滚轮缩放大小
- 在圆形框架内调整图片位置

### 4. 版面设置
- 选择徽章尺寸：32mm、58mm 或 75mm
- 选择排版模式：网格模式或紧凑模式
- 调整徽章间距

### 5. 导出或打印
- 点击"导出图片"保存为图片文件
- 点击"打印"直接打印
- 支持 PDF、PNG、JPG 格式

## 💻 系统要求

- Windows 7/8/10/11 (64位)
- 至少 100MB 可用磁盘空间
- 推荐 4GB 内存

## ✨ 主要功能

- 🎨 批量图片导入和圆形裁剪
- ⚙️ 可配置徽章尺寸（32mm/58mm/75mm）
- 📐 智能A4排版（网格/紧凑模式）
- 🖼️ 交互式图片编辑
- 📄 多页面自动分页
- 🖨️ 高质量导出和直接打印

## 📁 文件说明

- `BadgePatternTool.exe` - 主程序文件 ({file_size_mb:.1f}MB)
- `使用说明.md` - 本文件

## 🆘 技术支持

如遇问题或有建议，请联系：
- **开发者**: 喵喵mya (231750570@qq.com)
- **问题反馈**: https://github.com/fenglyu1314/BadgePatternTool/issues

## 📝 使用技巧

### 图片编辑技巧
- 使用鼠标滚轮可以精确调整图片缩放
- 拖拽时保持平滑移动以获得最佳效果
- 注意安全圈（内圈）确保重要内容不被裁切

### 排版建议
- 32mm徽章适合头像或小图标
- 58mm徽章适合一般照片
- 75mm徽章适合需要更多细节的图片
- 紧凑模式可以在一页放置更多徽章

### 打印建议
- 使用高质量纸张获得最佳效果
- 打印前预览确保布局正确
- 建议使用彩色激光打印机

---
BadgePatternTool v1.5.6
**开发者**: 喵喵mya
**版权所有** © 2024
"""

    guide_path = dist_dir / "使用说明.md"
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(user_guide)

    print("  Created: User guide (Chinese version)")

def optimize_executable():
    """Optimize executable file"""
    print("Optimizing executable...")

    project_root = Path(__file__).parent.parent
    exe_path = project_root / "dist" / "BadgePatternTool.exe"

    if not exe_path.exists():
        print("Executable file not found")
        return False

    try:
        # Get file information
        original_size = exe_path.stat().st_size
        print(f"  Original size: {original_size / 1024 / 1024:.1f} MB")

        # Additional optimization steps can be added here:
        # - Use UPX compression (if needed)
        # - Remove unnecessary resources
        # - Verify file integrity

        print("Executable optimization completed")
        return True

    except Exception as e:
        print(f"Optimization failed: {e}")
        return False



def main():
    """Main build function"""
    print("BadgePatternTool Build Script")
    print("=" * 40)

    # Check dependencies
    if not check_dependencies():
        return False

    # Clean build directories
    clean_build_dirs()

    # Build executable
    if not build_executable():
        return False

    # Optimize executable
    if not optimize_executable():
        return False

    # Copy resource files
    if not copy_resources():
        return False

    # Create user guide (already called in copy_resources)

    print("\n" + "=" * 40)
    print("Build completed successfully!")
    print("Executable file is located in dist/ directory")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
