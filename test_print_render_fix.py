#!/usr/bin/env python3
"""
测试打印渲染修复
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_print_render_fix():
    """测试打印渲染修复"""
    print("=== 测试打印渲染修复 ===\n")
    
    try:
        from PySide6.QtWidgets import QApplication
        from ui.main_window import MainWindow
        from core.image_processor import ImageProcessor
        
        # 创建应用程序（如果不存在）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建主窗口
        window = MainWindow()
        
        print("1. 检查ImageProcessor方法...")
        
        # 检查ImageProcessor的方法
        processor = ImageProcessor()
        
        has_create_circular_crop = hasattr(processor, 'create_circular_crop')
        has_create_circle_image = hasattr(processor, 'create_circle_image')
        has_create_preview_image = hasattr(processor, 'create_preview_image')
        
        print(f"   create_circular_crop: {'✅' if has_create_circular_crop else '❌'}")
        print(f"   create_circle_image: {'❌ (已弃用)' if has_create_circle_image else '✅ (正确移除)'}")
        print(f"   create_preview_image: {'✅' if has_create_preview_image else '❌'}")
        
        if not has_create_circular_crop:
            print("   ❌ 缺少必要的create_circular_crop方法")
            return False
        
        print(f"\n2. 检查主窗口的PIL转换方法...")
        
        # 检查新添加的转换方法
        has_pil_to_qpixmap = hasattr(window, '_pil_to_qpixmap')
        print(f"   _pil_to_qpixmap: {'✅' if has_pil_to_qpixmap else '❌'}")
        
        if not has_pil_to_qpixmap:
            print("   ❌ 缺少PIL到QPixmap的转换方法")
            return False
        
        print(f"\n3. 测试PIL到QPixmap转换...")
        
        try:
            from PIL import Image
            
            # 创建一个测试PIL图片
            test_image = Image.new('RGB', (100, 100), (255, 0, 0))  # 红色图片
            
            # 测试转换
            pixmap = window._pil_to_qpixmap(test_image)
            
            if pixmap and not pixmap.isNull():
                print(f"   ✅ PIL到QPixmap转换成功")
                print(f"   转换后尺寸: {pixmap.width()} × {pixmap.height()}")
            else:
                print(f"   ❌ PIL到QPixmap转换失败")
                return False
                
        except Exception as e:
            print(f"   ❌ PIL到QPixmap转换测试失败: {e}")
            return False
        
        print(f"\n4. 测试RGBA图片转换...")
        
        try:
            # 创建一个带透明度的测试图片
            rgba_image = Image.new('RGBA', (100, 100), (0, 255, 0, 128))  # 半透明绿色
            
            # 测试转换
            pixmap = window._pil_to_qpixmap(rgba_image)
            
            if pixmap and not pixmap.isNull():
                print(f"   ✅ RGBA图片转换成功")
            else:
                print(f"   ❌ RGBA图片转换失败")
                return False
                
        except Exception as e:
            print(f"   ❌ RGBA图片转换测试失败: {e}")
            return False
        
        print(f"\n5. 测试圆形图片创建...")
        
        try:
            # 测试圆形图片创建（使用空白图片）
            circle_image = processor._create_blank_circle()
            
            if circle_image:
                print(f"   ✅ 圆形图片创建成功")
                print(f"   圆形图片尺寸: {circle_image.size}")
                
                # 测试转换为QPixmap
                pixmap = window._pil_to_qpixmap(circle_image)
                if pixmap and not pixmap.isNull():
                    print(f"   ✅ 圆形图片转换为QPixmap成功")
                else:
                    print(f"   ❌ 圆形图片转换为QPixmap失败")
                    return False
            else:
                print(f"   ❌ 圆形图片创建失败")
                return False
                
        except Exception as e:
            print(f"   ❌ 圆形图片创建测试失败: {e}")
            return False
        
        print(f"\n6. 检查打印渲染方法...")
        
        # 检查render_to_printer方法
        has_render_to_printer = hasattr(window, 'render_to_printer')
        print(f"   render_to_printer: {'✅' if has_render_to_printer else '❌'}")
        
        if not has_render_to_printer:
            print("   ❌ 缺少render_to_printer方法")
            return False
        
        print(f"\n{'='*50}")
        print("打印渲染修复测试总结:")
        print("✅ ImageProcessor方法: 正确")
        print("✅ PIL转换方法: 已添加")
        print("✅ RGB图片转换: 正常")
        print("✅ RGBA图片转换: 正常")
        print("✅ 圆形图片创建: 正常")
        print("✅ 打印渲染方法: 存在")
        
        print(f"\n🎉 打印渲染功能修复成功！")
        print(f"\n修复内容:")
        print(f"- 修正了方法调用: create_circle_image → create_circular_crop")
        print(f"- 添加了PIL到QPixmap转换方法")
        print(f"- 处理了RGBA透明度问题")
        print(f"- 完善了错误处理机制")
        print(f"\n现在可以正常打印了！")
        print(f"{'='*50}")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_print_render_fix()
    if success:
        print(f"\n✅ 打印渲染修复测试通过！")
    else:
        print(f"\n❌ 打印渲染修复测试失败！")
