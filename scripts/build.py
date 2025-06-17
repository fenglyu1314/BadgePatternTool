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
    dirs_to_clean = ["build", "dist", "__pycache__"]
    
    for dir_name in dirs_to_clean:
        dir_path = project_root / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  清理: {dir_name}")
    
    # 清理.spec文件
    for spec_file in project_root.glob("*.spec"):
        spec_file.unlink()
        print(f"  清理: {spec_file.name}")

def build_executable():
    """构建可执行文件"""
    print("构建可执行文件...")
    
    project_root = Path(__file__).parent.parent
    main_script = project_root / "src" / "main.py"
    
    if not main_script.exists():
        print("❌ 找不到主脚本文件")
        return False
    
    # PyInstaller命令参数
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包成单个文件
        "--windowed",                   # Windows下隐藏控制台
        "--name=BadgePatternTool",      # 可执行文件名
        "--icon=src/assets/icon.ico",   # 图标（如果存在）
        "--add-data=src;src",           # 添加源代码目录
        "--hidden-import=PIL",          # 隐式导入
        "--hidden-import=reportlab",
        "--hidden-import=PySide6",
        str(main_script)
    ]
    
    try:
        # 检查图标文件是否存在
        icon_path = project_root / "src" / "assets" / "icon.ico"
        if not icon_path.exists():
            # 移除图标参数
            cmd = [arg for arg in cmd if not arg.startswith("--icon")]
        
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 构建成功")
            return True
        else:
            print("❌ 构建失败")
            print("错误输出:")
            print(result.stderr)
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

def create_installer_info():
    """创建安装说明"""
    print("创建安装说明...")
    
    project_root = Path(__file__).parent.parent
    dist_dir = project_root / "dist"
    
    install_info = """# BadgePatternTool 安装说明

## 🚀 快速开始

1. **运行程序**
   - 双击 `BadgePatternTool.exe` 启动程序
   - 首次运行可能需要几秒钟加载时间

2. **系统要求**
   - Windows 7/8/10/11
   - 至少 100MB 可用磁盘空间
   - 建议 4GB 内存

3. **使用说明**
   - 查看 `docs/` 目录中的详细文档
   - 参考 `README.md` 了解功能特性

## 📋 文件说明

- `BadgePatternTool.exe` - 主程序文件
- `README.md` - 项目说明
- `CHANGELOG.md` - 更新日志
- `docs/` - 详细文档目录

## 🆘 问题反馈

如遇到问题，请查看文档或联系开发者。

---
BadgePatternTool v1.0.0
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
