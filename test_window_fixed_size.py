#!/usr/bin/env python3
"""
测试窗口固定尺寸功能
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_window_fixed_size():
    """测试窗口固定尺寸"""
    print("=== 测试窗口固定尺寸功能 ===\n")
    
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
        
        print(f"窗口配置信息:")
        print(f"  预期尺寸: {WINDOW_WIDTH} × {WINDOW_HEIGHT}")
        print(f"  实际尺寸: {window.width()} × {window.height()}")
        print(f"  最小尺寸: {window.minimumWidth()} × {window.minimumHeight()}")
        print(f"  最大尺寸: {window.maximumWidth()} × {window.maximumHeight()}")
        print()
        
        # 检查窗口标志
        flags = window.windowFlags()
        print(f"窗口标志检查:")
        print(f"  是否可调整大小: {bool(flags & Qt.WindowType.Window)}")
        print(f"  是否有最大化按钮: {bool(flags & Qt.WindowMaximizeButtonHint)}")
        print(f"  是否有最小化按钮: {bool(flags & Qt.WindowMinimizeButtonHint)}")
        print(f"  是否有关闭按钮: {bool(flags & Qt.WindowCloseButtonHint)}")
        print()
        
        # 检查是否为固定尺寸
        is_fixed_width = window.minimumWidth() == window.maximumWidth()
        is_fixed_height = window.minimumHeight() == window.maximumHeight()
        is_fixed_size = is_fixed_width and is_fixed_height
        
        print(f"固定尺寸检查:")
        print(f"  宽度固定: {'✅' if is_fixed_width else '❌'}")
        print(f"  高度固定: {'✅' if is_fixed_height else '❌'}")
        print(f"  完全固定: {'✅' if is_fixed_size else '❌'}")
        print()
        
        if is_fixed_size:
            print("✅ 窗口尺寸已成功设置为固定大小！")
            print(f"   固定尺寸: {window.width()} × {window.height()}")
        else:
            print("❌ 窗口尺寸设置失败，仍然可以调整大小")
        
        # 检查窗口是否正确居中
        screen = window.screen().availableGeometry()
        expected_x = (screen.width() - WINDOW_WIDTH) // 2
        expected_y = (screen.height() - WINDOW_HEIGHT) // 2
        actual_x = window.x()
        actual_y = window.y()
        
        print(f"\n窗口位置检查:")
        print(f"  屏幕尺寸: {screen.width()} × {screen.height()}")
        print(f"  期望位置: ({expected_x}, {expected_y})")
        print(f"  实际位置: ({actual_x}, {actual_y})")
        
        # 允许一些误差
        position_ok = abs(actual_x - expected_x) <= 10 and abs(actual_y - expected_y) <= 10
        print(f"  位置正确: {'✅' if position_ok else '❌'}")
        
        # 显示窗口（可选，用于手动验证）
        print(f"\n提示: 窗口已创建但未显示。")
        print(f"如需手动验证，可以取消注释下面的代码行。")
        # window.show()
        # app.exec()
        
        return is_fixed_size and position_ok
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_window_fixed_size()
    if success:
        print(f"\n🎉 窗口固定尺寸功能测试通过！")
    else:
        print(f"\n❌ 窗口固定尺寸功能测试失败！")
