#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度包体分析工具
分析当前30.3MB包体的进一步优化空间
"""

import os
import sys
import subprocess
from pathlib import Path

def analyze_current_optimizations():
    """分析当前已应用的优化"""
    print("=" * 60)
    print("深度包体优化分析")
    print("=" * 60)
    
    project_root = Path(__file__).parent.parent
    exe_path = project_root / "dist" / "BadgePatternTool.exe"
    
    if exe_path.exists():
        file_size_mb = exe_path.stat().st_size / (1024 * 1024)
        original_size = 32.8
        total_saved = original_size - file_size_mb
        print(f"📦 当前大小: {file_size_mb:.1f} MB")
        print(f"📉 已优化: {total_saved:.1f} MB (从{original_size}MB)")
        print(f"📊 优化比例: {(total_saved/original_size)*100:.1f}%")
        print()
    
    return True

def analyze_further_optimizations():
    """分析进一步优化空间"""
    print("🔍 进一步优化分析:")
    print("-" * 40)
    
    optimizations = [
        {
            "name": "更激进的Qt6排除",
            "description": "排除Qt6PrintSupport的部分组件，只保留核心打印功能",
            "estimated_saving": "1.5-2.0 MB",
            "risk": "中等 - 可能影响打印功能"
        },
        {
            "name": "ReportLab模块精简",
            "description": "只保留PDF生成核心功能，排除图表、表格等高级功能",
            "estimated_saving": "0.8-1.2 MB", 
            "risk": "低 - 我们只用基础PDF功能"
        },
        {
            "name": "PIL深度优化",
            "description": "排除更多图像滤镜、变换和高级处理功能",
            "estimated_saving": "0.5-1.0 MB",
            "risk": "低 - 我们只用基础图像操作"
        },
        {
            "name": "Python标准库深度清理",
            "description": "排除更多编码、压缩、加密相关模块",
            "estimated_saving": "0.8-1.5 MB",
            "risk": "中等 - 需要仔细测试依赖"
        },
        {
            "name": "Windows DLL优化",
            "description": "排除更多系统DLL，使用静态链接",
            "estimated_saving": "0.3-0.8 MB",
            "risk": "高 - 可能影响兼容性"
        },
        {
            "name": "UPX高级压缩",
            "description": "使用更高压缩级别和优化参数",
            "estimated_saving": "3.0-5.0 MB",
            "risk": "中等 - 可能影响启动速度"
        }
    ]
    
    total_min = 0
    total_max = 0
    
    for i, opt in enumerate(optimizations, 1):
        saving_range = opt["estimated_saving"].replace("MB", "").split("-")
        min_save = float(saving_range[0])
        max_save = float(saving_range[1])
        total_min += min_save
        total_max += max_save
        
        print(f"  {i}. {opt['name']}")
        print(f"     💾 预期节省: {opt['estimated_saving']}")
        print(f"     ⚠️ 风险等级: {opt['risk']}")
        print(f"     📝 说明: {opt['description']}")
        print()
    
    current_size = 30.3
    min_final = current_size - total_max
    max_final = current_size - total_min
    
    print(f"🎯 总预期节省: {total_min:.1f} - {total_max:.1f} MB")
    print(f"📊 预期最终大小: {min_final:.1f} - {max_final:.1f} MB")
    
    if min_final <= 20:
        print("✅ 有望达到20MB以下")
    elif min_final <= 25:
        print("✅ 可以达到25MB以下")
    else:
        print("⚠️ 可能仍超过25MB")

def recommend_next_steps():
    """推荐下一步优化步骤"""
    print("\n" + "=" * 40)
    print("🚀 推荐优化顺序:")
    print("=" * 40)
    
    steps = [
        "1. 【低风险】ReportLab模块精简 - 预期节省1MB",
        "2. 【低风险】PIL深度优化 - 预期节省0.8MB", 
        "3. 【中风险】UPX高级压缩 - 预期节省4MB",
        "4. 【中风险】Python标准库深度清理 - 预期节省1.2MB",
        "5. 【中风险】Qt6PrintSupport精简 - 预期节省1.8MB",
        "6. 【高风险】Windows DLL优化 - 预期节省0.5MB"
    ]
    
    for step in steps:
        print(f"  {step}")
    
    print("\n💡 建议策略:")
    print("  - 先执行低风险优化，确保功能稳定")
    print("  - 逐步测试中风险优化，验证兼容性")
    print("  - 高风险优化需要充分测试")
    print("  - 目标：达到22-25MB范围")

def check_upx_availability():
    """检查UPX是否可用"""
    print("\n" + "=" * 40)
    print("🔧 UPX压缩工具检查:")
    print("=" * 40)
    
    try:
        result = subprocess.run(['upx', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"  ✅ UPX已安装: {version_line}")
            print("  💡 可以使用更高级的UPX压缩设置")
        else:
            print("  ❌ UPX未正确安装")
    except FileNotFoundError:
        print("  ❌ UPX未安装")
        print("  💡 建议安装UPX以获得更好的压缩效果")
        print("  📥 下载地址: https://upx.github.io/")

def main():
    """主函数"""
    analyze_current_optimizations()
    analyze_further_optimizations()
    recommend_next_steps()
    check_upx_availability()
    
    print("\n" + "=" * 60)
    print("分析完成！建议按推荐顺序逐步优化。")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
