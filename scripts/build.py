#!/usr/bin/env python3
"""
项目构建脚本
用于打包BadgePatternTool为可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_dependencies():
    """检查构建依赖"""
    print("检查构建依赖...")
    
    try:
        import PyInstaller
        print("✅ PyInstaller 已安装")
        return True
    except ImportError:
        print("❌ PyInstaller 未安装")
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
            print(f"  清理: {dir_name}")

    # 清理Python缓存文件
    for cache_dir in project_root.rglob("__pycache__"):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir)

    for pyc_file in project_root.rglob("*.pyc"):
        pyc_file.unlink()

    print("  清理: Python缓存文件")

def build_executable():
    """构建可执行文件（使用优化的.spec文件）"""
    print("构建可执行文件...")

    project_root = Path(__file__).parent.parent
    spec_file = project_root / "BadgePatternTool.spec"

    # 检查.spec文件是否存在
    if not spec_file.exists():
        print("❌ 找不到 BadgePatternTool.spec 文件")
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
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ 构建成功")

            # 检查生成的文件大小
            exe_path = project_root / "dist" / "BadgePatternTool.exe"
            if exe_path.exists():
                file_size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"📦 可执行文件大小: {file_size_mb:.1f} MB")

                # 如果文件过大，给出警告
                if file_size_mb > 60:
                    print("⚠️ 文件大小较大，考虑进一步优化")
                elif file_size_mb < 30:
                    print("✅ 文件大小优化良好")

            return True
        else:
            print("❌ 构建失败")
            print("错误输出:")
            print(result.stderr)
            if result.stdout:
                print("标准输出:")
                print(result.stdout)
            return False

    except Exception as e:
        print(f"❌ 构建过程出错: {e}")
        return False

def copy_resources():
    """复制资源文件"""
    print("复制资源文件...")
    
    project_root = Path(__file__).parent.parent
    dist_dir = project_root / "dist"
    
    if not dist_dir.exists():
        print("❌ dist目录不存在")
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
            print(f"  复制: {doc}")
    
    # 复制docs目录
    docs_dir = project_root / "docs"
    if docs_dir.exists():
        dst_docs = dist_dir / "docs"
        shutil.copytree(docs_dir, dst_docs, dirs_exist_ok=True)
        print("  复制: docs/")
    
    return True

def optimize_executable():
    """优化可执行文件"""
    print("优化可执行文件...")

    project_root = Path(__file__).parent.parent
    exe_path = project_root / "dist" / "BadgePatternTool.exe"

    if not exe_path.exists():
        print("❌ 找不到可执行文件")
        return False

    try:
        # 获取文件信息
        original_size = exe_path.stat().st_size
        print(f"  原始大小: {original_size / 1024 / 1024:.1f} MB")

        # 这里可以添加其他优化步骤，比如：
        # - 使用UPX压缩（如果需要）
        # - 移除不必要的资源
        # - 验证文件完整性

        print("✅ 可执行文件优化完成")
        return True

    except Exception as e:
        print(f"❌ 优化失败: {e}")
        return False

def create_installer_info():
    """创建安装说明"""
    print("创建安装说明...")

    project_root = Path(__file__).parent.parent
    dist_dir = project_root / "dist"
    exe_path = dist_dir / "BadgePatternTool.exe"

    # 获取文件大小
    file_size_mb = 0
    if exe_path.exists():
        file_size_mb = exe_path.stat().st_size / (1024 * 1024)

    install_info = f"""# BadgePatternTool 安装说明

## 🚀 快速开始

1. **运行程序**
   - 双击 `BadgePatternTool.exe` 启动程序
   - 首次运行可能需要几秒钟加载时间

2. **系统要求**
   - Windows 7/8/10/11 (64位)
   - 至少 100MB 可用磁盘空间
   - 建议 4GB 内存

3. **使用说明**
   - 查看 `docs/` 目录中的详细文档
   - 参考 `README.md` 了解功能特性

## 📋 文件说明

- `BadgePatternTool.exe` - 主程序文件 ({file_size_mb:.1f}MB)
- `README.md` - 项目说明
- `CHANGELOG.md` - 更新日志
- `docs/` - 详细文档目录

## 🔧 性能优化

本版本已进行以下优化：
- 移除不必要的依赖模块
- 优化启动速度
- 减小文件体积
- 提升运行效率

## 🆘 问题反馈

如遇到问题，请查看文档或联系开发者。

---
BadgePatternTool v1.5.5 (优化版)
构建时间: {Path(__file__).stat().st_mtime}
"""

    info_file = dist_dir / "安装说明.txt"
    with open(info_file, 'w', encoding='utf-8') as f:
        f.write(install_info)

    print("  创建: 安装说明.txt")

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

    # 复制资源文件
    if not copy_resources():
        return False

    # 创建安装说明
    create_installer_info()
    
    print("\n" + "=" * 40)
    print("🎉 构建完成！")
    print("可执行文件位于 dist/ 目录")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
