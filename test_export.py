"""
导出功能测试脚本
用于验证PDF和图片导出功能是否正常工作
"""

import sys
import os
from PIL import Image

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.file_handler import ImageItem
from core.export_manager import ExportManager
from utils.config import *

def create_test_image(filename, size=(800, 600), color=(255, 0, 0)):
    """创建测试图片"""
    img = Image.new('RGB', size, color)
    img.save(filename, 'PNG')
    print(f"创建测试图片: {filename}")

def test_export_functions():
    """测试导出功能"""
    print("=" * 50)
    print("BadgePatternTool 导出功能测试")
    print("=" * 50)
    
    # 创建测试图片
    test_images = []
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    
    for i, color in enumerate(colors):
        filename = f"test_image_{i+1}.png"
        create_test_image(filename, (600, 600), color)
        test_images.append(filename)
    
    # 创建图片项目
    image_items = []
    for img_path in test_images:
        if os.path.exists(img_path):
            item = ImageItem(img_path)
            # 设置为已处理状态
            item.scale = 1.2
            item.offset_x = 0
            item.offset_y = 0
            item.rotation = 0
            item.is_processed = True
            image_items.append(item)
    
    print(f"\n创建了 {len(image_items)} 个测试图片项目")
    
    # 创建导出管理器
    export_manager = ExportManager()
    
    # 测试验证功能
    print("\n1. 测试导出设置验证...")
    is_valid, error_msg = export_manager.validate_export_settings(image_items, "test_output.pdf")
    if is_valid:
        print("✅ 导出设置验证通过")
    else:
        print(f"❌ 导出设置验证失败: {error_msg}")
        return
    
    # 测试PDF导出
    print("\n2. 测试PDF导出...")
    try:
        success, count = export_manager.export_to_pdf(
            image_items, "test_output.pdf", "grid", 5, 10
        )
        if success:
            print(f"✅ PDF导出成功，处理了 {count} 张图片")
            if os.path.exists("test_output.pdf"):
                file_size = os.path.getsize("test_output.pdf") / 1024
                print(f"   文件大小: {file_size:.1f} KB")
            else:
                print("❌ PDF文件未生成")
        else:
            print("❌ PDF导出失败")
    except Exception as e:
        print(f"❌ PDF导出异常: {e}")
    
    # 测试PNG导出
    print("\n3. 测试PNG导出...")
    try:
        success, count = export_manager.export_to_image(
            image_items, "test_output.png", "PNG", "grid", 5, 10
        )
        if success:
            print(f"✅ PNG导出成功，处理了 {count} 张图片")
            if os.path.exists("test_output.png"):
                with Image.open("test_output.png") as img:
                    print(f"   图片尺寸: {img.size}")
                    print(f"   图片模式: {img.mode}")
        else:
            print("❌ PNG导出失败")
    except Exception as e:
        print(f"❌ PNG导出异常: {e}")
    
    # 测试JPG导出
    print("\n4. 测试JPG导出...")
    try:
        success, count = export_manager.export_to_image(
            image_items, "test_output.jpg", "JPEG", "compact", 8, 15
        )
        if success:
            print(f"✅ JPG导出成功，处理了 {count} 张图片")
            if os.path.exists("test_output.jpg"):
                with Image.open("test_output.jpg") as img:
                    print(f"   图片尺寸: {img.size}")
                    print(f"   图片模式: {img.mode}")
        else:
            print("❌ JPG导出失败")
    except Exception as e:
        print(f"❌ JPG导出异常: {e}")
    
    # 测试建议文件名生成
    print("\n5. 测试文件名生成...")
    pdf_name = export_manager.get_suggested_filename("PDF", "grid")
    png_name = export_manager.get_suggested_filename("PNG", "compact")
    print(f"   PDF建议文件名: {pdf_name}")
    print(f"   PNG建议文件名: {png_name}")
    
    # 清理测试文件
    print("\n6. 清理测试文件...")
    cleanup_files = test_images + ["test_output.pdf", "test_output.png", "test_output.jpg"]
    for filename in cleanup_files:
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print(f"   删除: {filename}")
            except Exception as e:
                print(f"   删除失败 {filename}: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    test_export_functions()
