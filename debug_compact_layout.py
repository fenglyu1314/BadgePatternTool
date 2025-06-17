#!/usr/bin/env python3
"""
调试紧凑布局的列计算问题
"""

def debug_compact_layout():
    """调试紧凑布局"""
    try:
        from src.core.layout_engine import LayoutEngine
        from src.utils.config import app_config, mm_to_pixels
        
        # 使用68mm配置
        app_config.badge_diameter_mm = 68
        layout_engine = LayoutEngine()
        
        spacing_mm = 5
        margin_mm = 10
        
        # 手动计算参数
        spacing_px = mm_to_pixels(spacing_mm)
        margin_px = mm_to_pixels(margin_mm)
        available_width = layout_engine.a4_width_px - 2 * margin_px
        available_height = layout_engine.a4_height_px - 2 * margin_px
        
        center_distance = layout_engine.badge_diameter_px + spacing_px
        horizontal_spacing = center_distance
        
        print(f"调试信息:")
        print(f"  圆形直径: {layout_engine.badge_diameter_px}px")
        print(f"  圆形半径: {layout_engine.badge_radius_px}px")
        print(f"  间距: {spacing_px}px")
        print(f"  页边距: {margin_px}px")
        print(f"  可用宽度: {available_width}px")
        print(f"  可用高度: {available_height}px")
        print(f"  圆心距离: {center_distance}px")
        print(f"  水平间距: {horizontal_spacing}px")
        
        # 计算列数
        max_cols = int(available_width // horizontal_spacing)
        print(f"  理论列数: {max_cols}")
        
        # 计算起始位置
        total_width_used = (max_cols - 1) * horizontal_spacing
        start_x = margin_px + (available_width - total_width_used) / 2 + layout_engine.badge_radius_px
        print(f"  起始X位置: {start_x}")
        
        # 检查每一列的边界
        print(f"\n列边界检查:")
        valid_cols = 0
        for col in range(max_cols):
            x = start_x + col * horizontal_spacing
            left_edge = x - layout_engine.badge_radius_px
            right_edge = x + layout_engine.badge_radius_px
            
            is_valid = (left_edge >= margin_px and right_edge <= layout_engine.a4_width_px - margin_px)
            
            print(f"  第{col+1}列: X={x:.1f}, 左边缘={left_edge:.1f}, 右边缘={right_edge:.1f}, 有效={is_valid}")
            
            if is_valid:
                valid_cols += 1
        
        print(f"  有效列数: {valid_cols}")
        
        # 运行实际的布局计算
        compact_layout = layout_engine.calculate_compact_layout(spacing_mm, margin_mm)
        print(f"\n实际布局结果:")
        print(f"  计算出的列数: {compact_layout['columns']}")
        print(f"  总位置数: {len(compact_layout['positions'])}")
        
        return True
        
    except Exception as e:
        print(f"调试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_compact_layout()
