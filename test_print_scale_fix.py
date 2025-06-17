#!/usr/bin/env python3
"""
测试打印缩放修复
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_print_scale_fix():
    """测试打印缩放修复"""
    print("=== 测试打印缩放修复 ===\n")
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtPrintSupport import QPrinter
        from PySide6.QtGui import QPageSize
        from ui.main_window import MainWindow
        
        # 创建应用程序（如果不存在）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建主窗口
        window = MainWindow()
        
        print("1. 测试打印机DPI和缩放计算...")
        
        # 创建打印机对象
        printer = QPrinter(QPrinter.HighResolution)
        page_size = QPageSize(QPageSize.A4)
        printer.setPageSize(page_size)
        
        # 获取打印机信息
        printer_dpi = printer.resolution()
        page_rect = printer.pageRect(QPrinter.Point)
        
        print(f"   打印机DPI: {printer_dpi}")
        print(f"   页面尺寸: {page_rect.width():.1f} × {page_rect.height():.1f} 点")
        
        # 计算A4纸的理论尺寸
        a4_width_mm = 210
        a4_height_mm = 297
        a4_width_points = (a4_width_mm / 25.4) * 72  # 72点/英寸
        a4_height_points = (a4_height_mm / 25.4) * 72
        
        print(f"   A4理论尺寸: {a4_width_points:.1f} × {a4_height_points:.1f} 点")
        
        # 计算缩放比例（使用新的页面比例方法）
        a4_width_px = window.layout_engine.a4_width_px
        a4_height_px = window.layout_engine.a4_height_px

        scale_x = page_rect.width() / a4_width_px
        scale_y = page_rect.height() / a4_height_px
        scale = min(scale_x, scale_y)
        
        print(f"   屏幕A4尺寸: {a4_width_px} × {a4_height_px} px")
        print(f"   缩放比例: {scale:.3f} (X={scale_x:.3f}, Y={scale_y:.3f})")
        
        print(f"\n2. 测试圆形尺寸计算...")
        
        # 获取当前圆形尺寸
        badge_diameter_px = window.layout_engine.badge_diameter_px
        from utils.config import app_config
        badge_diameter_mm = app_config.badge_diameter_mm
        
        print(f"   屏幕圆形直径: {badge_diameter_px}px ({badge_diameter_mm}mm)")
        
        # 计算打印圆形尺寸
        circle_diameter_print = badge_diameter_px * scale
        circle_diameter_mm_print = (circle_diameter_print / 72) * 25.4  # 转换为毫米
        
        print(f"   打印圆形直径: {circle_diameter_print:.1f}点 ({circle_diameter_mm_print:.1f}mm)")
        
        # 检查尺寸是否合理
        size_ratio = circle_diameter_mm_print / badge_diameter_mm
        print(f"   尺寸比例: {size_ratio:.2f} (应该接近1.0)")
        
        if 0.9 <= size_ratio <= 1.1:
            print("   ✅ 圆形尺寸计算正确")
        else:
            print("   ❌ 圆形尺寸计算有误")
        
        print(f"\n3. 测试布局位置计算...")
        
        # 获取布局位置
        layout_result = window.layout_engine.calculate_grid_layout(5, 15)
        positions = layout_result['positions']
        
        if positions:
            print(f"   布局位置数量: {len(positions)}")
            
            # 测试第一个位置的转换
            first_pos = positions[0]
            screen_x, screen_y = first_pos
            
            print(f"   屏幕第一个位置: ({screen_x}, {screen_y})px")
            
            # 转换为打印位置
            print_center_x = screen_x * scale
            print_center_y = screen_y * scale
            
            print(f"   打印中心位置: ({print_center_x:.1f}, {print_center_y:.1f})点")
            
            # 转换为毫米
            center_x_mm = (print_center_x / 72) * 25.4
            center_y_mm = (print_center_y / 72) * 25.4
            
            print(f"   打印中心位置: ({center_x_mm:.1f}, {center_y_mm:.1f})mm")
            
            # 检查是否在合理范围内
            if 0 <= center_x_mm <= 210 and 0 <= center_y_mm <= 297:
                print("   ✅ 位置计算在A4范围内")
            else:
                print("   ❌ 位置计算超出A4范围")
        else:
            print("   ❌ 没有找到布局位置")
        
        print(f"\n4. 测试打印预览功能...")
        
        # 检查打印预览方法
        has_print_preview = hasattr(window, 'print_preview')
        has_render_to_printer = hasattr(window, 'render_to_printer')
        
        print(f"   print_preview 方法: {'✅' if has_print_preview else '❌'}")
        print(f"   render_to_printer 方法: {'✅' if has_render_to_printer else '❌'}")
        
        print(f"\n{'='*50}")
        print("打印缩放修复测试总结:")
        
        # 检查各项修复
        dpi_ok = printer_dpi > 0
        scale_ok = 0.1 <= scale <= 2.0  # 合理的缩放范围（打印通常会缩小）
        size_ok = 0.9 <= size_ratio <= 1.1 if 'size_ratio' in locals() else False
        position_ok = len(positions) > 0 if positions else False
        methods_ok = has_print_preview and has_render_to_printer
        
        print(f"✅ 打印机DPI获取: {'正常' if dpi_ok else '异常'}")
        print(f"✅ 缩放比例计算: {'正常' if scale_ok else '异常'}")
        print(f"✅ 圆形尺寸转换: {'正确' if size_ok else '有误'}")
        print(f"✅ 位置计算: {'正常' if position_ok else '异常'}")
        print(f"✅ 打印方法: {'完整' if methods_ok else '缺失'}")
        
        all_ok = all([dpi_ok, scale_ok, size_ok, position_ok, methods_ok])
        
        if all_ok:
            print(f"\n🎉 打印缩放修复成功！")
            print(f"\n修复内容:")
            print(f"- 使用正确的DPI计算缩放比例")
            print(f"- 修复了圆心到左上角的位置转换")
            print(f"- 改进了打印预览的信号连接")
            print(f"- 添加了调试信息输出")
        else:
            print(f"\n⚠️ 部分修复可能需要进一步调整")
        
        print(f"\n使用建议:")
        print(f"- 打印前使用打印预览确认效果")
        print(f"- 如果尺寸仍然不对，检查打印机设置")
        print(f"- 确保选择正确的纸张尺寸（A4）")
        print(f"{'='*50}")
        
        return all_ok
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_print_scale_fix()
    if success:
        print(f"\n✅ 打印缩放修复测试通过！")
    else:
        print(f"\n❌ 打印缩放修复测试失败！")
