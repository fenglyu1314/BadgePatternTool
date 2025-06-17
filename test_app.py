#!/usr/bin/env python3
"""
BadgePatternTool 测试脚本
用于快速测试应用程序的基本功能
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """测试所有模块导入"""
    print("测试模块导入...")
    
    try:
        import utils.config
        print("✓ utils.config 导入成功")
        
        from utils.file_handler import FileHandler, ImageItem
        print("✓ utils.file_handler 导入成功")
        
        from core.image_processor import ImageProcessor, CircleEditor
        print("✓ core.image_processor 导入成功")
        
        from core.layout_engine import LayoutEngine
        print("✓ core.layout_engine 导入成功")
        
        from core.export_manager import ExportManager
        print("✓ core.export_manager 导入成功")
        
        from ui.main_window import MainWindow
        print("✓ ui.main_window 导入成功")
        
        print("所有模块导入成功！")
        return True
        
    except Exception as e:
        print(f"✗ 模块导入失败: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    print("\n测试基本功能...")

    try:
        from utils.file_handler import FileHandler
        from core.image_processor import ImageProcessor
        from core.layout_engine import LayoutEngine
        from core.export_manager import ExportManager

        # 测试文件处理器
        file_handler = FileHandler()
        print("✓ FileHandler 创建成功")

        # 测试图片处理器
        image_processor = ImageProcessor()
        print("✓ ImageProcessor 创建成功")

        # 测试布局引擎
        layout_engine = LayoutEngine()
        layout_info = layout_engine.get_layout_info()
        print(f"✓ LayoutEngine 创建成功，最大容量: {layout_info['max_count']}")

        # 测试导出管理器
        export_manager = ExportManager()
        print("✓ ExportManager 创建成功")

        print("基本功能测试通过！")
        return True

    except Exception as e:
        print(f"✗ 基本功能测试失败: {e}")
        return False

def test_gui():
    """测试GUI启动"""
    print("\n测试GUI启动...")
    
    try:
        from PySide6.QtWidgets import QApplication
        
        # 创建应用程序
        app = QApplication(sys.argv)
        
        # 创建主窗口
        from ui.main_window import MainWindow
        main_window = MainWindow()
        
        print("✓ GUI创建成功")
        print("注意: 窗口已创建但未显示，测试完成后会自动关闭")
        
        # 不显示窗口，直接退出
        app.quit()
        
        return True
        
    except Exception as e:
        print(f"✗ GUI测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("BadgePatternTool 功能测试")
    print("=" * 50)
    
    # 运行测试
    tests = [
        test_imports,
        test_basic_functionality,
        test_gui
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！应用程序可以正常运行。")
        print("\n启动应用程序:")
        print("python src/main.py")
    else:
        print("❌ 部分测试失败，请检查错误信息。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
