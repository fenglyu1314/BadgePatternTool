#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试无UPX环境下的构建
模拟GitHub Actions环境，测试在没有UPX的情况下构建是否正常
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def backup_spec_file():
    """备份当前的.spec文件"""
    project_root = Path(__file__).parent.parent
    spec_file = project_root / "BadgePatternTool.spec"
    backup_file = project_root / "BadgePatternTool.spec.backup"
    
    if spec_file.exists():
        import shutil
        shutil.copy2(spec_file, backup_file)
        print("✅ .spec文件已备份")
        return True
    return False

def create_no_upx_spec():
    """创建禁用UPX的.spec文件用于测试"""
    project_root = Path(__file__).parent.parent
    spec_file = project_root / "BadgePatternTool.spec"
    
    if not spec_file.exists():
        print("❌ .spec文件不存在")
        return False
    
    # 读取当前.spec文件
    with open(spec_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 禁用UPX压缩
    content = content.replace('upx=True', 'upx=False')
    
    # 写入临时.spec文件
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 已创建禁用UPX的.spec文件")
    return True

def restore_spec_file():
    """恢复原始.spec文件"""
    project_root = Path(__file__).parent.parent
    spec_file = project_root / "BadgePatternTool.spec"
    backup_file = project_root / "BadgePatternTool.spec.backup"
    
    if backup_file.exists():
        import shutil
        shutil.copy2(backup_file, spec_file)
        backup_file.unlink()
        print("✅ .spec文件已恢复")
        return True
    return False

def test_build_without_upx():
    """测试无UPX环境下的构建"""
    print("🔍 测试无UPX环境下的构建")
    print("-" * 50)
    
    project_root = Path(__file__).parent.parent
    
    try:
        # 运行构建
        result = subprocess.run([
            sys.executable, "scripts/build.py"
        ], cwd=project_root, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.returncode == 0:
            print("✅ 构建成功")
            
            # 检查生成的文件
            exe_path = project_root / "dist" / "BadgePatternTool.exe"
            if exe_path.exists():
                file_size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"📦 生成文件大小: {file_size_mb:.1f} MB")
                
                if file_size_mb > 25 and file_size_mb < 35:
                    print("✅ 文件大小在预期范围内 (无UPX压缩)")
                else:
                    print(f"⚠️ 文件大小异常: {file_size_mb:.1f} MB")
                
                return True
            else:
                print("❌ 未找到生成的可执行文件")
                return False
        else:
            print("❌ 构建失败")
            print("错误输出:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 构建过程出错: {e}")
        return False

def check_upx_availability():
    """检查UPX是否可用"""
    print("\n🔍 检查UPX可用性")
    print("-" * 50)
    
    try:
        result = subprocess.run(['upx', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ UPX可用: {version_line}")
            return True
        else:
            print("❌ UPX不可用")
            return False
    except FileNotFoundError:
        print("❌ UPX未安装")
        return False

def simulate_github_actions_environment():
    """模拟GitHub Actions环境"""
    print("\n🔍 模拟GitHub Actions环境测试")
    print("-" * 50)
    
    # 检查Python版本
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(f"🐍 Python版本: {python_version}")
    
    if python_version == "3.11":
        print("✅ Python版本与GitHub Actions一致")
    else:
        print("⚠️ Python版本与GitHub Actions不一致 (推荐3.11)")
    
    # 检查关键依赖
    dependencies = [
        ('PySide6', 'PySide6'),
        ('Pillow', 'PIL'),
        ('reportlab', 'reportlab'),
        ('pyinstaller', 'PyInstaller')
    ]

    for dep_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {dep_name} 已安装")
        except ImportError:
            print(f"❌ {dep_name} 未安装")
    
    # 检查操作系统
    import platform
    os_name = platform.system()
    print(f"💻 操作系统: {os_name}")
    
    if os_name == "Windows":
        print("✅ 操作系统与GitHub Actions一致")
    else:
        print("⚠️ 操作系统与GitHub Actions不一致 (GitHub Actions使用Windows)")

def main():
    """主函数"""
    print("=" * 60)
    print("GitHub Actions兼容性构建测试")
    print("=" * 60)
    
    # 检查UPX可用性
    upx_available = check_upx_availability()
    
    # 模拟GitHub Actions环境
    simulate_github_actions_environment()
    
    # 备份.spec文件
    if not backup_spec_file():
        print("❌ 无法备份.spec文件")
        return False
    
    try:
        # 创建禁用UPX的.spec文件
        if not create_no_upx_spec():
            return False
        
        # 测试构建
        build_success = test_build_without_upx()
        
        # 总结
        print("\n" + "=" * 60)
        if build_success:
            print("✅ GitHub Actions兼容性测试通过")
            print("🚀 可以安全地在GitHub Actions中使用当前优化")
            if not upx_available:
                print("💡 本地未安装UPX，但GitHub Actions会自动安装")
        else:
            print("❌ GitHub Actions兼容性测试失败")
            print("⚠️ 需要修复问题后再使用自动构建")
        
        return build_success
        
    finally:
        # 恢复原始.spec文件
        restore_spec_file()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
