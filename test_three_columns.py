#!/usr/bin/env python3
"""
测试3列布局的可行性
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_three_columns():
    """测试3列布局"""
    print("=== 测试3列布局的可行性 ===\n")
    
    try:
        from utils.config import BADGE_DIAMETER_PX, A4_WIDTH_PX, A4_HEIGHT_PX, mm_to_pixels
        
        print(f"基本参数:")
        print(f"  A4宽度: {A4_WIDTH_PX}px")
        print(f"  圆形直径: {BADGE_DIAMETER_PX}px")
        print()
        
        # 测试不同的间距和页边距
        test_cases = [
            {"spacing_mm": 2, "margin_mm": 8},
            {"spacing_mm": 1, "margin_mm": 5},
            {"spacing_mm": 0, "margin_mm": 5},
            {"spacing_mm": 0, "margin_mm": 3},
        ]
        
        for case in test_cases:
            spacing_mm = case["spacing_mm"]
            margin_mm = case["margin_mm"]
            
            spacing_px = mm_to_pixels(spacing_mm)
            margin_px = mm_to_pixels(margin_mm)
            
            available_width = A4_WIDTH_PX - 2 * margin_px
            
            print(f"测试设置: 间距={spacing_mm}mm, 页边距={margin_mm}mm")
            print(f"  可用宽度: {available_width}px")
            
            # 测试3列
            cols = 3
            total_circle_width = cols * BADGE_DIAMETER_PX
            available_for_spacing = available_width - total_circle_width
            
            print(f"  3列圆形总宽度: {total_circle_width}px")
            print(f"  可用于间距的空间: {available_for_spacing}px")
            
            if available_for_spacing >= 0:
                actual_spacing = available_for_spacing / (cols - 1)
                print(f"  实际间距: {actual_spacing:.1f}px ({actual_spacing/mm_to_pixels(1):.1f}mm)")
                
                if actual_spacing >= spacing_px:
                    print(f"  ✅ 3列可行！")
                    
                    # 计算水平间距
                    horizontal_spacing = BADGE_DIAMETER_PX + actual_spacing
                    print(f"  水平间距: {horizontal_spacing:.1f}px")
                    
                    # 计算起始位置
                    start_x = margin_px + BADGE_DIAMETER_PX // 2
                    
                    print(f"  列位置:")
                    for col in range(cols):
                        x = start_x + col * horizontal_spacing
                        left_edge = x - BADGE_DIAMETER_PX // 2
                        right_edge = x + BADGE_DIAMETER_PX // 2
                        
                        is_valid = (left_edge >= margin_px and right_edge <= A4_WIDTH_PX - margin_px)
                        print(f"    第{col+1}列: X={x:.0f}, 边界=[{left_edge:.0f}, {right_edge:.0f}], 有效={is_valid}")
                else:
                    print(f"  ❌ 间距不足 (需要至少 {spacing_px}px)")
            else:
                print(f"  ❌ 空间不足")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_three_columns()
