#!/usr/bin/env python3
"""
测试六边形布局容量
验证A4纸能否按4-3-4模式放置11个68mm圆形
"""

import sys
import os
import math

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def calculate_theoretical_capacity():
    """计算理论容量"""
    print("=== A4纸六边形布局理论计算 ===\n")
    
    from utils.config import A4_WIDTH_MM, A4_HEIGHT_MM, mm_to_pixels
    
    # 参数
    circle_diameter_mm = 68
    spacing_mm = 5
    margin_mm = 15
    
    print(f"A4纸尺寸: {A4_WIDTH_MM}mm × {A4_HEIGHT_MM}mm")
    print(f"圆形直径: {circle_diameter_mm}mm")
    print(f"间距: {spacing_mm}mm")
    print(f"页边距: {margin_mm}mm")
    print()
    
    # 可用区域
    available_width = A4_WIDTH_MM - 2 * margin_mm
    available_height = A4_HEIGHT_MM - 2 * margin_mm
    
    print(f"可用区域: {available_width}mm × {available_height}mm")
    
    # 圆心之间的距离
    center_distance = circle_diameter_mm + spacing_mm
    print(f"圆心距离: {center_distance}mm")
    
    # 网格排列容量
    grid_cols = int(available_width // center_distance)
    grid_rows = int(available_height // center_distance)
    grid_total = grid_cols * grid_rows
    
    print(f"\n网格排列:")
    print(f"  列数: {grid_cols}")
    print(f"  行数: {grid_rows}")
    print(f"  总数: {grid_total}")
    
    # 六边形排列容量（理论）
    # 第一行：4个圆形
    # 第二行：3个圆形（偏移半个间距）
    # 第三行：4个圆形
    # 总共：11个圆形
    
    print(f"\n六边形排列（4-3-4模式）:")
    
    # 计算第一行4个圆形需要的宽度
    row1_width = 4 * center_distance - spacing_mm  # 最后一个圆形不需要额外间距
    print(f"  第1行宽度需求: {row1_width}mm (4个圆形)")
    
    # 计算第二行3个圆形需要的宽度（偏移center_distance/2）
    row2_offset = center_distance / 2
    row2_width = 3 * center_distance - spacing_mm + row2_offset
    print(f"  第2行宽度需求: {row2_width}mm (3个圆形，偏移{row2_offset}mm)")
    
    # 计算第三行4个圆形需要的宽度
    row3_width = row1_width
    print(f"  第3行宽度需求: {row3_width}mm (4个圆形)")
    
    max_width_needed = max(row1_width, row2_width, row3_width)
    print(f"  最大宽度需求: {max_width_needed}mm")
    
    # 计算高度需求
    # 使用标准六边形垂直间距
    hex_vertical_spacing = center_distance * math.sqrt(3) / 2
    total_height_hex = 3 * hex_vertical_spacing - hex_vertical_spacing + circle_diameter_mm
    
    print(f"  六边形垂直间距: {hex_vertical_spacing:.1f}mm")
    print(f"  总高度需求(六边形): {total_height_hex:.1f}mm")
    
    # 使用我们修正后的垂直间距（等于center_distance）
    corrected_vertical_spacing = center_distance
    total_height_corrected = 3 * corrected_vertical_spacing - corrected_vertical_spacing + circle_diameter_mm
    
    print(f"  修正垂直间距: {corrected_vertical_spacing}mm")
    print(f"  总高度需求(修正): {total_height_corrected}mm")
    
    print(f"\n可行性分析:")
    print(f"  可用宽度: {available_width}mm")
    print(f"  需要宽度: {max_width_needed}mm")
    print(f"  宽度余量: {available_width - max_width_needed:.1f}mm")
    
    print(f"  可用高度: {available_height}mm")
    print(f"  需要高度(六边形): {total_height_hex:.1f}mm")
    print(f"  高度余量(六边形): {available_height - total_height_hex:.1f}mm")
    
    print(f"  需要高度(修正): {total_height_corrected}mm")
    print(f"  高度余量(修正): {available_height - total_height_corrected:.1f}mm")
    
    # 结论
    width_ok = available_width >= max_width_needed
    height_hex_ok = available_height >= total_height_hex
    height_corrected_ok = available_height >= total_height_corrected
    
    print(f"\n结论:")
    print(f"  宽度可行: {'✅' if width_ok else '❌'}")
    print(f"  高度可行(六边形): {'✅' if height_hex_ok else '❌'}")
    print(f"  高度可行(修正): {'✅' if height_corrected_ok else '❌'}")
    
    if width_ok and height_hex_ok:
        print("  ✅ 理论上可以使用六边形布局放置11个圆形")
        return True, "hexagon"
    elif width_ok and height_corrected_ok:
        print("  ✅ 可以使用修正布局放置11个圆形")
        return True, "corrected"
    else:
        print("  ❌ 无法放置11个圆形")
        return False, None

def test_current_algorithm():
    """测试当前算法"""
    print("\n" + "="*50)
    print("=== 当前算法测试 ===\n")
    
    try:
        from core.layout_engine import LayoutEngine
        
        layout_engine = LayoutEngine()
        
        # 测试紧凑布局
        compact_layout = layout_engine.calculate_compact_layout(5, 15)
        positions = compact_layout['positions']
        
        print(f"当前算法结果:")
        print(f"  总位置数: {len(positions)}")
        print(f"  圆心距离: {compact_layout['center_distance']}px")
        print(f"  垂直间距: {compact_layout['vertical_spacing']}px")
        print(f"  水平间距: {compact_layout['horizontal_spacing']}px")
        
        # 分析行结构
        rows = {}
        for i, (x, y) in enumerate(positions):
            if y not in rows:
                rows[y] = []
            rows[y].append((x, i))
        
        print(f"\n行结构:")
        for row_idx, row_y in enumerate(sorted(rows.keys())):
            row_positions = sorted(rows[row_y])
            print(f"  第{row_idx+1}行: {len(row_positions)}个圆形")
        
        return len(positions)
        
    except Exception as e:
        print(f"测试失败: {e}")
        return 0

if __name__ == "__main__":
    feasible, layout_type = calculate_theoretical_capacity()
    current_count = test_current_algorithm()
    
    print(f"\n" + "="*50)
    print("总结:")
    print(f"  理论可行: {'是' if feasible else '否'} ({layout_type if feasible else 'N/A'})")
    print(f"  当前算法: {current_count}个圆形")
    print(f"  目标: 11个圆形")
    
    if current_count < 11:
        print(f"  需要优化算法以增加 {11 - current_count} 个位置")
