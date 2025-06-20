#!/usr/bin/env python3
"""
图标验证脚本
检查所有图标文件是否正确配置
"""

import os
import sys
from PIL import Image

def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (不存在)")
        return False

def check_image_file(file_path, description):
    """检查图片文件"""
    if not check_file_exists(file_path, description):
        return False
    
    try:
        with Image.open(file_path) as img:
            print(f"   📐 尺寸: {img.size}")
            print(f"   🎨 模式: {img.mode}")
            if hasattr(img, 'format'):
                print(f"   📄 格式: {img.format}")
        return True
    except Exception as e:
        print(f"   ❌ 图片文件损坏: {e}")
        return False

def check_code_references():
    """检查代码中的图标引用"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    files_to_check = [
        ("src/main.py", "主程序"),
        ("src/ui/main_window.py", "主窗口"),
        ("BadgePatternTool.spec", "打包配置")
    ]
    
    print("\n🔍 检查代码中的图标引用:")
    
    for file_path, description in files_to_check:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 检查图标相关的引用
            icon_refs = []
            if 'icon.ico' in content:
                icon_refs.append('icon.ico')
            if 'icon.png' in content:
                icon_refs.append('icon.png')
            if 'setWindowIcon' in content:
                icon_refs.append('setWindowIcon')
            if 'QIcon' in content:
                icon_refs.append('QIcon')
                
            if icon_refs:
                print(f"✅ {description}: {', '.join(icon_refs)}")
            else:
                print(f"⚠️  {description}: 未找到图标引用")
        else:
            print(f"❌ {description}: 文件不存在")

def main():
    """主函数"""
    print("🔍 BadgePatternTool 图标验证")
    print("=" * 50)
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(project_root, "src", "assets")
    
    print("📁 检查图标文件:")
    
    # 检查图标文件
    icon_files = [
        (os.path.join(assets_dir, "icon.png"), "PNG图标 (源文件)"),
        (os.path.join(assets_dir, "icon.ico"), "ICO图标 (主要)"),
        (os.path.join(assets_dir, "icon_backup.ico"), "ICO图标 (备份)")
    ]
    
    all_good = True
    for file_path, description in icon_files:
        if not check_image_file(file_path, description):
            all_good = False
        print()
    
    # 检查打包后的exe文件
    exe_path = os.path.join(project_root, "dist", "BadgePatternTool.exe")
    print("📦 检查打包文件:")
    if check_file_exists(exe_path, "可执行文件"):
        # 获取文件大小
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"   📏 文件大小: {size_mb:.1f} MB")
    print()
    
    # 检查代码引用
    check_code_references()
    
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 所有图标文件检查通过！")
        print("\n📋 使用说明:")
        print("1. 窗口图标: 程序运行时自动显示")
        print("2. 任务栏图标: 与窗口图标相同")
        print("3. exe文件图标: 在文件管理器中显示")
        print("4. 图标支持多种尺寸: 16x16 到 256x256")
    else:
        print("⚠️  发现问题，请检查上述错误信息")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
