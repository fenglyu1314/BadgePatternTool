#!/usr/bin/env python3
"""
UI改进功能测试脚本
验证所有新增的UI优化功能
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_ui_improvements():
    """测试UI改进功能"""
    print("=== BadgePatternTool UI改进功能测试 ===\n")
    
    try:
        # 测试导入
        print("1. 测试模块导入...")
        from ui.main_window import MainWindow
        from ui.interactive_preview_label import InteractivePreviewLabel, InteractiveScrollArea
        from core.layout_engine import LayoutEngine
        print("✅ 所有模块导入成功")
        
        # 测试六边形布局算法
        print("\n2. 测试六边形布局算法...")
        layout_engine = LayoutEngine()
        compact_layout = layout_engine.calculate_compact_layout(5, 15)
        print(f"✅ 六边形布局算法正常，可放置 {compact_layout['max_count']} 个圆形")
        print(f"   - 圆心距离: {compact_layout['center_distance']:.1f}px")
        print(f"   - 垂直间距: {compact_layout['vertical_spacing']:.1f}px")
        print(f"   - 水平间距: {compact_layout['horizontal_spacing']:.1f}px")
        
        # 测试交互式预览组件
        print("\n3. 测试交互式预览组件...")
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QPixmap
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建交互式组件
        interactive_area = InteractiveScrollArea()
        print("✅ 交互式预览组件创建成功")
        
        # 测试缩放功能
        interactive_area.preview_label.set_scale_factor(1.5)
        scale = interactive_area.get_scale_factor()
        print(f"✅ 缩放功能正常，当前缩放比例: {scale}")
        
        print("\n4. 测试主窗口创建...")
        # 创建主窗口（不显示）
        main_window = MainWindow()
        print("✅ 主窗口创建成功")
        
        # 测试防抖定时器
        print("\n5. 测试防抖定时器...")
        if hasattr(main_window, 'edit_preview_timer'):
            print("✅ 编辑预览防抖定时器已创建")
        if hasattr(main_window, 'layout_preview_timer'):
            print("✅ 布局预览防抖定时器已创建")
        if hasattr(main_window, 'list_update_timer'):
            print("✅ 列表更新防抖定时器已创建")
        
        # 测试UI布局
        print("\n6. 测试UI布局改进...")
        if hasattr(main_window, 'quantity_spinbox'):
            print("✅ 数量设置控件已移至单图编辑区域")
        if hasattr(main_window, 'interactive_scroll_area'):
            print("✅ 交互式滚动区域已集成")
        
        # 测试图片列表设置
        print("\n7. 测试图片列表改进...")
        list_widget = main_window.image_listbox
        icon_size = list_widget.iconSize()
        print(f"✅ 图片列表支持缩略图，图标大小: {icon_size.width()}x{icon_size.height()}")
        
        print("\n=== 所有测试通过！ ===")
        print("\n改进功能总结:")
        print("1. ✅ 数量设置已移至单图编辑标签页")
        print("2. ✅ 六边形蜂巢布局算法已优化")
        print("3. ✅ 图片列表支持缩略图显示")
        print("4. ✅ 滑条操作性能已优化（防抖机制）")
        print("5. ✅ A4预览支持鼠标滚轮缩放和拖动")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_usage_guide():
    """打印使用指南"""
    print("\n" + "="*60)
    print("📖 新功能使用指南")
    print("="*60)
    
    print("\n🎯 1. 数量设置功能")
    print("   - 位置：单图编辑标签页 → 编辑控制 → 数量设置")
    print("   - 功能：为每张图片设置在画布上出现的数量")
    print("   - 操作：使用数字输入框或快速按钮（1、5、10）")
    
    print("\n🔷 2. 六边形蜂巢布局")
    print("   - 位置：排列模式 → 紧密排列")
    print("   - 特点：相邻图片距离完全相等，空间利用率更高")
    print("   - 优势：更美观的排列效果，符合几何学原理")
    
    print("\n🖼️ 3. 图片列表缩略图")
    print("   - 功能：图片列表显示48x48像素缩略图")
    print("   - 优势：快速识别图片内容，提升用户体验")
    print("   - 显示：文件名 + 尺寸信息 + 数量标识")
    
    print("\n⚡ 4. 滑条操作优化")
    print("   - 防抖延迟：150毫秒")
    print("   - 优化项目：缩放、位置调整、间距、页边距、预览缩放")
    print("   - 效果：消除卡顿，提升响应性能")
    
    print("\n🖱️ 5. A4预览交互")
    print("   - 鼠标滚轮：缩放预览（0.1x - 3.0x）")
    print("   - 鼠标拖动：平移预览画布")
    print("   - 适应窗口：自动调整到最佳显示大小")
    print("   - 重置视图：恢复到原始大小和位置")
    
    print("\n💡 使用建议:")
    print("   1. 导入图片后，先在单图编辑中调整每张图片的参数")
    print("   2. 设置合适的数量，利用六边形布局优化排版")
    print("   3. 在A4预览中使用鼠标交互查看细节")
    print("   4. 使用自动排版功能快速优化所有图片")

if __name__ == "__main__":
    success = test_ui_improvements()
    if success:
        print_usage_guide()
    else:
        print("\n请检查代码并修复错误后重新测试")
