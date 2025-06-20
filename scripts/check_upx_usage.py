#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查UPX压缩使用情况
验证当前构建是否真正使用了UPX压缩
"""

import subprocess
import sys
from pathlib import Path

def check_upx_installed():
    """检查UPX是否安装"""
    print("🔍 检查UPX安装状态")
    print("-" * 40)
    
    try:
        result = subprocess.run(['upx', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ UPX已安装: {version_line}")
            return True
        else:
            print("❌ UPX命令执行失败")
            return False
    except FileNotFoundError:
        print("❌ UPX未安装")
        print("💡 这就是为什么包体大小没有进一步减少的原因")
        return False

def check_exe_compression():
    """检查可执行文件是否被压缩"""
    print("\n🔍 检查可执行文件压缩状态")
    print("-" * 40)
    
    project_root = Path(__file__).parent.parent
    exe_path = project_root / "dist" / "BadgePatternTool.exe"
    
    if not exe_path.exists():
        print("❌ 可执行文件不存在")
        return False
    
    file_size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"📦 当前文件大小: {file_size_mb:.1f} MB")
    
    # 尝试用UPX检查文件（如果UPX可用）
    try:
        result = subprocess.run(['upx', '-t', str(exe_path)], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 文件已被UPX压缩")
            return True
        else:
            print("❌ 文件未被UPX压缩")
            return False
    except FileNotFoundError:
        print("❌ 无法检查压缩状态 (UPX未安装)")
        return False

def estimate_compression_potential():
    """估算压缩潜力"""
    print("\n📊 UPX压缩潜力分析")
    print("-" * 40)
    
    current_size = 29.9  # MB
    
    print(f"📦 当前大小: {current_size} MB (无UPX压缩)")
    print(f"🎯 预期UPX压缩后: 24-26 MB")
    print(f"💾 预期额外节省: 3.9-5.9 MB")
    print(f"📈 总优化潜力: 6.8-8.8 MB (相比原始32.8MB)")
    print(f"📊 总优化比例: 20-27%")

def provide_upx_installation_guide():
    """提供UPX安装指南"""
    print("\n💡 UPX安装指南")
    print("-" * 40)
    
    print("Windows安装方法:")
    print("1. 直接下载:")
    print("   - 访问: https://upx.github.io/")
    print("   - 下载Windows版本")
    print("   - 解压到目录 (如 C:\\upx\\)")
    print("   - 添加到系统PATH环境变量")
    print()
    print("2. 使用包管理器:")
    print("   - Chocolatey: choco install upx")
    print("   - Scoop: scoop install upx")
    print()
    print("3. 验证安装:")
    print("   - 运行: upx --version")
    print("   - 应该显示版本信息")

def show_github_actions_advantage():
    """显示GitHub Actions的优势"""
    print("\n🚀 GitHub Actions优势")
    print("-" * 40)
    
    print("✅ GitHub Actions会自动安装UPX:")
    print("   - 无需手动安装UPX")
    print("   - 自动下载最新版本")
    print("   - 确保构建环境一致")
    print()
    print("✅ 预期GitHub Actions构建效果:")
    print("   - 自动UPX压缩: 24-26 MB")
    print("   - 比本地构建小: 3.9-5.9 MB")
    print("   - 总优化: 20-27%")

def main():
    """主函数"""
    print("=" * 60)
    print("UPX压缩使用情况检查")
    print("=" * 60)
    
    # 检查UPX安装
    upx_installed = check_upx_installed()
    
    # 检查文件压缩状态
    is_compressed = check_exe_compression()
    
    # 估算压缩潜力
    estimate_compression_potential()
    
    # 提供安装指南
    if not upx_installed:
        provide_upx_installation_guide()
    
    # 显示GitHub Actions优势
    show_github_actions_advantage()
    
    # 总结
    print("\n" + "=" * 60)
    if upx_installed and is_compressed:
        print("✅ UPX压缩正常工作")
    elif upx_installed and not is_compressed:
        print("⚠️ UPX已安装但文件未被压缩")
        print("💡 可能需要重新构建")
    else:
        print("❌ UPX未安装，当前构建未使用压缩")
        print("💡 安装UPX后可额外减少3.9-5.9MB")
        print("🚀 或者使用GitHub Actions自动构建获得压缩效果")
    
    return upx_installed and is_compressed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
