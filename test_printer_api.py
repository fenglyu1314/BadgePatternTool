#!/usr/bin/env python3
"""
测试QPrinter API的正确用法
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_printer_api():
    """测试QPrinter API"""
    print("=== 测试QPrinter API ===\n")
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtPrintSupport import QPrinter
        from PySide6.QtGui import QPageSize
        
        # 创建应用程序（如果不存在）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("1. 探索QPrinter的可用属性...")
        
        # 创建打印机对象
        printer = QPrinter()
        
        # 查看QPrinter的属性
        print("QPrinter的属性:")
        printer_attrs = [attr for attr in dir(QPrinter) if not attr.startswith('_')]
        orientation_attrs = [attr for attr in printer_attrs if 'orient' in attr.lower()]
        page_attrs = [attr for attr in printer_attrs if 'page' in attr.lower()]
        
        print(f"  方向相关: {orientation_attrs}")
        print(f"  页面相关: {page_attrs}")
        
        print("\n2. 探索QPageSize的可用属性...")
        
        # 查看QPageSize的属性
        pagesize_attrs = [attr for attr in dir(QPageSize) if not attr.startswith('_')]
        size_attrs = [attr for attr in pagesize_attrs if 'A4' in attr or 'size' in attr.lower()]
        
        print(f"  尺寸相关: {size_attrs}")
        
        print("\n3. 测试不同的API组合...")
        
        # 测试1: 基本设置
        try:
            printer1 = QPrinter()
            page_size = QPageSize(QPageSize.A4)
            printer1.setPageSize(page_size)
            print("   ✅ 基本页面大小设置成功")
        except Exception as e:
            print(f"   ❌ 基本设置失败: {e}")
        
        # 测试2: 查找方向设置方法
        orientation_methods = [attr for attr in dir(printer) if 'orientation' in attr.lower()]
        print(f"   方向设置方法: {orientation_methods}")
        
        # 测试3: 尝试不同的方向设置
        try:
            if hasattr(printer, 'setPageOrientation'):
                # 尝试找到正确的枚举值
                if hasattr(QPrinter, 'Orientation'):
                    print("   找到 QPrinter.Orientation")
                    if hasattr(QPrinter.Orientation, 'Portrait'):
                        printer.setPageOrientation(QPrinter.Orientation.Portrait)
                        print("   ✅ 使用 QPrinter.Orientation.Portrait 成功")
                    else:
                        print("   QPrinter.Orientation 没有 Portrait 属性")
                else:
                    print("   QPrinter 没有 Orientation 属性")
            else:
                print("   QPrinter 没有 setPageOrientation 方法")
        except Exception as e:
            print(f"   方向设置测试失败: {e}")
        
        # 测试4: 尝试旧的API（如果还存在）
        try:
            if hasattr(printer, 'setOrientation'):
                print("   找到旧的 setOrientation 方法")
                # 尝试找到Portrait常量
                if hasattr(QPrinter, 'Portrait'):
                    printer.setOrientation(QPrinter.Portrait)
                    print("   ✅ 使用旧API QPrinter.Portrait 成功")
                else:
                    print("   QPrinter 没有 Portrait 常量")
            else:
                print("   没有找到 setOrientation 方法")
        except Exception as e:
            print(f"   旧API测试失败: {e}")
        
        # 测试5: 检查默认设置
        try:
            printer_default = QPrinter()
            page_rect = printer_default.pageRect()
            print(f"   默认页面尺寸: {page_rect.width():.0f} × {page_rect.height():.0f}")
            
            # 检查是否已经是纵向
            if page_rect.height() > page_rect.width():
                print("   ✅ 默认已经是纵向，可能不需要设置方向")
            else:
                print("   默认是横向，需要设置为纵向")
                
        except Exception as e:
            print(f"   默认设置检查失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_printer_api()
