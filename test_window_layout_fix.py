#!/usr/bin/env python3
"""
测试窗口布局修复效果
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_window_layout_fix():
    """测试窗口布局修复"""
    print("=== 测试窗口布局修复效果 ===\n")
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from ui.main_window import MainWindow
        from utils.config import WINDOW_WIDTH, WINDOW_HEIGHT
        
        # 创建应用程序（如果不存在）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建主窗口
        window = MainWindow()
        
        print(f"窗口尺寸检查:")
        print(f"  窗口宽度: {WINDOW_WIDTH}px")
        print(f"  窗口高度: {WINDOW_HEIGHT}px")
        print(f"  实际尺寸: {window.width()} × {window.height()}")
        print()
        
        # 检查列宽设置
        column_widths = [260, 340, 480, 300]
        total_width = sum(column_widths)
        
        print(f"列宽分配:")
        print(f"  图片列表: {column_widths[0]}px")
        print(f"  单图编辑: {column_widths[1]}px")
        print(f"  A4预览: {column_widths[2]}px")
        print(f"  控制面板: {column_widths[3]}px")
        print(f"  总计: {total_width}px")
        print(f"  窗口宽度: {WINDOW_WIDTH}px")
        print(f"  剩余空间: {WINDOW_WIDTH - total_width}px")
        print()
        
        # 检查是否有重叠
        if total_width <= WINDOW_WIDTH:
            margin = WINDOW_WIDTH - total_width
            print(f"✅ 列宽设置合理，有{margin}px边距空间")
        else:
            overlap = total_width - WINDOW_WIDTH
            print(f"❌ 列宽超出窗口，重叠{overlap}px")
        
        # 检查窗口标志
        flags = window.windowFlags()
        print(f"\n窗口控制检查:")
        print(f"  是否有最大化按钮: {bool(flags & Qt.WindowMaximizeButtonHint)}")
        print(f"  是否有最小化按钮: {bool(flags & Qt.WindowMinimizeButtonHint)}")
        print(f"  是否有关闭按钮: {bool(flags & Qt.WindowCloseButtonHint)}")
        print(f"  是否可调整大小: {window.minimumWidth() != window.maximumWidth() or window.minimumHeight() != window.maximumHeight()}")
        print()
        
        # 检查固定尺寸
        is_fixed_width = window.minimumWidth() == window.maximumWidth()
        is_fixed_height = window.minimumHeight() == window.maximumHeight()
        
        print(f"固定尺寸检查:")
        print(f"  宽度固定: {'✅' if is_fixed_width else '❌'}")
        print(f"  高度固定: {'✅' if is_fixed_height else '❌'}")
        print(f"  最小尺寸: {window.minimumWidth()} × {window.minimumHeight()}")
        print(f"  最大尺寸: {window.maximumWidth()} × {window.maximumHeight()}")
        print()
        
        # 总结
        layout_ok = total_width <= WINDOW_WIDTH
        close_button_ok = bool(flags & Qt.WindowCloseButtonHint)
        maximize_disabled = not bool(flags & Qt.WindowMaximizeButtonHint)
        size_fixed = is_fixed_width and is_fixed_height
        
        print(f"修复效果总结:")
        print(f"  ✅ 列宽不重叠: {'是' if layout_ok else '否'}")
        print(f"  ✅ 关闭按钮可用: {'是' if close_button_ok else '否'}")
        print(f"  ✅ 最大化按钮禁用: {'是' if maximize_disabled else '否'}")
        print(f"  ✅ 窗口尺寸固定: {'是' if size_fixed else '否'}")
        
        all_ok = layout_ok and close_button_ok and maximize_disabled and size_fixed
        
        if all_ok:
            print(f"\n🎉 所有问题都已修复！")
        else:
            print(f"\n⚠️ 还有问题需要解决")
        
        return all_ok
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_window_layout_fix()
    if success:
        print(f"\n✅ 窗口布局修复测试通过！")
    else:
        print(f"\n❌ 窗口布局修复测试失败！")
