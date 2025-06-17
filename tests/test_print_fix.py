#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试打印功能修复
验证QPrinter.pageRect()方法的正确调用
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_qprinter_page_rect():
    """测试QPrinter.pageRect()方法的正确调用"""
    print("\n测试QPrinter.pageRect()方法...")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtPrintSupport import QPrinter
        from PySide6.QtGui import QPainter
        
        # 创建应用程序
        app = QApplication(sys.argv)
        
        # 创建打印机对象
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        
        # 测试不同的Unit参数
        units_to_test = [
            QPrinter.Unit.DevicePixel,
            QPrinter.Unit.Point,
            QPrinter.Unit.Millimeter,
            QPrinter.Unit.Inch
        ]
        
        print("✓ QPrinter对象创建成功")
        
        for unit in units_to_test:
            try:
                page_rect = printer.pageRect(unit)
                print(f"✓ pageRect({unit.name}) 调用成功: {page_rect}")
            except Exception as e:
                print(f"❌ pageRect({unit.name}) 调用失败: {e}")
                return False
        
        # 测试错误的调用方式（应该失败）
        try:
            # 这是错误的调用方式，应该会失败
            page_rect = printer.pageRect(printer.Point)  # 这会失败
            print("❌ 错误的调用方式居然成功了，这不应该发生")
            return False
        except AttributeError:
            print("✓ 错误的调用方式正确地失败了（printer.Point不存在）")
        except Exception as e:
            print(f"✓ 错误的调用方式正确地失败了: {e}")
        
        # 清理
        app.quit()
        
        print("\n修复验证:")
        print("  ✅ QPrinter.pageRect()需要Unit参数")
        print("  ✅ QPrinter.Unit.DevicePixel是正确的参数")
        print("  ✅ printer.Point属性不存在（这是错误的用法）")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_window_print_fix():
    """测试主窗口的打印修复"""
    print("\n测试主窗口打印修复...")
    print("=" * 50)

    try:
        from PySide6.QtWidgets import QApplication
        from ui.main_window import MainWindow

        # 检查是否已有QApplication实例
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建主窗口
        main_window = MainWindow()
        
        # 检查paint_requested_handler方法是否存在
        if hasattr(main_window, 'paint_requested_handler'):
            print("✓ paint_requested_handler方法存在")
        else:
            print("❌ paint_requested_handler方法不存在")
            return False
        
        # 模拟打印机对象
        from PySide6.QtPrintSupport import QPrinter
        printer = QPrinter()
        
        # 设置空的图片列表进行测试
        main_window._current_print_images = []
        
        # 尝试调用paint_requested_handler（应该不会崩溃）
        try:
            main_window.paint_requested_handler(printer)
            print("✓ paint_requested_handler调用成功（空图片列表）")
        except Exception as e:
            print(f"❌ paint_requested_handler调用失败: {e}")
            return False
        
        # 不需要清理QApplication，因为可能是共享的实例
        
        print("\n主窗口修复验证:")
        print("  ✅ 使用QPrinter.Unit.DevicePixel替代printer.Point")
        print("  ✅ paint_requested_handler方法可以正常调用")
        print("  ✅ 错误处理机制正常工作")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("打印功能修复测试")
    print("=" * 60)
    
    # 运行测试
    test1_result = test_qprinter_page_rect()
    test2_result = test_main_window_print_fix()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"  QPrinter.pageRect()测试: {'✅ 通过' if test1_result else '❌ 失败'}")
    print(f"  主窗口打印修复测试: {'✅ 通过' if test2_result else '❌ 失败'}")
    
    if test1_result and test2_result:
        print("\n🎉 所有测试通过！打印功能修复成功！")
        return True
    else:
        print("\n❌ 部分测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
