#!/usr/bin/env python3
"""
测试不同间距下的排版效果
"""

import sys
import os
import math

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_spacing_detailed():
    """详细测试不同间距下的排版"""
    print("详细测试不同间距下的排版...")
    
    try:
        from core.layout_engine import LayoutEngine
        from utils.config import BADGE_DIAMETER_PX
        
        layout_engine = LayoutEngine()
        
        # 测试更多间距值
        spacings = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        print("\n详细间距测试结果:")
        print("间距(mm) | 网格容量 | 密集容量 | 最小距离 | 重叠状态 | 效率提升")
        print("-" * 75)
        
        for spacing in spacings:
            grid_layout = layout_engine.calculate_grid_layout(spacing, 15)
            compact_layout = layout_engine.calculate_compact_layout(spacing, 15)
            
            grid_count = grid_layout['max_count']
            compact_count = compact_layout['max_count']
            efficiency = (compact_count - grid_count) / grid_count * 100 if grid_count > 0 else 0
            
            # 计算密集排版的最小距离
            positions = compact_layout['positions']
            min_distance = float('inf')
            
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    x1, y1 = positions[i]
                    x2, y2 = positions[j]
                    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                    min_distance = min(min_distance, distance)
            
            required_distance = BADGE_DIAMETER_PX
            overlap_status = "重叠" if min_distance < required_distance else "正常"
            
            print(f"{spacing:7} | {grid_count:8} | {compact_count:8} | {min_distance:8.1f} | {overlap_status:6} | {efficiency:6.1f}%")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def analyze_safety_factor():
    """分析安全系数的影响"""
    print("\n分析安全系数的影响...")
    
    try:
        from core.layout_engine import LayoutEngine
        from utils.config import BADGE_DIAMETER_PX, DEFAULT_SPACING
        
        # 临时修改安全系数进行测试
        layout_engine = LayoutEngine()
        
        # 测试不同的安全系数
        safety_factors = [1.0, 1.02, 1.05, 1.08, 1.1, 1.15]
        
        print("\n安全系数影响分析:")
        print("安全系数 | 圆心距离 | 最小距离 | 容量 | 重叠状态")
        print("-" * 55)
        
        for factor in safety_factors:
            # 临时修改算法中的安全系数
            original_method = layout_engine.calculate_compact_layout
            
            def modified_compact_layout(spacing_mm=DEFAULT_SPACING, margin_mm=15):
                import math
                from utils.config import mm_to_pixels
                
                spacing_px = mm_to_pixels(spacing_mm)
                margin_px = mm_to_pixels(margin_mm)
                available_width = layout_engine.a4_width_px - 2 * margin_px
                
                min_distance = BADGE_DIAMETER_PX + spacing_px
                center_distance = min_distance * factor  # 使用测试的安全系数
                
                row_offset_y = center_distance * math.sqrt(3) / 2
                col_offset_x = center_distance / 2
                
                positions = []
                row = 0
                y = margin_px + layout_engine.badge_radius_px
                
                while y + layout_engine.badge_radius_px <= layout_engine.a4_height_px - margin_px:
                    if row % 2 == 0:
                        current_col_offset = 0
                    else:
                        current_col_offset = col_offset_x
                    
                    available_row_width = available_width - current_col_offset
                    cols_in_row = max(0, int(available_row_width // center_distance))
                    
                    if cols_in_row > 0:
                        total_row_width = cols_in_row * center_distance
                        start_x = margin_px + current_col_offset + (available_row_width - total_row_width) / 2
                        
                        for col in range(cols_in_row):
                            x = start_x + col * center_distance + layout_engine.badge_radius_px
                            if (x - layout_engine.badge_radius_px >= margin_px and 
                                x + layout_engine.badge_radius_px <= layout_engine.a4_width_px - margin_px):
                                positions.append((int(x), int(y)))
                    
                    row += 1
                    y += row_offset_y
                
                return {
                    'type': 'compact',
                    'positions': positions,
                    'max_count': len(positions),
                    'center_distance': center_distance
                }
            
            # 使用修改后的方法
            layout_engine.calculate_compact_layout = modified_compact_layout
            
            compact_layout = layout_engine.calculate_compact_layout(2, 15)  # 使用2mm间距测试
            positions = compact_layout['positions']
            center_distance = compact_layout['center_distance']
            
            # 计算最小距离
            min_distance = float('inf')
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    x1, y1 = positions[i]
                    x2, y2 = positions[j]
                    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                    min_distance = min(min_distance, distance)
            
            required_distance = BADGE_DIAMETER_PX
            overlap_status = "重叠" if min_distance < required_distance else "正常"
            
            print(f"{factor:8.2f} | {center_distance:8.1f} | {min_distance:8.1f} | {len(positions):4} | {overlap_status}")
            
            # 恢复原方法
            layout_engine.calculate_compact_layout = original_method
        
        return True
        
    except Exception as e:
        print(f"分析失败: {e}")
        return False

def main():
    """主函数"""
    print("BadgePatternTool 间距详细测试")
    print("=" * 50)
    
    test_spacing_detailed()
    analyze_safety_factor()

if __name__ == "__main__":
    main()
