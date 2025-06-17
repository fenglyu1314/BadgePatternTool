#!/usr/bin/env python3
"""
调试排版算法的脚本
详细分析密集排版中的位置坐标
"""

import sys
import os
import math

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_compact_layout():
    """调试密集排版算法"""
    print("调试密集排版算法...")
    
    try:
        from core.layout_engine import LayoutEngine
        from utils.config import DEFAULT_SPACING, DEFAULT_MARGIN, BADGE_DIAMETER_PX
        
        layout_engine = LayoutEngine()
        
        # 获取密集排版结果
        compact_layout = layout_engine.calculate_compact_layout(DEFAULT_SPACING, DEFAULT_MARGIN)
        positions = compact_layout['positions']
        
        print(f"圆形直径: {BADGE_DIAMETER_PX}px")
        print(f"圆心距离: {compact_layout['center_distance']}px")
        print(f"行间距: {compact_layout['row_offset_y']:.1f}px")
        print(f"总位置数: {len(positions)}")
        print()
        
        # 打印所有位置
        print("所有圆心位置:")
        for i, (x, y) in enumerate(positions):
            print(f"圆{i+1}: ({x}, {y})")
        print()
        
        # 计算所有距离
        print("圆心之间的距离:")
        min_distance = float('inf')
        min_pair = None
        
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                x1, y1 = positions[i]
                x2, y2 = positions[j]
                distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                
                print(f"圆{i+1} -> 圆{j+1}: {distance:.1f}px")
                
                if distance < min_distance:
                    min_distance = distance
                    min_pair = (i+1, j+1)
        
        print()
        print(f"最小距离: {min_distance:.1f}px (圆{min_pair[0]} -> 圆{min_pair[1]})")
        print(f"要求最小距离: {BADGE_DIAMETER_PX}px")
        print(f"是否重叠: {'是' if min_distance < BADGE_DIAMETER_PX else '否'}")
        
        # 分析行结构
        print("\n行结构分析:")
        y_positions = sorted(set(y for x, y in positions))
        for i, y in enumerate(y_positions):
            row_positions = [(x, y) for x, y in positions if y == y]
            row_positions.sort()
            print(f"第{i+1}行 (y={y}): {len(row_positions)}个圆")
            for j, (x, y) in enumerate(row_positions):
                print(f"  圆{j+1}: x={x}")
        
        return True
        
    except Exception as e:
        print(f"调试失败: {e}")
        return False

def main():
    """主函数"""
    print("BadgePatternTool 密集排版调试")
    print("=" * 50)
    
    debug_compact_layout()

if __name__ == "__main__":
    main()
