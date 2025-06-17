#!/usr/bin/env python3
"""
详细调试紧凑排布算法
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_detailed():
    """详细调试"""
    print("=== 详细调试紧凑排布算法 ===\n")
    
    try:
        from core.layout_engine import LayoutEngine
        from utils.config import BADGE_DIAMETER_PX, A4_WIDTH_PX, A4_HEIGHT_PX, mm_to_pixels
        
        # 参数
        spacing_mm = 5
        margin_mm = 15
        spacing_px = mm_to_pixels(spacing_mm)
        margin_px = mm_to_pixels(margin_mm)
        
        print(f"基本参数:")
        print(f"  A4尺寸: {A4_WIDTH_PX}px × {A4_HEIGHT_PX}px")
        print(f"  圆形直径: {BADGE_DIAMETER_PX}px")
        print(f"  间距: {spacing_mm}mm = {spacing_px}px")
        print(f"  页边距: {margin_mm}mm = {margin_px}px")
        print()
        
        # 可用区域
        available_width = A4_WIDTH_PX - 2 * margin_px
        available_height = A4_HEIGHT_PX - 2 * margin_px
        
        print(f"可用区域:")
        print(f"  宽度: {available_width}px")
        print(f"  高度: {available_height}px")
        print()
        
        # 手动计算列数
        print("=== 手动计算列数 ===")
        for test_cols in range(1, 5):
            print(f"\n测试 {test_cols} 列:")
            
            if test_cols == 1:
                total_width_needed = BADGE_DIAMETER_PX
                print(f"  需要宽度: {total_width_needed}px")
            else:
                # 计算实际可用的水平空间（减去圆形直径）
                available_for_spacing = available_width - test_cols * BADGE_DIAMETER_PX
                print(f"  可用于间距的空间: {available_for_spacing}px")
                
                if available_for_spacing < 0:
                    print(f"  ❌ 空间不足")
                    break
                
                # 计算间距（列间距数量 = 列数 - 1）
                actual_spacing = available_for_spacing / (test_cols - 1)
                print(f"  实际间距: {actual_spacing}px")
                
                # 检查间距是否足够
                if actual_spacing < spacing_px:
                    print(f"  ❌ 间距太小 (需要至少 {spacing_px}px)")
                    break
                
                total_width_needed = test_cols * BADGE_DIAMETER_PX + (test_cols - 1) * actual_spacing
                print(f"  需要宽度: {total_width_needed}px")
            
            # 检查是否能放下
            if total_width_needed <= available_width:
                print(f"  ✅ 可以放下")
            else:
                print(f"  ❌ 放不下")
                break
        
        print(f"\n=== 运行实际算法 ===")
        
        layout_engine = LayoutEngine()
        compact_layout = layout_engine.calculate_compact_layout(spacing_mm, margin_mm)
        
        print(f"算法结果:")
        print(f"  总位置数: {len(compact_layout['positions'])}")
        print(f"  列数: {compact_layout['columns']}")
        print(f"  水平间距: {compact_layout['horizontal_spacing']:.1f}px")
        print(f"  垂直间距: {compact_layout['vertical_spacing']:.1f}px")
        
        # 分析实际位置
        positions = compact_layout['positions']
        if positions:
            print(f"\n实际位置:")
            for i, (x, y) in enumerate(positions):
                print(f"  位置{i+1}: ({x}, {y})")
        
        return True
        
    except Exception as e:
        print(f"调试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_detailed()
