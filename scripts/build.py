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

# Set environment variable to support UTF-8 output
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def check_dependencies():
    """检查构建依赖"""
    print("检查构建依赖...")

    try:
        import PyInstaller
        print("PyInstaller 已安装")
        return True
    except ImportError:
        print("PyInstaller 未安装")
        print("请运行: pip install pyinstaller")
        return False

def clean_build_dirs():
    """清理构建目录"""
    print("清理构建目录...")

    project_root = Path(__file__).parent.parent
    dirs_to_clean = ["build", "dist"]

    for dir_name in dirs_to_clean:
        dir_path = project_root / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  已清理: {dir_name}")

    # 清理Python缓存文件
    for cache_dir in project_root.rglob("__pycache__"):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir)

    for pyc_file in project_root.rglob("*.pyc"):
        pyc_file.unlink()

    print("  已清理: Python缓存文件")

def build_executable():
    """构建可执行文件（使用优化的.spec文件）"""
    print("构建可执行文件...")

    project_root = Path(__file__).parent.parent
    spec_file = project_root / "BadgePatternTool.spec"

    # 检查.spec文件是否存在
    if not spec_file.exists():
        print("未找到 BadgePatternTool.spec 文件")
        return False

    try:
        # 使用.spec文件构建
        cmd = [
            "pyinstaller",
            "--clean",                  # 清理临时文件
            "--noconfirm",             # 不询问覆盖
            str(spec_file)
        ]

        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, encoding='utf-8', errors='ignore')

        if result.returncode == 0:
            print("构建成功")

            # 检查生成的文件大小
            exe_path = project_root / "dist" / "BadgePatternTool.exe"
            if exe_path.exists():
                file_size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"可执行文件大小: {file_size_mb:.1f} MB")

                # 如果文件过大，给出警告
                if file_size_mb > 60:
                    print("文件大小较大，建议进一步优化")
                elif file_size_mb < 30:
                    print("文件大小优化良好")

            return True
        else:
            print("构建失败")
            print("错误输出:")
            print(result.stderr)
            if result.stdout:
                print("标准输出:")
                print(result.stdout)
            return False

    except Exception as e:
        print(f"构建过程错误: {e}")
        return False

def copy_resources():
    """复制用户必需的资源文件"""
    print("复制必要文件...")

    project_root = Path(__file__).parent.parent
    dist_dir = project_root / "dist"

    if not dist_dir.exists():
        print("dist目录不存在")
        return False

    # 直接从项目复制CHANGELOG.md
    changelog_src = project_root / "CHANGELOG.md"
    if changelog_src.exists():
        changelog_dst = dist_dir / "CHANGELOG.md"
        shutil.copy2(changelog_src, changelog_dst)
        print("  已复制: CHANGELOG.md")
    else:
        print("  警告: 未找到 CHANGELOG.md")

    return True



def optimize_executable():
    """优化可执行文件"""
    print("优化可执行文件...")

    project_root = Path(__file__).parent.parent
    exe_path = project_root / "dist" / "BadgePatternTool.exe"

    if not exe_path.exists():
        print("未找到可执行文件")
        return False

    try:
        # 获取文件信息
        original_size = exe_path.stat().st_size
        print(f"  原始大小: {original_size / 1024 / 1024:.1f} MB")

        # 这里可以添加其他优化步骤，比如：
        # - 使用UPX压缩（如果需要）
        # - 移除不必要的资源
        # - 验证文件完整性

        print("可执行文件优化完成")
        return True

    except Exception as e:
        print(f"优化失败: {e}")
        return False



def main():
    """主构建函数"""
    print("BadgePatternTool 构建脚本")
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

    # 复制必要文件 (CHANGELOG.md)
    if not copy_resources():
        return False

    print("\n" + "=" * 40)
    print("构建完成！")
    print("可执行文件位于 dist/ 目录")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
