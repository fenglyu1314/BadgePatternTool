#!/usr/bin/env python3
"""
测试两种排版方式的间距一致性
"""

import sys
import os
import math

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_spacing_consistency():
    """测试两种排版方式的间距一致性"""
    print("测试两种排版方式的间距一致性...")
    
    try:
        from core.layout_engine import LayoutEngine
        from utils.config import BADGE_DIAMETER_PX
        
        layout_engine = LayoutEngine()
        
        # 测试不同间距值
        spacings = [0, 2, 5, 10]
        
        print("\n间距一致性测试结果:")
        print("间距(mm) | 网格最小距离 | 密集最小距离 | 差异 | 一致性")
        print("-" * 65)
        
        for spacing in spacings:
            # 计算网格排版
            grid_layout = layout_engine.calculate_grid_layout(spacing, 15)
            grid_positions = grid_layout['positions']
            
            # 计算密集排版
            compact_layout = layout_engine.calculate_compact_layout(spacing, 15)
            compact_positions = compact_layout['positions']
            
            # 计算网格排版的最小距离
            grid_min_distance = float('inf')
            for i in range(len(grid_positions)):
                for j in range(i + 1, len(grid_positions)):
                    x1, y1 = grid_positions[i]
                    x2, y2 = grid_positions[j]
                    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                    grid_min_distance = min(grid_min_distance, distance)
            
            # 计算密集排版的最小距离
            compact_min_distance = float('inf')
            for i in range(len(compact_positions)):
                for j in range(i + 1, len(compact_positions)):
                    x1, y1 = compact_positions[i]
                    x2, y2 = compact_positions[j]
                    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                    compact_min_distance = min(compact_min_distance, distance)
            
            # 计算差异
            difference = abs(grid_min_distance - compact_min_distance)
            consistency = "一致" if difference < 50 else "不一致"  # 50px容差
            
            print(f"{spacing:7} | {grid_min_distance:11.1f} | {compact_min_distance:11.1f} | {difference:4.1f} | {consistency}")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def analyze_actual_spacing():
    """分析实际间距与设定间距的关系"""
    print("\n分析实际间距与设定间距的关系...")
    
    try:
        from core.layout_engine import LayoutEngine
        from utils.config import BADGE_DIAMETER_PX, mm_to_pixels
        
        layout_engine = LayoutEngine()
        
        spacings = [0, 2, 5, 10]
        
        print("\n实际间距分析:")
        print("设定间距(mm) | 设定间距(px) | 网格实际间距 | 密集实际间距 | 理论最小距离")
        print("-" * 80)
        
        for spacing_mm in spacings:
            spacing_px = mm_to_pixels(spacing_mm)
            theoretical_min = BADGE_DIAMETER_PX + spacing_px
            
            # 网格排版
            grid_layout = layout_engine.calculate_grid_layout(spacing_mm, 15)
            grid_positions = grid_layout['positions']
            
            grid_min_distance = float('inf')
            for i in range(len(grid_positions)):
                for j in range(i + 1, len(grid_positions)):
                    x1, y1 = grid_positions[i]
                    x2, y2 = grid_positions[j]
                    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                    grid_min_distance = min(grid_min_distance, distance)
            
            # 密集排版
            compact_layout = layout_engine.calculate_compact_layout(spacing_mm, 15)
            compact_positions = compact_layout['positions']
            
            compact_min_distance = float('inf')
            for i in range(len(compact_positions)):
                for j in range(i + 1, len(compact_positions)):
                    x1, y1 = compact_positions[i]
                    x2, y2 = compact_positions[j]
                    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                    compact_min_distance = min(compact_min_distance, distance)
            
            grid_actual_spacing = grid_min_distance - BADGE_DIAMETER_PX
            compact_actual_spacing = compact_min_distance - BADGE_DIAMETER_PX
            
            print(f"{spacing_mm:11} | {spacing_px:11.1f} | {grid_actual_spacing:13.1f} | {compact_actual_spacing:15.1f} | {theoretical_min:13.1f}")
        
        return True
        
    except Exception as e:
        print(f"分析失败: {e}")
        return False

def main():
    """主函数"""
    print("BadgePatternTool 间距一致性测试")
    print("=" * 50)
    
    test_spacing_consistency()
    analyze_actual_spacing()

if __name__ == "__main__":
    main()
