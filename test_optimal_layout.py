#!/usr/bin/env python3
"""
测试最优布局设置
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_optimal_layout():
    """测试最优布局设置"""
    print("=== 测试最优布局设置 ===\n")
    
    try:
        from core.layout_engine import LayoutEngine
        from utils.config import BADGE_DIAMETER_PX, A4_WIDTH_PX, A4_HEIGHT_PX, mm_to_pixels
        
        layout_engine = LayoutEngine()
        
        # 使用最优设置
        spacing_mm = 0
        margin_mm = 3
        
        print(f"最优设置:")
        print(f"  间距: {spacing_mm}mm")
        print(f"  页边距: {margin_mm}mm")
        print()
        
        # 计算紧凑布局
        compact_layout = layout_engine.calculate_compact_layout(spacing_mm, margin_mm)
        
        print(f"布局结果:")
        print(f"  总位置数: {len(compact_layout['positions'])}")
        print(f"  列数: {compact_layout['columns']}")
        print(f"  水平间距: {compact_layout['horizontal_spacing']:.1f}px")
        print(f"  垂直间距: {compact_layout['vertical_spacing']:.1f}px")
        print(f"  中间列偏移: {compact_layout['middle_col_offset']:.1f}px")
        print()
        
        # 分析位置分布
        positions = compact_layout['positions']
        if positions:
            print(f"位置详情:")
            
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
            
            for col_idx, (x, positions_in_col) in enumerate(sorted_columns):
                positions_in_col.sort()
                print(f"  第{col_idx+1}列 (X={x:.0f}): {len(positions_in_col)}个圆形")
                
                # 显示Y坐标
                y_coords = [y for y, _ in positions_in_col]
                print(f"    Y坐标: {[int(y) for y in y_coords]}")
                
                # 检查是否为中间列（奇数列应该有偏移）
                if col_idx % 2 == 1 and len(sorted_columns) > 1:
                    first_col_y = [y for y, _ in sorted(columns[sorted_columns[0][0]])]
                    current_col_y = [y for y, _ in positions_in_col]
                    
                    if len(first_col_y) > 0 and len(current_col_y) > 0:
                        y_offset = current_col_y[0] - first_col_y[0]
                        expected_offset = compact_layout['middle_col_offset']
                        print(f"    实际偏移: {y_offset:.1f}px (期望: {expected_offset:.1f}px)")
        
        # 检查重叠
        print(f"\n重叠检查:")
        min_distance = float('inf')
        overlap_pairs = []
        
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                x1, y1 = positions[i]
                x2, y2 = positions[j]
                distance = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
                min_distance = min(min_distance, distance)
                
                if distance < BADGE_DIAMETER_PX:
                    overlap_pairs.append((i, j, distance))
        
        print(f"  最小距离: {min_distance:.1f}px")
        print(f"  圆形直径: {BADGE_DIAMETER_PX}px")
        print(f"  重叠情况: {'有重叠' if min_distance < BADGE_DIAMETER_PX else '无重叠'}")
        
        if overlap_pairs:
            print(f"  重叠对数: {len(overlap_pairs)}")
            for i, j, dist in overlap_pairs[:3]:  # 只显示前3个
                print(f"    位置{i+1}和位置{j+1}: 距离{dist:.1f}px")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_optimal_layout()
