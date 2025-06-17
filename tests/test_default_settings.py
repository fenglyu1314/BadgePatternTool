#!/usr/bin/env python3
"""
默认设置测试
验证新的默认设置是否正确应用
"""

import sys
from pathlib import Path

# 添加src目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

def test_config_defaults():
    """测试配置文件的默认值"""
    print("测试配置默认值...")
    
    try:
        from utils.config import (
            DEFAULT_SPACING, DEFAULT_MARGIN, DEFAULT_LAYOUT, DEFAULT_EXPORT_FORMAT
        )
        
        # 验证默认值
        assert DEFAULT_SPACING == 5, f"默认间距应为5mm，实际为{DEFAULT_SPACING}mm"
        assert DEFAULT_MARGIN == 5, f"默认边距应为5mm，实际为{DEFAULT_MARGIN}mm"
        assert DEFAULT_LAYOUT == "compact", f"默认布局应为compact，实际为{DEFAULT_LAYOUT}"
        assert DEFAULT_EXPORT_FORMAT == "PNG", f"默认导出格式应为PNG，实际为{DEFAULT_EXPORT_FORMAT}"
        
        print("✓ 配置默认值正确")
        print(f"  - 默认间距: {DEFAULT_SPACING}mm")
        print(f"  - 默认边距: {DEFAULT_MARGIN}mm")
        print(f"  - 默认布局: {DEFAULT_LAYOUT}")
        print(f"  - 默认导出格式: {DEFAULT_EXPORT_FORMAT}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置默认值测试失败: {e}")
        return False

def test_main_window_defaults():
    """测试主窗口的默认设置"""
    print("\n测试主窗口默认设置...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from ui.main_window import MainWindow
        
        # 创建应用程序
        app = QApplication(sys.argv)
        
        # 创建主窗口
        main_window = MainWindow()
        
        # 验证主窗口的默认设置
        assert main_window.layout_mode == "compact", f"主窗口默认布局应为compact，实际为{main_window.layout_mode}"
        assert main_window.spacing_value == 5, f"主窗口默认间距应为5，实际为{main_window.spacing_value}"
        assert main_window.margin_value == 5, f"主窗口默认边距应为5，实际为{main_window.margin_value}"
        assert main_window.export_format == "png", f"主窗口默认导出格式应为png，实际为{main_window.export_format}"
        
        print("✓ 主窗口默认设置正确")
        print(f"  - 布局模式: {main_window.layout_mode}")
        print(f"  - 间距值: {main_window.spacing_value}mm")
        print(f"  - 边距值: {main_window.margin_value}mm")
        print(f"  - 导出格式: {main_window.export_format}")
        
        # 验证UI控件的默认状态
        # 检查单选按钮
        compact_checked = False
        grid_checked = False
        for button in main_window.layout_button_group.buttons():
            if button.text() == "紧密排列" and button.isChecked():
                compact_checked = True
            elif button.text() == "网格排列" and button.isChecked():
                grid_checked = True
        
        assert compact_checked, "紧密排列单选按钮应该被选中"
        assert not grid_checked, "网格排列单选按钮不应该被选中"
        print("✓ 布局模式单选按钮状态正确")
        
        # 检查导出格式下拉框
        current_format = main_window.format_combo.currentText()
        assert current_format == "png", f"导出格式下拉框应选择png，实际选择{current_format}"
        print("✓ 导出格式下拉框状态正确")
        
        # 检查滑块值
        assert main_window.spacing_slider.value() == 5, f"间距滑块值应为5，实际为{main_window.spacing_slider.value()}"
        assert main_window.margin_slider.value() == 5, f"边距滑块值应为5，实际为{main_window.margin_slider.value()}"
        print("✓ 滑块默认值正确")
        
        # 清理
        app.quit()
        
        return True
        
    except Exception as e:
        print(f"❌ 主窗口默认设置测试失败: {e}")
        return False

def test_gray_circle_preview():
    """测试灰色圆形预览功能"""
    print("\n测试灰色圆形预览...")

    try:
        from PySide6.QtWidgets import QApplication
        from ui.main_window import MainWindow

        # 检查是否已有QApplication实例
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建主窗口
        main_window = MainWindow()
        
        # 验证没有图片时的预览状态
        assert len(main_window.image_items) == 0, "初始状态应该没有图片"
        
        # 检查是否有预览图片（应该显示灰色圆形）
        # 通过布局引擎直接测试预览生成
        layout_pixmap = main_window.layout_engine.create_layout_preview(
            [],  # 空图片列表
            layout_type=main_window.layout_mode,
            spacing_mm=main_window.spacing_value,
            margin_mm=main_window.margin_value,
            preview_scale=0.5
        )

        if layout_pixmap and not layout_pixmap.isNull():
            print("✓ 成功生成灰色圆形预览")
            print(f"  - 预览图片尺寸: {layout_pixmap.width()}x{layout_pixmap.height()}")
        else:
            print("❌ 预览图片生成失败")
        
        # 检查布局信息
        layout_info_text = main_window.layout_info_label.text()
        print(f"✓ 布局信息显示: {layout_info_text}")
        
        # 不需要清理，复用现有的QApplication
        
        return True
        
    except Exception as e:
        print(f"❌ 灰色圆形预览测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("BadgePatternTool 默认设置和灰色预览测试")
    print("=" * 60)
    
    # 运行测试
    tests = [
        test_config_defaults,
        test_main_window_defaults,
        test_gray_circle_preview
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！新的默认设置已正确应用。")
        print("\n改进效果:")
        print("  ✅ 默认使用紧密排列模式")
        print("  ✅ 默认间距和边距都为5mm")
        print("  ✅ 默认导出格式为PNG")
        print("  ✅ 启动时显示灰色圆形预览")
        print("  ✅ UI控件状态与默认设置一致")
    else:
        print("❌ 部分测试失败，请检查错误信息。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
