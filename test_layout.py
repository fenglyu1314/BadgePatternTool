#!/usr/bin/env python3
"""
测试排版算法的脚本
验证网格排版和密集排版是否正确
"""

import sys
import os
import math

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_layout_algorithms():
    """测试排版算法"""
    print("测试排版算法...")
    
    try:
        from core.layout_engine import LayoutEngine
        from utils.config import DEFAULT_SPACING, DEFAULT_MARGIN, BADGE_DIAMETER_PX
        
        layout_engine = LayoutEngine()
        
        # 测试网格排版
        print("\n=== 网格排版测试 ===")
        grid_layout = layout_engine.calculate_grid_layout(DEFAULT_SPACING, DEFAULT_MARGIN)
        print(f"网格排版 - 最大容量: {grid_layout['max_count']}")
        print(f"行数: {grid_layout['rows']}, 列数: {grid_layout['cols']}")
        print(f"位置数量: {len(grid_layout['positions'])}")
        
        # 验证网格排版中圆形不重叠
        positions = grid_layout['positions']
        min_distance = float('inf')
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                x1, y1 = positions[i]
                x2, y2 = positions[j]
                distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                min_distance = min(min_distance, distance)
        
        required_distance = BADGE_DIAMETER_PX  # 圆形直径
        print(f"网格排版 - 最小圆心距离: {min_distance:.1f}px")
        print(f"网格排版 - 要求最小距离: {required_distance}px")
        print(f"网格排版 - {'✓ 无重叠' if min_distance >= required_distance else '✗ 有重叠'}")
        
        # 测试密集排版
        print("\n=== 密集排版测试 ===")
        compact_layout = layout_engine.calculate_compact_layout(DEFAULT_SPACING, DEFAULT_MARGIN)
        print(f"密集排版 - 最大容量: {compact_layout['max_count']}")
        print(f"位置数量: {len(compact_layout['positions'])}")
        print(f"行间距: {compact_layout['row_offset_y']:.1f}px")
        print(f"圆心距离: {compact_layout['center_distance']:.1f}px")
        
        # 验证密集排版中圆形不重叠
        positions = compact_layout['positions']
        min_distance = float('inf')
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                x1, y1 = positions[i]
                x2, y2 = positions[j]
                distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                min_distance = min(min_distance, distance)
        
        print(f"密集排版 - 最小圆心距离: {min_distance:.1f}px")
        print(f"密集排版 - 要求最小距离: {required_distance}px")
        print(f"密集排版 - {'✓ 无重叠' if min_distance >= required_distance else '✗ 有重叠'}")
        
        # 比较效率
        print(f"\n=== 排版效率比较 ===")
        print(f"网格排版容量: {grid_layout['max_count']}")
        print(f"密集排版容量: {compact_layout['max_count']}")
        efficiency_gain = (compact_layout['max_count'] - grid_layout['max_count']) / grid_layout['max_count'] * 100
        print(f"密集排版效率提升: {efficiency_gain:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"✗ 排版算法测试失败: {e}")
        return False

def test_spacing_variations():
    """测试不同间距下的排版"""
    print("\n测试不同间距下的排版...")
    
    try:
        from core.layout_engine import LayoutEngine
        
        layout_engine = LayoutEngine()
        spacings = [0, 2, 5, 10]  # 不同间距值
        
        print("\n间距(mm) | 网格容量 | 密集容量 | 效率提升")
        print("-" * 45)
        
        for spacing in spacings:
            grid_layout = layout_engine.calculate_grid_layout(spacing, 15)
            compact_layout = layout_engine.calculate_compact_layout(spacing, 15)
            
            grid_count = grid_layout['max_count']
            compact_count = compact_layout['max_count']
            efficiency = (compact_count - grid_count) / grid_count * 100 if grid_count > 0 else 0
            
            print(f"{spacing:7} | {grid_count:8} | {compact_count:8} | {efficiency:6.1f}%")
        
        return True
        
    except Exception as e:
        print(f"✗ 间距变化测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("BadgePatternTool 排版算法测试")
    print("=" * 50)
    
    tests = [
        test_layout_algorithms,
        test_spacing_variations
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有排版算法测试通过！")
    else:
        print("❌ 部分测试失败，请检查算法。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
