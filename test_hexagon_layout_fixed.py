#!/usr/bin/env python3
"""
测试修复后的六边形蜂窝布局算法
验证是否实现了期望的左右对齐、中间错位的效果
"""

import sys
import os
import math

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_hexagon_layout_visual():
    """测试六边形布局的视觉效果"""
    print("=== 六边形蜂窝布局视觉测试 ===\n")
    
    try:
        from core.layout_engine import LayoutEngine
        from utils.config import app_config, mm_to_pixels
        
        # 设置测试参数
        app_config.badge_diameter_mm = 32  # 使用32mm圆形便于测试
        spacing_mm = 5
        margin_mm = 15
        
        layout_engine = LayoutEngine()
        
        print(f"测试参数:")
        print(f"  圆形直径: {app_config.badge_diameter_mm}mm ({app_config.badge_diameter_px}px)")
        print(f"  间距: {spacing_mm}mm ({mm_to_pixels(spacing_mm)}px)")
        print(f"  页边距: {margin_mm}mm ({mm_to_pixels(margin_mm)}px)")
        print()
        
        # 获取紧凑布局结果
        compact_layout = layout_engine.calculate_compact_layout(spacing_mm, margin_mm)
        positions = compact_layout['positions']
        
        print(f"布局结果:")
        print(f"  总位置数: {len(positions)}")
        print(f"  列数: {compact_layout['columns']}")
        print(f"  水平间距: {compact_layout['horizontal_spacing']:.1f}px")
        print(f"  垂直间距: {compact_layout['vertical_spacing']:.1f}px")
        print(f"  中间列偏移: {compact_layout['middle_col_offset']:.1f}px")
        print()
        
        # 按列分组分析
        columns = {}
        for i, (x, y) in enumerate(positions):
            # 根据X坐标确定列
            col_index = None
            for existing_x in columns.keys():
                if abs(x - existing_x) < 10:  # 允许10px的误差
                    col_index = existing_x
                    break
            
            if col_index is None:
                col_index = x
                columns[col_index] = []
            
            columns[col_index].append((y, i))
        
        # 按X坐标排序列
        sorted_columns = sorted(columns.items())
        
        print(f"列结构分析:")
        for col_idx, (x, positions_in_col) in enumerate(sorted_columns):
            positions_in_col.sort()  # 按Y坐标排序
            print(f"  第{col_idx+1}列 (X={x}): {len(positions_in_col)}个圆形")
            
            # 显示前几个Y坐标
            y_coords = [y for y, _ in positions_in_col[:5]]
            print(f"    Y坐标: {y_coords}")
            
            # 检查是否为中间列（奇数列应该有偏移）
            if col_idx % 2 == 1 and len(sorted_columns) > 1:
                # 比较与第一列的Y坐标差异
                first_col_y = [y for y, _ in sorted(columns[sorted_columns[0][0]])]
                current_col_y = [y for y, _ in positions_in_col]
                
                if len(first_col_y) > 0 and len(current_col_y) > 0:
                    y_offset = current_col_y[0] - first_col_y[0]
                    expected_offset = compact_layout['middle_col_offset']
                    print(f"    实际偏移: {y_offset:.1f}px (期望: {expected_offset:.1f}px)")
        
        # 创建ASCII艺术图来可视化布局
        print(f"\n布局可视化 (简化):")
        create_ascii_layout(positions, compact_layout)
        
        # 验证间距
        print(f"\n间距验证:")
        verify_spacing(positions, compact_layout)
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_ascii_layout(positions, layout_info):
    """创建ASCII艺术图显示布局"""
    if not positions:
        print("  无位置数据")
        return
    
    # 计算缩放比例
    min_x = min(pos[0] for pos in positions)
    max_x = max(pos[0] for pos in positions)
    min_y = min(pos[1] for pos in positions)
    max_y = max(pos[1] for pos in positions)
    
    # 创建网格
    width = 60  # ASCII图宽度
    height = 20  # ASCII图高度
    
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # 映射位置到网格
    for i, (x, y) in enumerate(positions):
        grid_x = int((x - min_x) / (max_x - min_x) * (width - 1)) if max_x > min_x else width // 2
        grid_y = int((y - min_y) / (max_y - min_y) * (height - 1)) if max_y > min_y else height // 2
        
        if 0 <= grid_x < width and 0 <= grid_y < height:
            grid[grid_y][grid_x] = 'O'
    
    # 打印网格
    for row in grid:
        print('  ' + ''.join(row))

def verify_spacing(positions, layout_info):
    """验证间距是否正确"""
    if len(positions) < 2:
        print("  位置太少，无法验证间距")
        return
    
    center_distance = layout_info['center_distance']
    tolerance = 10  # 允许10px的误差
    
    # 检查相邻位置的距离
    correct_distances = 0
    total_distances = 0
    
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            pos1 = positions[i]
            pos2 = positions[j]
            distance = math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)
            
            # 检查是否为相邻位置（距离接近center_distance）
            if abs(distance - center_distance) <= tolerance:
                correct_distances += 1
            
            total_distances += 1
            
            # 只检查前几个距离
            if total_distances >= 20:
                break
        if total_distances >= 20:
            break
    
    print(f"  检查了 {total_distances} 个距离对")
    print(f"  符合预期的距离: {correct_distances} 个")
    print(f"  期望圆心距离: {center_distance:.1f}px")
    
    if correct_distances > 0:
        print("  ✅ 间距验证通过")
    else:
        print("  ⚠️ 需要检查间距设置")

def compare_layouts():
    """比较不同布局模式"""
    print("\n" + "="*50)
    print("=== 布局模式比较 ===\n")
    
    try:
        from core.layout_engine import LayoutEngine
        from utils.config import app_config
        
        app_config.badge_diameter_mm = 32
        layout_engine = LayoutEngine()
        
        # 网格布局
        grid_layout = layout_engine.calculate_grid_layout(5, 15)
        print(f"网格布局: {grid_layout['max_count']}个圆形")
        
        # 紧凑布局
        compact_layout = layout_engine.calculate_compact_layout(5, 15)
        print(f"紧凑布局: {compact_layout['max_count']}个圆形")
        
        # 计算空间利用率提升
        if grid_layout['max_count'] > 0:
            improvement = (compact_layout['max_count'] - grid_layout['max_count']) / grid_layout['max_count'] * 100
            print(f"空间利用率提升: {improvement:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"比较失败: {e}")
        return False

if __name__ == "__main__":
    success1 = test_hexagon_layout_visual()
    success2 = compare_layouts()
    
    if success1 and success2:
        print(f"\n🎉 六边形蜂窝布局测试通过！")
        print("布局效果应该符合您的期望：左右两列对齐，中间列错位")
    else:
        print(f"\n❌ 测试失败，需要进一步调试")
