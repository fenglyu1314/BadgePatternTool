#!/usr/bin/env python3
"""
图标创建脚本
为BadgePatternTool创建默认图标
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """检查依赖"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        return True
    except ImportError:
        print("❌ 缺少Pillow库，正在安装...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
            print("✅ Pillow安装成功")
            return True
        except subprocess.CalledProcessError:
            print("❌ Pillow安装失败，请手动安装: pip install Pillow")
            return False

def create_badge_icon():
    """创建徽章工具图标"""
    from PIL import Image, ImageDraw, ImageFont
    
    print("正在创建徽章工具图标...")
    
    # 创建256x256的图像
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制外圆环（深蓝色）
    margin = 16
    outer_circle = [margin, margin, size-margin, size-margin]
    draw.ellipse(outer_circle, fill=(41, 128, 185, 255), outline=(52, 73, 94, 255), width=6)
    
    # 绘制内圆（浅蓝色）
    inner_margin = 32
    inner_circle = [inner_margin, inner_margin, size-inner_margin, size-inner_margin]
    draw.ellipse(inner_circle, fill=(52, 152, 219, 255))
    
    # 绘制字母"B"
    try:
        # 尝试使用系统字体
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",  # Windows
            "C:/Windows/Fonts/calibri.ttf",  # Windows
            "/System/Library/Fonts/Arial.ttf",  # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Linux
        ]
        
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, 120)
                break
        
        if font is None:
            font = ImageFont.load_default()
            print("⚠️ 使用默认字体，效果可能不佳")
    except:
        font = ImageFont.load_default()
        print("⚠️ 字体加载失败，使用默认字体")
    
    text = "B"
    
    # 计算文字位置（居中）
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2 - 10  # 稍微向上偏移
    
    # 绘制文字阴影
    shadow_offset = 3
    draw.text((text_x + shadow_offset, text_y + shadow_offset), text, 
              fill=(0, 0, 0, 100), font=font)
    
    # 绘制主文字（白色）
    draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
    
    # 添加小装饰元素（圆点）
    dot_size = 8
    dot_positions = [
        (size//2 - 60, size//2 + 60),  # 左下
        (size//2 + 60, size//2 + 60),  # 右下
        (size//2, size//2 - 70),       # 上方
    ]
    
    for x, y in dot_positions:
        dot_bbox = [x-dot_size//2, y-dot_size//2, x+dot_size//2, y+dot_size//2]
        draw.ellipse(dot_bbox, fill=(255, 255, 255, 200))
    
    return img

def create_simple_icon():
    """创建简单图标（备用方案）"""
    from PIL import Image, ImageDraw
    
    print("正在创建简单图标...")
    
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制简单的圆形
    margin = 20
    circle_bbox = [margin, margin, size-margin, size-margin]
    draw.ellipse(circle_bbox, fill=(52, 152, 219, 255), outline=(41, 128, 185, 255), width=8)
    
    # 绘制简单的"B"形状
    center_x, center_y = size//2, size//2
    
    # 垂直线
    line_width = 20
    draw.rectangle([center_x-40, center_y-60, center_x-40+line_width, center_y+60], 
                   fill=(255, 255, 255, 255))
    
    # 上半圆
    draw.arc([center_x-40, center_y-60, center_x+20, center_y], 
             start=270, end=90, fill=(255, 255, 255, 255), width=line_width)
    
    # 下半圆
    draw.arc([center_x-40, center_y, center_x+20, center_y+60], 
             start=270, end=90, fill=(255, 255, 255, 255), width=line_width)
    
    return img

def save_icon(img, output_path):
    """保存图标文件"""
    try:
        # 创建多种尺寸
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # 保存为ICO格式
        img.save(output_path, format='ICO', sizes=sizes)
        print(f"✅ 图标已保存: {output_path}")
        
        # 验证文件
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"   文件大小: {file_size} 字节")
            return True
        else:
            print("❌ 图标文件保存失败")
            return False
            
    except Exception as e:
        print(f"❌ 保存图标时出错: {e}")
        return False

def main():
    """主函数"""
    print("BadgePatternTool 图标创建工具")
    print("=" * 40)
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 确保assets目录存在
    project_root = Path(__file__).parent.parent
    assets_dir = project_root / "src" / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = assets_dir / "icon.ico"
    
    # 如果图标已存在，询问是否覆盖
    if output_path.exists():
        response = input(f"图标文件已存在: {output_path}\n是否覆盖? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("操作已取消")
            return True
    
    try:
        # 尝试创建精美图标
        img = create_badge_icon()
        
        # 保存图标
        if save_icon(img, output_path):
            print("\n" + "=" * 40)
            print("🎉 图标创建成功！")
            print(f"图标位置: {output_path}")
            print("\n下一步:")
            print("1. 运行 'python scripts/build.py' 重新打包程序")
            print("2. 或运行 'build.bat' 使用批处理脚本")
            print("3. 新的exe文件将包含自定义图标")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ 创建图标时出错: {e}")
        print("尝试创建简单图标...")
        
        try:
            # 备用方案：创建简单图标
            img = create_simple_icon()
            return save_icon(img, output_path)
        except Exception as e2:
            print(f"❌ 创建简单图标也失败: {e2}")
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
