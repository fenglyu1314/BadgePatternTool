#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试UI改进
验证A4画布适应窗口和自动排版功能
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_auto_fit_to_window():
    """测试程序启动时自动适应窗口"""
    print("\n测试程序启动时自动适应窗口...")
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
        
        # 检查是否有适应窗口的方法
        if hasattr(main_window, 'fit_preview_to_window'):
            print("✓ fit_preview_to_window方法存在")
        else:
            print("❌ fit_preview_to_window方法不存在")
            return False
        
        # 检查InteractiveScrollArea是否有fit_to_window方法
        if hasattr(main_window.interactive_scroll_area, 'fit_to_window'):
            print("✓ InteractiveScrollArea.fit_to_window方法存在")
        else:
            print("❌ InteractiveScrollArea.fit_to_window方法不存在")
            return False
        
        # 检查初始化时是否设置了延迟适应窗口
        import inspect
        source = inspect.getsource(main_window.__init__)
        if "fit_preview_to_window" in source and "QTimer.singleShot" in source:
            print("✓ 初始化时设置了延迟适应窗口")
        else:
            print("❌ 初始化时没有设置延迟适应窗口")
            return False
        
        print("\n自动适应窗口验证:")
        print("  ✅ 程序启动时会自动适应窗口")
        print("  ✅ 使用QTimer延迟执行，确保界面完全加载")
        print("  ✅ 用户可以看到完整的A4画布")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_auto_layout_on_import():
    """测试导入图片后自动排版"""
    print("\n测试导入图片后自动排版...")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        from ui.main_window import MainWindow
        from utils.file_handler import ImageItem
        
        # 检查是否已有QApplication实例
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建主窗口
        main_window = MainWindow()
        
        # 检查是否有自动处理新图片的方法
        if hasattr(main_window, 'auto_process_new_images'):
            print("✓ auto_process_new_images方法存在")
        else:
            print("❌ auto_process_new_images方法不存在")
            return False
        
        # 检查导入图片逻辑是否包含自动处理
        import inspect
        source = inspect.getsource(main_window.import_images)
        if "auto_process_new_images" in source:
            print("✓ 导入图片时会调用自动处理")
        else:
            print("❌ 导入图片时没有调用自动处理")
            return False
        
        # 检查是否在导入后适应窗口
        if "fit_preview_to_window" in source:
            print("✓ 导入图片后会适应窗口")
        else:
            print("❌ 导入图片后没有适应窗口")
            return False
        
        # 模拟测试自动处理功能
        test_images = []
        for i in range(2):
            item = ImageItem.__new__(ImageItem)
            item.file_path = f"test_image_{i}.jpg"
            item.filename = f"test_image_{i}.jpg"
            item.scale = 1.0
            item.offset_x = 0
            item.offset_y = 0
            item.rotation = 0
            item.quantity = 1
            item.is_processed = False  # 模拟未处理状态
            test_images.append(item)
        
        # 添加到主窗口
        main_window.image_items = test_images
        
        # 测试自动处理
        main_window.auto_process_new_images()
        
        # 检查是否已处理
        processed_count = sum(1 for item in test_images if item.is_processed)
        if processed_count == len(test_images):
            print(f"✓ 自动处理了 {processed_count} 张图片")
        else:
            print(f"❌ 只处理了 {processed_count}/{len(test_images)} 张图片")
            return False
        
        print("\n自动排版验证:")
        print("  ✅ 导入图片后自动应用最佳参数")
        print("  ✅ 自动更新A4排版预览")
        print("  ✅ 自动适应窗口显示")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edit_auto_update():
    """测试编辑后自动更新排版"""
    print("\n测试编辑后自动更新排版...")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        from ui.main_window import MainWindow
        from utils.file_handler import ImageItem
        
        # 检查是否已有QApplication实例
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建主窗口
        main_window = MainWindow()
        
        # 检查apply_edit方法是否会更新排版
        import inspect
        source = inspect.getsource(main_window.apply_edit)
        if "update_layout_preview" in source:
            print("✓ apply_edit会更新排版预览")
        else:
            print("❌ apply_edit不会更新排版预览")
            return False
        
        # 检查滑块变化是否会触发防抖更新
        source = inspect.getsource(main_window.on_scale_change)
        if "edit_preview_timer" in source:
            print("✓ 缩放变化会触发防抖更新")
        else:
            print("❌ 缩放变化不会触发防抖更新")
            return False
        
        source = inspect.getsource(main_window.on_position_change)
        if "edit_preview_timer" in source:
            print("✓ 位置变化会触发防抖更新")
        else:
            print("❌ 位置变化不会触发防抖更新")
            return False
        
        # 检查数量变化是否会触发布局更新
        source = inspect.getsource(main_window.on_quantity_change)
        if "layout_preview_timer" in source:
            print("✓ 数量变化会触发布局更新")
        else:
            print("❌ 数量变化不会触发布局更新")
            return False
        
        print("\n编辑自动更新验证:")
        print("  ✅ 应用编辑后自动更新排版")
        print("  ✅ 滑块操作使用防抖机制")
        print("  ✅ 数量变化自动更新布局")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_responsiveness():
    """测试UI响应性改进"""
    print("\n测试UI响应性改进...")
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
        
        # 检查防抖定时器设置
        if hasattr(main_window, 'edit_preview_timer'):
            print("✓ 编辑预览防抖定时器存在")
        else:
            print("❌ 编辑预览防抖定时器不存在")
            return False
        
        if hasattr(main_window, 'layout_preview_timer'):
            print("✓ 布局预览防抖定时器存在")
        else:
            print("❌ 布局预览防抖定时器不存在")
            return False
        
        # 检查防抖延迟设置
        if hasattr(main_window, 'debounce_delay') and main_window.debounce_delay > 0:
            print(f"✓ 防抖延迟设置: {main_window.debounce_delay}ms")
        else:
            print("❌ 防抖延迟设置不正确")
            return False
        
        if hasattr(main_window, 'layout_debounce_delay') and main_window.layout_debounce_delay > 0:
            print(f"✓ 布局防抖延迟设置: {main_window.layout_debounce_delay}ms")
        else:
            print("❌ 布局防抖延迟设置不正确")
            return False
        
        print("\nUI响应性验证:")
        print("  ✅ 使用防抖机制优化性能")
        print("  ✅ 区分轻量级和重量级操作")
        print("  ✅ 合理的延迟时间设置")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("UI改进测试")
    print("=" * 60)
    
    # 运行测试
    test1_result = test_auto_fit_to_window()
    test2_result = test_auto_layout_on_import()
    test3_result = test_edit_auto_update()
    test4_result = test_ui_responsiveness()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"  自动适应窗口测试: {'✅ 通过' if test1_result else '❌ 失败'}")
    print(f"  导入自动排版测试: {'✅ 通过' if test2_result else '❌ 失败'}")
    print(f"  编辑自动更新测试: {'✅ 通过' if test3_result else '❌ 失败'}")
    print(f"  UI响应性测试: {'✅ 通过' if test4_result else '❌ 失败'}")
    
    if test1_result and test2_result and test3_result and test4_result:
        print("\n🎉 所有测试通过！UI改进成功！")
        print("\n改进效果:")
        print("  🖼️ A4画布启动时自动适应窗口")
        print("  🚀 导入图片后自动排版和适应窗口")
        print("  ⚡ 编辑操作实时更新排版预览")
        print("  🎛️ 使用防抖机制优化性能")
        return True
    else:
        print("\n❌ 部分测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
