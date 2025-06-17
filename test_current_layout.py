#!/usr/bin/env python3
"""
测试当前68mm配置下的紧凑布局
"""

def test_current_layout():
    """测试当前配置下的布局"""
    try:
        from src.core.layout_engine import LayoutEngine
        from src.utils.config import app_config
        
        # 确保使用68mm配置
        app_config.badge_diameter_mm = 68
        layout_engine = LayoutEngine()
        
        print(f"当前配置: {app_config.badge_diameter_mm}mm ({app_config.badge_diameter_px}px)")
        
        # 测试紧凑布局
        compact_layout = layout_engine.calculate_compact_layout(5, 10)
        positions = compact_layout['positions']
        
        print(f"紧凑布局结果:")
        print(f"  总位置数: {len(positions)}")
        print(f"  最大容量: {compact_layout['max_count']}")
        print(f"  水平间距: {compact_layout['horizontal_spacing']:.1f}px")
        print(f"  垂直间距: {compact_layout['vertical_spacing']:.1f}px")
        
        # 分析列结构
        columns = {}
        for i, (x, y) in enumerate(positions):
            col_index = None
            for existing_x in columns.keys():
                if abs(x - existing_x) < 10:
                    col_index = existing_x
                    break
            if col_index is None:
                col_index = x
                columns[col_index] = []
            columns[col_index].append((y, i))
        
        sorted_columns = sorted(columns.items())
        print(f"列结构:")
        for col_idx, (x, positions_in_col) in enumerate(sorted_columns):
            print(f"  第{col_idx+1}列: {len(positions_in_col)}个圆形")
        
        # 检查是否只有4个位置（垂直排列）
        if len(positions) == 4:
            print("\n⚠️ 检测到只有4个位置，可能是垂直排列问题")
            print("前4个位置:")
            for i, (x, y) in enumerate(positions[:4]):
                print(f"  位置{i+1}: ({x}, {y})")
        
        return len(positions)
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    test_current_layout()
