#!/usr/bin/env python3
"""
测试布局间距问题
验证5mm间距时圆形是否重叠
"""

import sys
import os
import math

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_layout_spacing():
    """测试布局间距"""
    print("=== 布局间距测试 ===\n")
    
    try:
        from core.layout_engine import LayoutEngine
        from utils.config import BADGE_DIAMETER_PX, mm_to_pixels
        
        layout_engine = LayoutEngine()
        
        # 测试参数
        spacing_mm = 5
        margin_mm = 15
        
        print(f"圆形直径: {BADGE_DIAMETER_PX}px ({BADGE_DIAMETER_PX/mm_to_pixels(1):.1f}mm)")
        print(f"设定间距: {spacing_mm}mm ({mm_to_pixels(spacing_mm)}px)")
        print(f"页边距: {margin_mm}mm ({mm_to_pixels(margin_mm)}px)")
        print()
        
        # 测试紧凑布局
        compact_layout = layout_engine.calculate_compact_layout(spacing_mm, margin_mm)
        positions = compact_layout['positions']
        
        print("紧凑布局结果:")
        print(f"  总位置数: {len(positions)}")
        print(f"  圆心距离: {compact_layout['center_distance']:.1f}px")
        print(f"  垂直间距: {compact_layout['vertical_spacing']:.1f}px")
        print(f"  水平间距: {compact_layout['horizontal_spacing']:.1f}px")
        print()
        
        # 验证间距
        if len(positions) >= 2:
            print("距离验证:")
            radius_px = BADGE_DIAMETER_PX / 2
            min_required_distance = BADGE_DIAMETER_PX + mm_to_pixels(spacing_mm)
            
            print(f"  圆形半径: {radius_px}px")
            print(f"  最小圆心距离要求: {min_required_distance}px")
            print()
            
            # 检查相邻位置的距离
            overlaps = []
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    pos1 = positions[i]
                    pos2 = positions[j]
                    distance = math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)
                    
                    # 计算圆形边缘之间的实际间距
                    edge_distance = distance - BADGE_DIAMETER_PX
                    edge_distance_mm = edge_distance / mm_to_pixels(1)
                    
                    if distance < min_required_distance:
                        overlaps.append((i, j, distance, edge_distance_mm))
                    
                    # 只显示前几个距离用于调试
                    if len(overlaps) == 0 and j <= i + 3:
                        print(f"  位置{i+1}到位置{j+1}: 圆心距离={distance:.1f}px, 边缘间距={edge_distance_mm:.1f}mm")
            
            if overlaps:
                print(f"\n❌ 发现 {len(overlaps)} 对重叠的圆形:")
                for i, j, distance, edge_distance_mm in overlaps[:5]:  # 只显示前5个
                    print(f"  圆{i+1}和圆{j+1}: 圆心距离={distance:.1f}px, 边缘间距={edge_distance_mm:.1f}mm (重叠!)")
            else:
                print("\n✅ 没有发现重叠的圆形")
        
        # 分析行结构
        print(f"\n行结构分析:")
        rows = {}
        for i, (x, y) in enumerate(positions):
            if y not in rows:
                rows[y] = []
            rows[y].append((x, i))
        
        for row_idx, row_y in enumerate(sorted(rows.keys())):
            row_positions = sorted(rows[row_y])
            print(f"  第{row_idx+1}行 (Y={row_y}): {len(row_positions)}个圆形")
            
            # 检查同行圆形的水平间距
            if len(row_positions) > 1:
                for k in range(len(row_positions) - 1):
                    x1, idx1 = row_positions[k]
                    x2, idx2 = row_positions[k + 1]
                    h_distance = x2 - x1
                    h_edge_distance = h_distance - BADGE_DIAMETER_PX
                    h_edge_distance_mm = h_edge_distance / mm_to_pixels(1)
                    print(f"    圆{idx1+1}到圆{idx2+1}: 水平距离={h_distance:.1f}px, 边缘间距={h_edge_distance_mm:.1f}mm")
        
        return len(overlaps) == 0
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def calculate_ideal_hexagon_spacing():
    """计算理想的六边形间距"""
    print("\n=== 理想六边形间距计算 ===")
    
    from utils.config import BADGE_DIAMETER_PX, mm_to_pixels
    
    spacing_mm = 5
    spacing_px = mm_to_pixels(spacing_mm)
    
    # 理想的圆心距离应该是：圆形直径 + 间距
    ideal_center_distance = BADGE_DIAMETER_PX + spacing_px
    
    print(f"圆形直径: {BADGE_DIAMETER_PX}px")
    print(f"设定间距: {spacing_px}px")
    print(f"理想圆心距离: {ideal_center_distance}px")
    
    # 六边形布局的垂直间距
    vertical_spacing = ideal_center_distance * math.sqrt(3) / 2
    print(f"理想垂直间距: {vertical_spacing:.1f}px")
    
    # 行偏移
    row_offset = ideal_center_distance / 2
    print(f"理想行偏移: {row_offset:.1f}px")

if __name__ == "__main__":
    calculate_ideal_hexagon_spacing()
    print("\n" + "="*50)
    success = test_layout_spacing()
    if not success:
        print("\n需要修复布局算法以避免重叠")
