"""
A4排版引擎模块
实现圆形图片在A4纸上的自动排版算法
"""

import math
from PIL import Image, ImageDraw, ImageTk
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import *

class LayoutEngine:
    """A4排版引擎类"""
    
    def __init__(self):
        self.a4_width_px = A4_WIDTH_PX
        self.a4_height_px = A4_HEIGHT_PX
        self.badge_diameter_px = BADGE_DIAMETER_PX
        self.badge_radius_px = self.badge_diameter_px // 2
        
    def calculate_grid_layout(self, spacing_mm=DEFAULT_SPACING, margin_mm=DEFAULT_MARGIN):
        """
        计算网格排列布局
        参数:
            spacing_mm: 圆形间距（毫米）
            margin_mm: 页边距（毫米）
        返回: dict - 布局信息
        """
        # 转换为像素
        spacing_px = mm_to_pixels(spacing_mm)
        margin_px = mm_to_pixels(margin_mm)
        
        # 计算可用区域
        available_width = self.a4_width_px - 2 * margin_px
        available_height = self.a4_height_px - 2 * margin_px
        
        # 计算每行和每列可放置的圆形数量
        circle_with_spacing = self.badge_diameter_px + spacing_px
        
        cols = max(1, available_width // circle_with_spacing)
        rows = max(1, available_height // circle_with_spacing)
        
        # 计算实际间距（均匀分布）
        if cols > 1:
            actual_spacing_x = (available_width - cols * self.badge_diameter_px) / (cols - 1)
        else:
            actual_spacing_x = 0
            
        if rows > 1:
            actual_spacing_y = (available_height - rows * self.badge_diameter_px) / (rows - 1)
        else:
            actual_spacing_y = 0
        
        # 计算起始位置（居中）
        total_width = cols * self.badge_diameter_px + (cols - 1) * actual_spacing_x
        total_height = rows * self.badge_diameter_px + (rows - 1) * actual_spacing_y
        
        start_x = margin_px + (available_width - total_width) / 2
        start_y = margin_px + (available_height - total_height) / 2
        
        # 生成位置列表
        positions = []
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * (self.badge_diameter_px + actual_spacing_x) + self.badge_radius_px
                y = start_y + row * (self.badge_diameter_px + actual_spacing_y) + self.badge_radius_px
                positions.append((int(x), int(y)))
        
        return {
            'type': 'grid',
            'positions': positions,
            'rows': rows,
            'cols': cols,
            'max_count': rows * cols,
            'spacing_x': actual_spacing_x,
            'spacing_y': actual_spacing_y,
            'margin': margin_px
        }
    
    def calculate_compact_layout(self, spacing_mm=DEFAULT_SPACING, margin_mm=DEFAULT_MARGIN):
        """
        计算紧密排列布局（六边形密排）
        参数:
            spacing_mm: 圆形间距（毫米）
            margin_mm: 页边距（毫米）
        返回: dict - 布局信息
        """
        # 转换为像素
        spacing_px = mm_to_pixels(spacing_mm)
        margin_px = mm_to_pixels(margin_mm)
        
        # 计算可用区域
        available_width = self.a4_width_px - 2 * margin_px
        available_height = self.a4_height_px - 2 * margin_px
        
        # 六边形密排的行间距
        row_height = self.badge_diameter_px + spacing_px
        row_offset_y = row_height * 0.866  # sin(60°) ≈ 0.866
        
        positions = []
        row = 0
        y = margin_px + self.badge_radius_px
        
        while y + self.badge_radius_px <= self.a4_height_px - margin_px:
            # 计算当前行的列数和起始位置
            if row % 2 == 0:  # 偶数行
                col_offset = 0
            else:  # 奇数行（偏移半个圆的距离）
                col_offset = (self.badge_diameter_px + spacing_px) / 2
            
            # 计算当前行可放置的圆形数量
            available_row_width = available_width - col_offset
            circle_with_spacing = self.badge_diameter_px + spacing_px
            cols_in_row = max(0, int(available_row_width // circle_with_spacing))
            
            if cols_in_row > 0:
                # 计算起始X位置（居中）
                total_row_width = cols_in_row * circle_with_spacing - spacing_px
                start_x = margin_px + col_offset + (available_row_width - total_row_width) / 2
                
                # 添加当前行的所有位置
                for col in range(cols_in_row):
                    x = start_x + col * circle_with_spacing + self.badge_radius_px
                    if x + self.badge_radius_px <= self.a4_width_px - margin_px:
                        positions.append((int(x), int(y)))
            
            # 移动到下一行
            row += 1
            y += row_offset_y
        
        return {
            'type': 'compact',
            'positions': positions,
            'max_count': len(positions),
            'row_offset_y': row_offset_y,
            'spacing': spacing_px,
            'margin': margin_px
        }
    
    def create_layout_preview(self, image_items, layout_type='grid', spacing_mm=DEFAULT_SPACING,
                            margin_mm=DEFAULT_MARGIN, preview_scale=0.5):
        """
        创建排版预览图片
        参数:
            image_items: 图片项目列表
            layout_type: 布局类型 ('grid' 或 'compact')
            spacing_mm: 间距（毫米）
            margin_mm: 页边距（毫米）
            preview_scale: 预览缩放比例
        返回: PIL.ImageTk.PhotoImage - 预览图片
        """
        try:
            # 计算布局
            if layout_type == 'grid':
                layout = self.calculate_grid_layout(spacing_mm, margin_mm)
            else:
                layout = self.calculate_compact_layout(spacing_mm, margin_mm)
            
            # 创建A4画布
            canvas = Image.new('RGB', (self.a4_width_px, self.a4_height_px), (255, 255, 255))
            
            # 绘制页边距线（用于预览）
            draw = ImageDraw.Draw(canvas)
            margin_px = mm_to_pixels(margin_mm)
            draw.rectangle([
                margin_px, margin_px, 
                self.a4_width_px - margin_px, self.a4_height_px - margin_px
            ], outline=(200, 200, 200), width=2)
            
            # 放置圆形图片
            positions = layout['positions']
            for i, image_item in enumerate(image_items):
                if i >= len(positions):
                    break  # 超出可放置数量
                
                try:
                    # 获取圆形图片
                    from core.image_processor import ImageProcessor
                    processor = ImageProcessor()
                    
                    circle_img = processor.create_circular_crop(
                        image_item.file_path,
                        image_item.scale,
                        image_item.offset_x,
                        image_item.offset_y,
                        image_item.rotation
                    )
                    
                    # 计算粘贴位置（圆心位置转换为左上角位置）
                    center_x, center_y = positions[i]
                    paste_x = center_x - self.badge_radius_px
                    paste_y = center_y - self.badge_radius_px
                    
                    # 粘贴到画布
                    canvas.paste(circle_img, (paste_x, paste_y))
                    
                except Exception as e:
                    print(f"放置图片失败 {image_item.filename}: {e}")
                    # 绘制占位圆形
                    center_x, center_y = positions[i]
                    draw.ellipse([
                        center_x - self.badge_radius_px, center_y - self.badge_radius_px,
                        center_x + self.badge_radius_px, center_y + self.badge_radius_px
                    ], outline=(200, 200, 200), width=2)
            
            # 绘制剩余位置的占位符
            for i in range(len(image_items), len(positions)):
                center_x, center_y = positions[i]
                draw.ellipse([
                    center_x - self.badge_radius_px, center_y - self.badge_radius_px,
                    center_x + self.badge_radius_px, center_y + self.badge_radius_px
                ], outline=(220, 220, 220), width=1)
            
            # 缩放到预览大小
            preview_width = int(self.a4_width_px * preview_scale)
            preview_height = int(self.a4_height_px * preview_scale)
            preview_img = canvas.resize((preview_width, preview_height), Image.Resampling.LANCZOS)
            
            return ImageTk.PhotoImage(preview_img)
            
        except Exception as e:
            print(f"创建排版预览失败: {e}")
            # 返回空白预览
            blank_img = Image.new('RGB', (400, 566), (240, 240, 240))
            return ImageTk.PhotoImage(blank_img)
    
    def get_layout_info(self, layout_type='grid', spacing_mm=DEFAULT_SPACING, margin_mm=DEFAULT_MARGIN):
        """
        获取布局信息
        参数:
            layout_type: 布局类型
            spacing_mm: 间距
            margin_mm: 页边距
        返回: dict - 布局信息
        """
        if layout_type == 'grid':
            layout = self.calculate_grid_layout(spacing_mm, margin_mm)
        else:
            layout = self.calculate_compact_layout(spacing_mm, margin_mm)
        
        return {
            'type': layout_type,
            'max_count': layout['max_count'],
            'positions_count': len(layout['positions']),
            'spacing_mm': spacing_mm,
            'margin_mm': margin_mm
        }
