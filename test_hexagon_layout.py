#!/usr/bin/env python3
"""
测试六边形蜂巢布局算法
验证相邻圆形距离是否相等
"""

import sys
import os
import math

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_hexagon_layout():
    """测试六边形布局算法"""
    print("=== 六边形蜂巢布局算法测试 ===\n")
    
    try:
        from core.layout_engine import LayoutEngine
        from utils.config import DEFAULT_SPACING, DEFAULT_MARGIN, BADGE_DIAMETER_PX
        
        layout_engine = LayoutEngine()
        
        # 获取紧凑排版结果
        compact_layout = layout_engine.calculate_compact_layout(DEFAULT_SPACING, DEFAULT_MARGIN)
        positions = compact_layout['positions']
        
        print(f"圆形直径: {BADGE_DIAMETER_PX}px")
        print(f"设定间距: {DEFAULT_SPACING}mm")
        print(f"圆心距离: {compact_layout['center_distance']}px")
        print(f"垂直间距: {compact_layout['vertical_spacing']:.1f}px")
        print(f"水平间距: {compact_layout['horizontal_spacing']:.1f}px")
        print(f"行偏移: {compact_layout['row_offset']:.1f}px")
        print(f"总位置数: {len(positions)}")
        print()
        
        # 验证距离计算
        if len(positions) >= 7:  # 至少需要7个位置来验证六边形结构
            center_pos = positions[0]  # 取第一个位置作为中心
            print(f"验证中心位置: {center_pos}")
            
            # 计算与其他位置的距离
            distances = []
            for i, pos in enumerate(positions[1:7], 1):  # 检查前6个相邻位置
                if i < len(positions):
                    distance = math.sqrt((pos[0] - center_pos[0])**2 + (pos[1] - center_pos[1])**2)
                    distances.append(distance)
                    print(f"到位置{i} {pos} 的距离: {distance:.1f}px")
            
            # 检查距离是否相等（允许1px的误差）
            if distances:
                avg_distance = sum(distances) / len(distances)
                max_diff = max(abs(d - avg_distance) for d in distances)
                print(f"\n平均距离: {avg_distance:.1f}px")
                print(f"最大偏差: {max_diff:.1f}px")
                
                if max_diff <= 1.0:
                    print("✅ 距离验证通过：相邻圆形距离基本相等")
                else:
                    print("❌ 距离验证失败：相邻圆形距离差异过大")
        
        # 打印前20个位置用于可视化验证
        print(f"\n前20个圆心位置:")
        for i, (x, y) in enumerate(positions[:20]):
            row = i // 10  # 假设每行最多10个
            print(f"圆{i+1:2d}: ({x:4d}, {y:4d})", end="  ")
            if (i + 1) % 5 == 0:  # 每5个换行
                print()
        print()
        
        # 分析行结构
        print("\n行结构分析:")
        rows = {}
        for i, (x, y) in enumerate(positions):
            if y not in rows:
                rows[y] = []
            rows[y].append((x, i))
        
        for row_y in sorted(rows.keys())[:5]:  # 只显示前5行
            row_positions = sorted(rows[row_y])
            print(f"Y={row_y}: {len(row_positions)}个圆形")
            for x, idx in row_positions[:8]:  # 每行最多显示8个
                print(f"  圆{idx+1}(X={x})", end="")
            print()
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def calculate_theoretical_distances():
    """计算理论上的六边形距离"""
    print("\n=== 六边形几何理论验证 ===")
    
    # 假设圆心距离为100px
    center_distance = 100
    
    print(f"设定圆心距离: {center_distance}px")
    
    # 六边形中心到顶点的距离
    print(f"水平相邻距离: {center_distance}px")
    
    # 对角相邻距离（60度角）
    diagonal_distance = center_distance
    print(f"对角相邻距离: {diagonal_distance}px")
    
    # 垂直行间距
    vertical_spacing = center_distance * math.sqrt(3) / 2
    print(f"垂直行间距: {vertical_spacing:.1f}px")
    
    # 行偏移
    row_offset = center_distance / 2
    print(f"行偏移: {row_offset:.1f}px")
    
    print("\n在完美的六边形密排中，所有相邻圆形的距离都应该等于设定的圆心距离")

if __name__ == "__main__":
    calculate_theoretical_distances()
    print("\n" + "="*50)
    test_hexagon_layout()
