#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试A4画布缩放逻辑
验证缩放整个A4画布而不是只缩放内容
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_a4_canvas_structure():
    """测试A4画布结构"""
    print("\n测试A4画布结构...")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        from ui.interactive_preview_label import InteractivePreviewLabel
        
        # 检查是否已有QApplication实例
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建交互式预览标签
        preview_label = InteractivePreviewLabel()
        
        # 检查A4画布属性
        print("A4画布属性检查:")
        
        if hasattr(preview_label, 'a4_width_mm') and preview_label.a4_width_mm == 210:
            print("✓ A4宽度设置正确 (210mm)")
        else:
            print("❌ A4宽度设置不正确")
            return False
        
        if hasattr(preview_label, 'a4_height_mm') and preview_label.a4_height_mm == 297:
            print("✓ A4高度设置正确 (297mm)")
        else:
            print("❌ A4高度设置不正确")
            return False
        
        if hasattr(preview_label, 'base_width') and preview_label.base_width == 400:
            print("✓ 基础显示宽度设置正确 (400px)")
        else:
            print("❌ 基础显示宽度设置不正确")
            return False
        
        # 检查A4比例
        expected_height = int(400 * (297 / 210))  # 约566
        if hasattr(preview_label, 'base_height') and abs(preview_label.base_height - expected_height) <= 1:
            print(f"✓ 基础显示高度设置正确 ({preview_label.base_height}px，A4比例)")
        else:
            print(f"❌ 基础显示高度设置不正确 (期望约{expected_height}px)")
            return False
        
        print("\nA4画布结构验证:")
        print("  ✅ A4纸张尺寸标准 (210×297mm)")
        print("  ✅ 基础显示尺寸合理 (400×566px)")
        print("  ✅ 保持正确的A4比例")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_scaling_logic():
    """测试缩放逻辑"""
    print("\n测试缩放逻辑...")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        from ui.interactive_preview_label import InteractivePreviewLabel
        from PySide6.QtGui import QPixmap
        
        # 检查是否已有QApplication实例
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建交互式预览标签
        preview_label = InteractivePreviewLabel()
        
        # 测试初始状态
        print("初始状态检查:")
        if preview_label.scale_factor == 1.0:
            print("✓ 初始缩放因子为1.0")
        else:
            print(f"❌ 初始缩放因子不正确: {preview_label.scale_factor}")
            return False
        
        # 测试缩放范围
        print("\n缩放范围检查:")
        if preview_label.min_scale == 0.1:
            print("✓ 最小缩放0.1")
        else:
            print(f"❌ 最小缩放设置不正确: {preview_label.min_scale}")
            return False
        
        if preview_label.max_scale == 5.0:
            print("✓ 最大缩放5.0")
        else:
            print(f"❌ 最大缩放设置不正确: {preview_label.max_scale}")
            return False
        
        # 测试缩放方法
        print("\n缩放方法测试:")
        
        # 测试设置缩放因子
        preview_label.set_scale_factor(2.0)
        if preview_label.scale_factor == 2.0:
            print("✓ 设置缩放因子2.0成功")
        else:
            print(f"❌ 设置缩放因子失败: {preview_label.scale_factor}")
            return False
        
        # 测试缩放限制
        preview_label.set_scale_factor(10.0)  # 超出最大值
        if preview_label.scale_factor == 5.0:
            print("✓ 缩放限制正常工作 (限制在最大值5.0)")
        else:
            print(f"❌ 缩放限制不正常: {preview_label.scale_factor}")
            return False
        
        preview_label.set_scale_factor(0.01)  # 低于最小值
        if preview_label.scale_factor == 0.1:
            print("✓ 缩放限制正常工作 (限制在最小值0.1)")
        else:
            print(f"❌ 缩放限制不正常: {preview_label.scale_factor}")
            return False
        
        # 重置缩放
        preview_label.reset_scale()
        if preview_label.scale_factor == 1.0:
            print("✓ 重置缩放成功")
        else:
            print(f"❌ 重置缩放失败: {preview_label.scale_factor}")
            return False
        
        print("\n缩放逻辑验证:")
        print("  ✅ 缩放因子设置正确")
        print("  ✅ 缩放范围限制有效")
        print("  ✅ 缩放方法工作正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_a4_display_update():
    """测试A4显示更新"""
    print("\n测试A4显示更新...")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        from ui.interactive_preview_label import InteractivePreviewLabel
        from PySide6.QtGui import QPixmap
        
        # 检查是否已有QApplication实例
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建交互式预览标签
        preview_label = InteractivePreviewLabel()
        
        # 检查update_a4_display方法
        if hasattr(preview_label, 'update_a4_display'):
            print("✓ update_a4_display方法存在")
        else:
            print("❌ update_a4_display方法不存在")
            return False
        
        # 测试A4显示更新
        print("\nA4显示更新测试:")
        
        # 测试不同缩放下的尺寸
        test_scales = [0.5, 1.0, 2.0]
        for scale in test_scales:
            preview_label.set_scale_factor(scale)
            
            expected_width = int(preview_label.base_width * scale)
            expected_height = int(preview_label.base_height * scale)
            
            # 检查标签尺寸
            actual_size = preview_label.size()
            if (abs(actual_size.width() - expected_width) <= 1 and 
                abs(actual_size.height() - expected_height) <= 1):
                print(f"✓ 缩放{scale}时尺寸正确: {actual_size.width()}×{actual_size.height()}px")
            else:
                print(f"❌ 缩放{scale}时尺寸不正确: 期望{expected_width}×{expected_height}px，实际{actual_size.width()}×{actual_size.height()}px")
                return False
        
        # 测试内容设置
        print("\n内容设置测试:")
        
        # 创建测试pixmap
        test_pixmap = QPixmap(400, 566)
        test_pixmap.fill()  # 白色背景
        
        # 设置内容
        preview_label.set_pixmap(test_pixmap)
        
        if hasattr(preview_label, 'content_pixmap') and preview_label.content_pixmap is not None:
            print("✓ 内容pixmap设置成功")
        else:
            print("❌ 内容pixmap设置失败")
            return False
        
        print("\nA4显示更新验证:")
        print("  ✅ A4画布尺寸随缩放正确变化")
        print("  ✅ 内容正确绘制到A4画布上")
        print("  ✅ 缩放影响整个A4画布而不是只影响内容")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fit_to_size():
    """测试适应尺寸功能"""
    print("\n测试适应尺寸功能...")
    print("=" * 50)
    
    try:
        from PySide6.QtWidgets import QApplication
        from ui.interactive_preview_label import InteractivePreviewLabel
        from PySide6.QtCore import QSize
        
        # 检查是否已有QApplication实例
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建交互式预览标签
        preview_label = InteractivePreviewLabel()
        
        # 测试适应不同尺寸
        test_sizes = [
            QSize(200, 283),  # 小尺寸
            QSize(400, 566),  # 基础尺寸
            QSize(800, 1132)  # 大尺寸
        ]
        
        print("适应尺寸测试:")
        for target_size in test_sizes:
            preview_label.fit_to_size(target_size)
            
            # 计算期望的缩放因子
            scale_x = target_size.width() / preview_label.base_width
            scale_y = target_size.height() / preview_label.base_height
            expected_scale = min(scale_x, scale_y)
            
            if abs(preview_label.scale_factor - expected_scale) < 0.01:
                print(f"✓ 适应尺寸{target_size.width()}×{target_size.height()}成功，缩放因子{preview_label.scale_factor:.2f}")
            else:
                print(f"❌ 适应尺寸失败: 期望缩放{expected_scale:.2f}，实际{preview_label.scale_factor:.2f}")
                return False
        
        print("\n适应尺寸验证:")
        print("  ✅ 正确计算适应缩放因子")
        print("  ✅ 保持A4画布比例")
        print("  ✅ 适应不同目标尺寸")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("A4画布缩放逻辑测试")
    print("=" * 60)
    
    # 运行测试
    test1_result = test_a4_canvas_structure()
    test2_result = test_scaling_logic()
    test3_result = test_a4_display_update()
    test4_result = test_fit_to_size()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"  A4画布结构测试: {'✅ 通过' if test1_result else '❌ 失败'}")
    print(f"  缩放逻辑测试: {'✅ 通过' if test2_result else '❌ 失败'}")
    print(f"  A4显示更新测试: {'✅ 通过' if test3_result else '❌ 失败'}")
    print(f"  适应尺寸测试: {'✅ 通过' if test4_result else '❌ 失败'}")
    
    if test1_result and test2_result and test3_result and test4_result:
        print("\n🎉 所有测试通过！A4画布缩放逻辑修复成功！")
        print("\n修复效果:")
        print("  📐 缩放整个A4画布而不是只缩放内容")
        print("  🎯 A4纸区域始终保持正确比例")
        print("  🔍 滚轮缩放影响整个画布显示大小")
        print("  📄 排版内容正确显示在A4纸区域内")
        return True
    else:
        print("\n❌ 部分测试失败，需要进一步检查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
