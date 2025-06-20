#!/usr/bin/env python3
"""
图标转换脚本
将PNG图标转换为ICO格式，支持多种尺寸
"""

import os
import sys
from PIL import Image

def convert_png_to_ico(png_path, ico_path):
    """
    将PNG图标转换为ICO格式
    
    Args:
        png_path: PNG文件路径
        ico_path: 输出ICO文件路径
    """
    try:
        # 打开PNG图片
        with Image.open(png_path) as img:
            print(f"原始图片尺寸: {img.size}")
            print(f"原始图片模式: {img.mode}")
            
            # 确保图片是RGBA模式（支持透明度）
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # 创建多种尺寸的图标
            # Windows ICO文件通常包含多种尺寸：16x16, 32x32, 48x48, 64x64, 128x128, 256x256
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            
            # 调整图片为正方形（如果不是的话）
            width, height = img.size
            if width != height:
                # 以较小的边为准，居中裁剪
                size = min(width, height)
                left = (width - size) // 2
                top = (height - size) // 2
                img = img.crop((left, top, left + size, top + size))
                print(f"裁剪为正方形: {img.size}")
            
            # 保存为ICO格式，包含多种尺寸
            img.save(ico_path, format='ICO', sizes=sizes)
            print(f"✅ 成功转换: {png_path} -> {ico_path}")
            print(f"包含尺寸: {sizes}")
            
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    # 获取项目根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # 定义文件路径
    png_path = os.path.join(project_root, "src", "assets", "icon.png")
    ico_path = os.path.join(project_root, "src", "assets", "icon.ico")
    backup_path = os.path.join(project_root, "src", "assets", "icon_backup.ico")
    
    print("🔄 开始转换图标...")
    print(f"PNG源文件: {png_path}")
    print(f"ICO目标文件: {ico_path}")
    
    # 检查PNG文件是否存在
    if not os.path.exists(png_path):
        print(f"❌ 错误: PNG文件不存在 {png_path}")
        return 1
    
    # 备份现有的ICO文件
    if os.path.exists(ico_path):
        if os.path.exists(backup_path):
            os.remove(backup_path)
        os.rename(ico_path, backup_path)
        print(f"📦 已备份现有ICO文件到: {backup_path}")
    
    # 转换PNG为ICO
    if convert_png_to_ico(png_path, ico_path):
        print("🎉 图标转换完成！")
        
        # 验证生成的ICO文件
        try:
            with Image.open(ico_path) as ico_img:
                print(f"✅ ICO文件验证成功，尺寸: {ico_img.size}")
        except Exception as e:
            print(f"⚠️  ICO文件验证失败: {e}")
        
        return 0
    else:
        print("❌ 图标转换失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())
