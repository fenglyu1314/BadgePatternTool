#!/usr/bin/env python3
"""
测试优化的间距设置
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_optimized_spacing():
    """测试优化的间距设置"""
    print("=== 测试优化的间距设置 ===\n")
    
    try:
        from core.layout_engine import LayoutEngine
        from utils.config import BADGE_DIAMETER_PX, A4_WIDTH_PX, A4_HEIGHT_PX, mm_to_pixels
        
        layout_engine = LayoutEngine()
        
        # 测试不同的间距和页边距组合
        test_cases = [
            {"spacing_mm": 5, "margin_mm": 15, "desc": "当前设置"},
            {"spacing_mm": 3, "margin_mm": 15, "desc": "减少间距"},
            {"spacing_mm": 5, "margin_mm": 10, "desc": "减少页边距"},
            {"spacing_mm": 3, "margin_mm": 10, "desc": "减少间距和页边距"},
            {"spacing_mm": 2, "margin_mm": 8, "desc": "最小间距和页边距"},
            {"spacing_mm": 1, "margin_mm": 5, "desc": "极小间距和页边距"},
            {"spacing_mm": 0, "margin_mm": 3, "desc": "零间距极小页边距"},
        ]
        
        print("间距(mm) | 页边距(mm) | 网格容量 | 紧凑容量 | 描述")
        print("-" * 60)
        
        best_compact = 0
        best_settings = None
        
        for case in test_cases:
            spacing_mm = case["spacing_mm"]
            margin_mm = case["margin_mm"]
            desc = case["desc"]
            
            # 计算网格布局
            grid_layout = layout_engine.calculate_grid_layout(spacing_mm, margin_mm)
            grid_count = grid_layout['max_count']
            
            # 计算紧凑布局
            compact_layout = layout_engine.calculate_compact_layout(spacing_mm, margin_mm)
            compact_count = compact_layout['max_count']
            
            print(f"{spacing_mm:8} | {margin_mm:10} | {grid_count:8} | {compact_count:8} | {desc}")
            
            if compact_count > best_compact:
                best_compact = compact_count
                best_settings = case
        
        print(f"\n最佳设置: {best_settings['desc']}")
        print(f"最大容量: {best_compact} 个圆形")
        
        # 详细分析最佳设置
        if best_settings:
            print(f"\n=== 最佳设置详细分析 ===")
            spacing_mm = best_settings["spacing_mm"]
            margin_mm = best_settings["margin_mm"]
            
            compact_layout = layout_engine.calculate_compact_layout(spacing_mm, margin_mm)
            
            print(f"间距: {spacing_mm}mm")
            print(f"页边距: {margin_mm}mm")
            print(f"列数: {compact_layout['columns']}")
            print(f"水平间距: {compact_layout['horizontal_spacing']:.1f}px")
            print(f"垂直间距: {compact_layout['vertical_spacing']:.1f}px")
            print(f"总位置数: {len(compact_layout['positions'])}")
            
            # 分析位置分布
            positions = compact_layout['positions']
            if positions:
                # 按列分组
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
                
                # 按X坐标排序
                sorted_columns = sorted(columns.items())
                
                print(f"\n列分布:")
                for col_idx, (x, positions_in_col) in enumerate(sorted_columns):
                    positions_in_col.sort()
                    print(f"  第{col_idx+1}列: {len(positions_in_col)}个圆形")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_optimized_spacing()
