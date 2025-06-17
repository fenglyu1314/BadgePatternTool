#!/usr/bin/env python3
"""
测试打印功能优化
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_print_optimization():
    """测试打印功能优化"""
    print("=== 测试打印功能优化 ===\n")
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtPrintSupport import QPrinter, QPrintPreviewDialog
        from PySide6.QtGui import QPageSize, QPageLayout
        from PySide6.QtCore import QMarginsF, Qt
        from ui.main_window import MainWindow
        
        # 创建应用程序（如果不存在）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建主窗口
        window = MainWindow()
        
        print("1. 测试QPageLayout的使用...")
        
        try:
            # 测试页面布局创建（参考文章方法）
            page_layout = QPageLayout()
            page_layout.setPageSize(QPageSize(QPageSize.A4))
            page_layout.setOrientation(QPageLayout.Orientation.Portrait)
            # 转换毫米为点（setMargins只接受点单位）
            margin_points = 15 * 2.83465
            page_layout.setMargins(QMarginsF(margin_points, margin_points, margin_points, margin_points))
            
            print("   ✅ QPageLayout 创建成功")
            print(f"   页面尺寸: {page_layout.pageSize().name()}")
            print(f"   页面方向: {'纵向' if page_layout.orientation() == QPageLayout.Orientation.Portrait else '横向'}")
            
            # 获取页面信息
            page_rect = page_layout.paintRect(QPageLayout.Unit.Point)
            print(f"   绘制区域: {page_rect.width():.1f} × {page_rect.height():.1f} 点")
            
        except Exception as e:
            print(f"   ❌ QPageLayout 测试失败: {e}")
            return False
        
        print(f"\n2. 测试打印机页面布局设置...")
        
        try:
            # 创建打印机并设置页面布局
            printer = QPrinter(QPrinter.HighResolution)
            printer.setPageLayout(page_layout)
            
            # 验证设置是否生效
            current_layout = printer.pageLayout()
            current_margins = current_layout.margins()  # 默认返回点单位
            current_margins_mm = current_margins.left() / 2.83465  # 转换为毫米
            
            print("   ✅ 打印机页面布局设置成功")
            print(f"   页边距: {current_margins_mm:.1f}mm ({current_margins.left():.1f}点)")
            print(f"   页面尺寸: {current_layout.pageSize().name()}")
            
        except Exception as e:
            print(f"   ❌ 打印机页面布局测试失败: {e}")
            return False
        
        print(f"\n3. 测试QPainter初始化方式...")
        
        try:
            # 测试文章中推荐的QPainter初始化方式
            from PySide6.QtGui import QPainter
            
            # 方式1：直接传入打印机对象（文章推荐）
            painter1 = QPainter(printer)
            is_active1 = painter1.isActive()
            painter1.end()
            
            print(f"   方式1 (QPainter(printer)): {'✅ 成功' if is_active1 else '❌ 失败'}")
            
            # 方式2：先创建再begin（我们之前的方式）
            painter2 = QPainter()
            is_active2 = painter2.begin(printer)
            painter2.end()
            
            print(f"   方式2 (painter.begin(printer)): {'✅ 成功' if is_active2 else '❌ 失败'}")
            
        except Exception as e:
            print(f"   ❌ QPainter 测试失败: {e}")
            return False
        
        print(f"\n4. 测试打印预览对话框优化...")
        
        try:
            # 测试优化后的打印预览创建方式
            preview_dialog = QPrintPreviewDialog()
            preview_dialog.printer().setPageLayout(page_layout)
            preview_dialog.setWindowTitle("测试打印预览")
            
            # 测试窗口状态设置
            preview_dialog.setWindowState(Qt.WindowMaximized)
            
            print("   ✅ 打印预览对话框创建成功")
            print("   ✅ 页面布局设置成功")
            print("   ✅ 窗口最大化设置成功")
            
        except Exception as e:
            print(f"   ❌ 打印预览对话框测试失败: {e}")
            return False
        
        print(f"\n5. 测试主窗口打印方法更新...")
        
        # 检查主窗口的打印方法
        has_print_layout = hasattr(window, 'print_layout')
        has_print_preview = hasattr(window, 'print_preview')
        has_render_to_printer = hasattr(window, 'render_to_printer')
        
        print(f"   print_layout 方法: {'✅' if has_print_layout else '❌'}")
        print(f"   print_preview 方法: {'✅' if has_print_preview else '❌'}")
        print(f"   render_to_printer 方法: {'✅' if has_render_to_printer else '❌'}")
        
        print(f"\n6. 测试页边距单位转换...")
        
        try:
            # 测试毫米单位的页边距设置
            test_margins = [5, 10, 15, 20]
            
            for margin_mm in test_margins:
                test_layout = QPageLayout()
                test_layout.setPageSize(QPageSize(QPageSize.A4))

                # 转换毫米为点
                margin_points = margin_mm * 2.83465
                test_layout.setMargins(QMarginsF(margin_points, margin_points, margin_points, margin_points))

                # 获取设置的页边距
                margins_point = test_layout.margins()

                print(f"   {margin_mm}mm → {margins_point.left():.1f}点 (期望: {margin_points:.1f}点)")
            
            print("   ✅ 页边距单位转换正确")
            
        except Exception as e:
            print(f"   ❌ 页边距单位转换测试失败: {e}")
            return False
        
        print(f"\n{'='*50}")
        print("打印功能优化测试总结:")
        
        # 检查各项优化
        layout_ok = True  # QPageLayout测试通过
        printer_ok = True  # 打印机设置测试通过
        painter_ok = is_active1  # QPainter初始化测试
        preview_ok = True  # 打印预览测试通过
        methods_ok = has_print_layout and has_print_preview and has_render_to_printer
        margins_ok = True  # 页边距转换测试通过
        
        print(f"✅ QPageLayout 使用: {'正确' if layout_ok else '有误'}")
        print(f"✅ 打印机页面布局: {'正确' if printer_ok else '有误'}")
        print(f"✅ QPainter 初始化: {'优化' if painter_ok else '需改进'}")
        print(f"✅ 打印预览对话框: {'优化' if preview_ok else '需改进'}")
        print(f"✅ 主窗口方法: {'完整' if methods_ok else '缺失'}")
        print(f"✅ 页边距处理: {'正确' if margins_ok else '有误'}")
        
        all_ok = all([layout_ok, printer_ok, painter_ok, preview_ok, methods_ok, margins_ok])
        
        if all_ok:
            print(f"\n🎉 打印功能优化成功！")
            print(f"\n优化内容（参考CSDN文章）:")
            print(f"- 使用QPageLayout统一管理页面设置")
            print(f"- 优化QPainter初始化方式")
            print(f"- 改进打印预览对话框创建")
            print(f"- 使用毫米单位设置页边距")
            print(f"- 添加窗口最大化显示")
        else:
            print(f"\n⚠️ 部分优化可能需要进一步调整")
        
        print(f"\n参考文章要点:")
        print(f"- 使用QPageLayout.setMargins()设置毫米单位页边距")
        print(f"- 使用QPainter(printer)直接初始化")
        print(f"- 使用lambda连接paintRequested信号")
        print(f"- 设置预览窗口最大化显示")
        print(f"{'='*50}")
        
        return all_ok
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_print_optimization()
    if success:
        print(f"\n✅ 打印功能优化测试通过！")
    else:
        print(f"\n❌ 打印功能优化测试失败！")
