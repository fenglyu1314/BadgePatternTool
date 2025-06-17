#!/usr/bin/env python3
"""
测试32mm圆形的布局效果
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_32mm_layout():
    """测试32mm圆形的布局"""
    print("=== 测试32mm圆形的布局效果 ===\n")
    
    try:
        from core.layout_engine import LayoutEngine
        from utils.config import A4_WIDTH_PX, A4_HEIGHT_PX, mm_to_pixels
        
        # 创建32mm圆形的布局引擎
        from utils.config import app_config

        # 临时修改圆形尺寸
        original_diameter_mm = app_config.badge_diameter_mm
        app_config.badge_diameter_mm = 32

        layout_engine = LayoutEngine()
        
        print(f"圆形参数:")
        print(f"  直径: 32mm = {layout_engine.badge_diameter_px}px")
        print(f"  半径: {layout_engine.badge_radius_px}px")
        print()
        
        # 测试不同设置
        test_cases = [
            {"spacing_mm": 5, "margin_mm": 15, "desc": "默认设置"},
            {"spacing_mm": 3, "margin_mm": 10, "desc": "中等设置"},
            {"spacing_mm": 2, "margin_mm": 8, "desc": "紧凑设置"},
            {"spacing_mm": 1, "margin_mm": 5, "desc": "很紧凑设置"},
        ]
        
        print("间距(mm) | 页边距(mm) | 列数 | 总数 | 水平间距(px) | 描述")
        print("-" * 70)
        
        for case in test_cases:
            spacing_mm = case["spacing_mm"]
            margin_mm = case["margin_mm"]
            desc = case["desc"]
            
            compact_layout = layout_engine.calculate_compact_layout(spacing_mm, margin_mm)
            
            print(f"{spacing_mm:8} | {margin_mm:10} | {compact_layout['columns']:4} | {len(compact_layout['positions']):4} | {compact_layout['horizontal_spacing']:12.1f} | {desc}")
        
        # 详细分析一个案例
        print(f"\n=== 详细分析：紧凑设置 ===")
        spacing_mm = 2
        margin_mm = 8
        
        compact_layout = layout_engine.calculate_compact_layout(spacing_mm, margin_mm)
        positions = compact_layout['positions']
        
        print(f"布局参数:")
        print(f"  列数: {compact_layout['columns']}")
        print(f"  总位置数: {len(positions)}")
        print(f"  水平间距: {compact_layout['horizontal_spacing']:.1f}px")
        print(f"  垂直间距: {compact_layout['vertical_spacing']:.1f}px")
        print()
        
        # 分析列分布
        if positions:
            columns = {}
            for i, (x, y) in enumerate(positions):
                col_found = False
                for existing_x in columns.keys():
                    if abs(x - existing_x) < 10:
                        columns[existing_x].append((y, i))
                        col_found = True
                        break
                
                if not col_found:
                    columns[x] = [(y, i)]
            
            sorted_columns = sorted(columns.items())
            
            print(f"列分布:")
            for col_idx, (x, positions_in_col) in enumerate(sorted_columns):
                positions_in_col.sort()
                print(f"  第{col_idx+1}列 (X={x:.0f}): {len(positions_in_col)}个圆形")
            
            # 计算列间距
            if len(sorted_columns) > 1:
                actual_col_spacing = sorted_columns[1][0] - sorted_columns[0][0]
                print(f"\n实际列间距: {actual_col_spacing:.1f}px ({actual_col_spacing/mm_to_pixels(1):.1f}mm)")
                
                # 计算理论六边形列间距
                circle_diameter_px = layout_engine.badge_diameter_px
                theoretical_hex_spacing = circle_diameter_px * 0.866  # √3/2 ≈ 0.866
                print(f"理论六边形列间距: {theoretical_hex_spacing:.1f}px ({theoretical_hex_spacing/mm_to_pixels(1):.1f}mm)")
                print(f"当前列间距是理论值的: {actual_col_spacing/theoretical_hex_spacing:.2f}倍")
        
        # 恢复原始尺寸
        app_config.badge_diameter_mm = original_diameter_mm
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_32mm_layout()
