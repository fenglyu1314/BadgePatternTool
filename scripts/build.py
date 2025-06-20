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
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, encoding='utf-8', errors='ignore')

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
    """复制用户必需的资源文件"""
    print("Copying essential user files...")

    project_root = Path(__file__).parent.parent
    dist_dir = project_root / "dist"

    if not dist_dir.exists():
        print("dist directory does not exist")
        return False

    # 创建用户使用说明
    create_user_guide(dist_dir)

    # 不复制开发文档目录，用户不需要
    print("  Skipped: Development documentation (not needed for end users)")

    return True

def create_user_guide(dist_dir):
    """创建中文用户使用指南"""
    print("Creating Chinese user guide...")

    # 获取exe文件大小
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

    print("  Created: 使用说明.md (Chinese user guide)")

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

    # 创建用户指南 (已在 copy_resources 中调用)

    print("\n" + "=" * 40)
    print("Build completed successfully!")
    print("Executable file is located in dist/ directory")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
