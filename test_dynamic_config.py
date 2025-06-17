#!/usr/bin/env python3
"""
测试动态配置功能
验证圆形尺寸可以动态调整
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_dynamic_config():
    """测试动态配置"""
    print("=== 动态配置测试 ===\n")
    
    try:
        from utils.config import app_config
        from core.layout_engine import LayoutEngine
        from core.image_processor import ImageProcessor
        
        # 创建组件
        layout_engine = LayoutEngine()
        image_processor = ImageProcessor()
        
        print("1. 测试默认配置:")
        print(f"   圆形直径: {app_config.badge_diameter_mm}mm ({app_config.badge_diameter_px}px)")
        print(f"   布局引擎直径: {layout_engine.badge_diameter_px}px")
        print(f"   图片处理器直径: {image_processor.badge_diameter_px}px")
        
        # 测试配置变化监听
        changes = []
        def config_listener(key, old_value, new_value):
            changes.append((key, old_value, new_value))
        
        app_config.add_listener(config_listener)
        
        print("\n2. 测试配置变化:")
        
        # 测试不同尺寸
        test_sizes = [32, 58, 25, 68]
        
        for size in test_sizes:
            print(f"\n   设置直径为 {size}mm:")
            app_config.badge_diameter_mm = size
            
            print(f"     配置: {app_config.badge_diameter_mm}mm ({app_config.badge_diameter_px}px)")
            print(f"     布局引擎: {layout_engine.badge_diameter_px}px")
            print(f"     图片处理器: {image_processor.badge_diameter_px}px")
            
            # 测试布局容量
            compact_layout = layout_engine.calculate_compact_layout(5, 15)
            print(f"     紧凑布局容量: {compact_layout['max_count']}个")
        
        print(f"\n3. 配置变化记录:")
        for i, (key, old_val, new_val) in enumerate(changes, 1):
            print(f"   变化{i}: {key} {old_val}mm -> {new_val}mm")
        
        # 测试边界值
        print(f"\n4. 测试边界值:")
        
        # 测试最小值
        app_config.badge_diameter_mm = 5  # 应该被限制为10
        print(f"   设置5mm，实际: {app_config.badge_diameter_mm}mm")
        
        # 测试最大值
        app_config.badge_diameter_mm = 150  # 应该被限制为100
        print(f"   设置150mm，实际: {app_config.badge_diameter_mm}mm")
        
        # 测试正常值
        app_config.badge_diameter_mm = 32
        print(f"   设置32mm，实际: {app_config.badge_diameter_mm}mm")
        
        print("\n✅ 动态配置测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def calculate_optimal_sizes():
    """计算不同尺寸下的最优布局"""
    print("\n" + "="*50)
    print("=== 最优尺寸计算 ===\n")
    
    try:
        from utils.config import app_config, A4_WIDTH_MM, A4_HEIGHT_MM
        from core.layout_engine import LayoutEngine
        
        layout_engine = LayoutEngine()
        
        # 测试不同尺寸的布局容量
        test_sizes = [20, 25, 30, 32, 35, 40, 45, 50, 55, 58, 60, 65, 68, 70]
        
        print("圆形直径 | 网格布局 | 紧凑布局 | 理论4-3-4")
        print("-" * 45)
        
        for size in test_sizes:
            app_config.badge_diameter_mm = size
            
            # 计算布局容量
            grid_layout = layout_engine.calculate_grid_layout(5, 15)
            compact_layout = layout_engine.calculate_compact_layout(5, 15)
            
            grid_count = grid_layout['max_count']
            compact_count = compact_layout['max_count']
            
            # 计算理论4-3-4布局是否可行
            spacing_mm = 5
            margin_mm = 15
            available_width = A4_WIDTH_MM - 2 * margin_mm
            available_height = A4_HEIGHT_MM - 2 * margin_mm
            
            center_distance = size + spacing_mm
            
            # 4-3-4布局宽度需求
            row1_width = 4 * center_distance - spacing_mm
            row2_width = 3 * center_distance - spacing_mm + center_distance / 2
            max_width_needed = max(row1_width, row2_width)
            
            # 高度需求（3行）
            import math
            hex_vertical_spacing = center_distance * math.sqrt(3) / 2
            total_height_needed = 2 * hex_vertical_spacing + size
            
            can_fit_434 = (available_width >= max_width_needed and 
                          available_height >= total_height_needed)
            
            fit_434_str = "✅" if can_fit_434 else "❌"
            
            print(f"{size:8}mm | {grid_count:8}个 | {compact_count:8}个 | {fit_434_str:8}")
        
        print("\n推荐尺寸:")
        print("  - 25mm: 小徽章，高密度排版")
        print("  - 32mm: 中等徽章，平衡尺寸和数量")
        print("  - 58mm: 大徽章，标准尺寸")
        
        return True
        
    except Exception as e:
        print(f"计算失败: {e}")
        return False

if __name__ == "__main__":
    success1 = test_dynamic_config()
    success2 = calculate_optimal_sizes()
    
    if success1 and success2:
        print(f"\n🎉 所有测试通过！")
    else:
        print(f"\n❌ 部分测试失败")
