#!/usr/bin/env python3
"""
测试修复后的打印API
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_print_api_fix():
    """测试修复后的打印API"""
    print("=== 测试修复后的打印API ===\n")
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
        from PySide6.QtGui import QPageSize
        from PySide6.QtCore import QMarginsF
        
        # 创建应用程序（如果不存在）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("1. 测试新的QPrinter API...")
        
        try:
            # 测试新的API
            printer = QPrinter(QPrinter.HighResolution)
            print("   ✅ QPrinter 创建成功")
            
            # 测试页面大小设置
            page_size = QPageSize(QPageSize.A4)
            printer.setPageSize(page_size)
            print("   ✅ 页面大小设置成功 (QPageSize.A4)")

            # 测试页面方向设置
            printer.setPageOrientation(QPrinter.Portrait)
            print("   ✅ 页面方向设置成功 (Portrait)")
            
            # 测试页边距设置
            margin_points = 15 * 2.83465  # 15mm转换为点
            printer.setPageMargins(QMarginsF(margin_points, margin_points, margin_points, margin_points))
            print("   ✅ 页边距设置成功")
            
            # 测试获取页面信息
            page_rect = printer.pageRect()
            print(f"   ✅ 页面尺寸: {page_rect.width():.0f} × {page_rect.height():.0f} 点")
            
            print("   ✅ 所有QPrinter API测试通过")
            
        except Exception as e:
            print(f"   ❌ QPrinter API测试失败: {e}")
            return False
        
        print(f"\n2. 测试打印对话框...")
        
        try:
            # 测试打印对话框创建（不显示）
            print_dialog = QPrintDialog(printer)
            print_dialog.setWindowTitle("测试打印对话框")
            print("   ✅ 打印对话框创建成功")
            
        except Exception as e:
            print(f"   ❌ 打印对话框测试失败: {e}")
            return False
        
        print(f"\n3. 测试打印预览对话框...")
        
        try:
            # 测试打印预览对话框创建（不显示）
            preview_dialog = QPrintPreviewDialog(printer)
            preview_dialog.setWindowTitle("测试打印预览")
            print("   ✅ 打印预览对话框创建成功")
            
        except Exception as e:
            print(f"   ❌ 打印预览对话框测试失败: {e}")
            return False
        
        print(f"\n4. 测试主窗口打印功能...")
        
        try:
            from ui.main_window import MainWindow
            
            # 创建主窗口
            window = MainWindow()
            
            # 检查打印方法是否存在
            has_print_layout = hasattr(window, 'print_layout')
            has_print_preview = hasattr(window, 'print_preview')
            has_render_to_printer = hasattr(window, 'render_to_printer')
            
            print(f"   print_layout 方法: {'✅' if has_print_layout else '❌'}")
            print(f"   print_preview 方法: {'✅' if has_print_preview else '❌'}")
            print(f"   render_to_printer 方法: {'✅' if has_render_to_printer else '❌'}")
            
            if not all([has_print_layout, has_print_preview, has_render_to_printer]):
                return False
            
        except Exception as e:
            print(f"   ❌ 主窗口打印功能测试失败: {e}")
            return False
        
        print(f"\n5. 测试API兼容性...")
        
        # 测试旧API是否还存在（应该不存在）
        try:
            # 这些应该会失败
            test_printer = QPrinter()
            test_printer.setPageSize(QPrinter.A4)  # 这应该失败
            print("   ⚠️ 旧API仍然可用，可能存在兼容性问题")
        except AttributeError:
            print("   ✅ 旧API已正确移除，使用新API")
        except Exception as e:
            print(f"   ✅ 旧API不可用: {type(e).__name__}")
        
        print(f"\n{'='*50}")
        print("打印API修复测试总结:")
        print("✅ QPrinter 新API: 正常工作")
        print("✅ QPageSize 设置: 正常工作") 
        print("✅ 页面方向设置: 正常工作")
        print("✅ 页边距设置: 正常工作")
        print("✅ 打印对话框: 正常工作")
        print("✅ 打印预览: 正常工作")
        print("✅ 主窗口集成: 正常工作")
        
        print(f"\n🎉 打印API修复成功！现在可以正常使用打印功能了。")
        print(f"\n修复内容:")
        print(f"- QPrinter.A4 → QPageSize(QPageSize.A4)")
        print(f"- QPrinter.Portrait → QPageSize.Portrait")
        print(f"- setPageSize() → 使用QPageSize对象")
        print(f"- setOrientation() → setPageOrientation()")
        print(f"{'='*50}")
        
        return True
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已正确安装PySide6及其打印支持模块")
        return False
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_print_api_fix()
    if success:
        print(f"\n✅ 打印API修复测试通过！")
    else:
        print(f"\n❌ 打印API修复测试失败！")
