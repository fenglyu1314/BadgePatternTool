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
import time
from pathlib import Path

# 设置环境变量以支持UTF-8输出
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
    """验证和优化可执行文件"""
    print("验证可执行文件...")

    project_root = Path(__file__).parent.parent
    exe_path = project_root / "dist" / "BadgePatternTool.exe"

    if not exe_path.exists():
        print("未找到可执行文件")
        return False

    try:
        # 获取文件信息
        original_size = exe_path.stat().st_size
        size_mb = original_size / 1024 / 1024
        print(f"  文件大小: {size_mb:.1f} MB")

        # 验证文件完整性
        if size_mb < 20:
            print("  ⚠️ 警告: 文件大小异常小，可能构建不完整")
        elif size_mb > 80:
            print("  ⚠️ 警告: 文件大小较大，建议检查是否包含不必要的依赖")
        else:
            print("  ✅ 文件大小正常")

        # 检查文件是否可执行
        if exe_path.suffix.lower() == '.exe':
            print("  ✅ 文件格式正确")
        else:
            print("  ❌ 文件格式错误")
            return False

        print("可执行文件验证完成")
        return True

    except Exception as e:
        print(f"验证失败: {e}")
        return False



def main():
    """主构建函数"""
    start_time = time.time()

    print("BadgePatternTool 构建脚本")
    print("=" * 40)
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 尝试获取版本信息
    try:
        project_root = Path(__file__).parent.parent
        sys.path.insert(0, str(project_root / "src"))
        from common.constants import APP_VERSION
        print(f"项目版本: {APP_VERSION}")
    except ImportError:
        print("项目版本: 无法获取")

    print()

    # 检查依赖
    if not check_dependencies():
        return False

    # 清理构建目录
    clean_build_dirs()

    # 构建可执行文件
    if not build_executable():
        return False

    # 验证可执行文件
    if not optimize_executable():
        return False

    # 复制必要文件 (CHANGELOG.md)
    if not copy_resources():
        return False

    # 计算构建时间
    end_time = time.time()
    build_time = end_time - start_time

    print("\n" + "=" * 40)
    print("🎉 构建完成！")
    print(f"构建耗时: {build_time:.1f} 秒")
    print("可执行文件位于 dist/ 目录")

    # 显示最终构建产物
    dist_dir = Path(__file__).parent.parent / "dist"
    if dist_dir.exists():
        print("\n构建产物:")
        for file in dist_dir.iterdir():
            if file.is_file():
                size_mb = file.stat().st_size / 1024 / 1024
                print(f"  - {file.name} ({size_mb:.1f} MB)")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
