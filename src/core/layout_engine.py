"""
A4排版引擎模块
实现圆形图片在A4纸上的自动排版算法
"""

import math
import sys
import os
from io import BytesIO

from PIL import Image, ImageDraw

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import (
    A4_WIDTH_PX, A4_HEIGHT_PX, DEFAULT_SPACING, DEFAULT_MARGIN,
    mm_to_pixels, app_config
)

# PySide6导入（用于预览功能）
try:
    from PySide6.QtGui import QPixmap
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

class LayoutEngine:
    """A4排版引擎类"""
    
    def __init__(self):
        self.a4_width_px = A4_WIDTH_PX
        self.a4_height_px = A4_HEIGHT_PX

    @property
    def badge_diameter_px(self):
        """获取当前圆形直径（像素）"""
        return app_config.badge_diameter_px

    @property
    def badge_radius_px(self):
        """获取当前圆形半径（像素）"""
        return app_config.badge_radius_px
        
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
        
        # 使用固定间距计算，与密集排版保持一致
        # 圆心之间的距离（圆形直径 + 用户设定的间距）
        center_distance = self.badge_diameter_px + spacing_px

        # 计算每行和每列可放置的圆形数量
        cols = max(1, available_width // center_distance)
        rows = max(1, available_height // center_distance)

        # 计算起始位置（居中）
        total_width = cols * center_distance
        total_height = rows * center_distance

        start_x = margin_px + (available_width - total_width) / 2
        start_y = margin_px + (available_height - total_height) / 2

        # 生成位置列表
        positions = []
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * center_distance + self.badge_radius_px
                y = start_y + row * center_distance + self.badge_radius_px
                positions.append((int(x), int(y)))
        
        return {
            'type': 'grid',
            'positions': positions,
            'rows': rows,
            'cols': cols,
            'max_count': rows * cols,
            'spacing_x': spacing_px,
            'spacing_y': spacing_px,
            'center_distance': center_distance,
            'margin': margin_px
        }
    
    def calculate_compact_layout(self, spacing_mm=DEFAULT_SPACING, margin_mm=DEFAULT_MARGIN):
        """
        计算紧密排列布局（六边形蜂巢密排）
        优化算法：实现4-3-4模式的紧凑排列，最大化利用A4空间
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

        positions = []

        # 优化的紧凑排列算法
        # 目标：实现4-3-4模式，最大化利用空间

        # 圆心之间的最小距离（圆形直径 + 用户设定的间距）
        min_center_distance = self.badge_diameter_px + spacing_px

        # 第一步：计算可以放置的列数
        # 使用更保守的计算方式，确保所有列都能放下
        max_cols = 1

        # 逐步增加列数，直到无法放下为止
        for test_cols in range(1, 5):  # 最多测试4列
            # 计算这个列数需要的总宽度
            if test_cols == 1:
                total_width_needed = self.badge_diameter_px
            else:
                # 计算实际可用的水平空间（减去圆形直径）
                available_for_spacing = available_width - test_cols * self.badge_diameter_px
                if available_for_spacing < 0:
                    break  # 空间不足

                # 计算间距（列间距数量 = 列数 - 1）
                actual_spacing = available_for_spacing / (test_cols - 1)

                # 放宽间距要求：允许更小的间距，但不能为负数
                min_required_spacing = max(0, spacing_px * 0.5)  # 允许间距减半
                if actual_spacing < min_required_spacing:
                    break  # 间距太小

                total_width_needed = test_cols * self.badge_diameter_px + (test_cols - 1) * actual_spacing

            # 检查是否能放下
            if total_width_needed <= available_width:
                max_cols = test_cols
            else:
                break

        # 第二步：使用六边形网格的理论间距
        # 六边形网格的水平间距 = 圆形直径 * √3/2 + 用户间距
        hex_horizontal_factor = math.sqrt(3) / 2  # ≈ 0.866
        theoretical_hex_spacing = self.badge_diameter_px * hex_horizontal_factor + spacing_px

        # 重新计算可以放置的列数（基于六边形间距）
        max_cols_hex = int((available_width + theoretical_hex_spacing) // theoretical_hex_spacing)
        max_cols_hex = max(1, max_cols_hex)

        # 检查六边形间距是否可行
        if max_cols_hex > max_cols:
            # 六边形间距可以放下更多列，使用六边形间距
            max_cols = max_cols_hex
            horizontal_spacing = theoretical_hex_spacing

            # 计算起始位置（从左边距开始）
            start_x = margin_px + self.badge_radius_px
        else:
            # 使用原来的均匀分布方式
            if max_cols == 1:
                horizontal_spacing = min_center_distance
                start_x = margin_px + available_width / 2  # 居中
            else:
                # 计算实际可用的水平空间（减去圆形直径）
                available_for_spacing = available_width - max_cols * self.badge_diameter_px
                # 计算间距（列间距数量 = 列数 - 1）
                actual_spacing = available_for_spacing / (max_cols - 1)
                # 水平间距 = 圆形直径 + 实际间距（这是圆心之间的距离）
                horizontal_spacing = self.badge_diameter_px + actual_spacing
                # 起始X位置（第一个圆的圆心）
                start_x = margin_px + self.badge_radius_px

        # 第三步：计算垂直间距
        # 六边形网格的垂直间距 = 水平间距 * √3/2
        theoretical_vertical = horizontal_spacing * math.sqrt(3) / 2
        # 使用理论值和最小距离的较大者，确保不重叠
        vertical_spacing = max(theoretical_vertical, min_center_distance)

        # 中间列的垂直偏移
        middle_col_offset = vertical_spacing / 2

        # 第四步：为每一列计算位置
        for col in range(max_cols):
            if max_cols == 1:
                x = start_x
            else:
                x = start_x + col * horizontal_spacing

            # 边界检查
            if (x - self.badge_radius_px < margin_px or
                x + self.badge_radius_px > self.a4_width_px - margin_px):
                continue

            # 计算当前列的Y起始位置
            if col % 2 == 0:  # 偶数列（第0、2、4...列）
                y_start = margin_px + self.badge_radius_px
            else:  # 奇数列（第1、3、5...列）- 向下偏移
                y_start = margin_px + self.badge_radius_px + middle_col_offset

            # 在当前列中放置圆形
            y = y_start
            while y + self.badge_radius_px <= self.a4_height_px - margin_px:
                positions.append((int(x), int(y)))
                y += vertical_spacing

        return {
            'type': 'compact',
            'positions': positions,
            'max_count': len(positions),
            'vertical_spacing': vertical_spacing,
            'horizontal_spacing': horizontal_spacing,
            'middle_col_offset': middle_col_offset,
            'center_distance': min_center_distance,
            'spacing': spacing_px,
            'margin': margin_px,
            'columns': max_cols
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
        返回: QPixmap - 预览图片
        """
        if not PYSIDE6_AVAILABLE:
            print("PySide6不可用，无法创建排版预览")
            return None

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

            # 创建图片处理器（复用实例）
            from core.image_processor import ImageProcessor
            processor = ImageProcessor()

            # 图片缓存字典，避免重复处理相同参数的图片
            image_cache = {}

            for i, image_item in enumerate(image_items):
                if i >= len(positions):
                    break  # 超出可放置数量

                try:
                    # 创建缓存键
                    cache_key = f"{image_item.file_path}:{image_item.scale}:{image_item.offset_x}:{image_item.offset_y}:{image_item.rotation}"

                    # 检查缓存
                    if cache_key in image_cache:
                        circle_img = image_cache[cache_key]
                    else:
                        # 获取圆形图片
                        circle_img = processor.create_circular_crop(
                            image_item.file_path,
                            image_item.scale,
                            image_item.offset_x,
                            image_item.offset_y,
                            image_item.rotation
                        )
                        # 缓存结果
                        image_cache[cache_key] = circle_img

                    # 计算粘贴位置（圆心位置转换为左上角位置）
                    center_x, center_y = positions[i]
                    paste_x = center_x - self.badge_radius_px
                    paste_y = center_y - self.badge_radius_px

                    # 粘贴到画布（使用透明度遮罩）
                    if circle_img.mode == 'RGBA':
                        canvas.paste(circle_img, (paste_x, paste_y), circle_img)
                    else:
                        canvas.paste(circle_img, (paste_x, paste_y))

                except Exception as e:
                    print(f"放置图片失败 {image_item.filename}: {e}")
                    # 绘制占位圆形（实心）
                    center_x, center_y = positions[i]
                    draw.ellipse([
                        center_x - self.badge_radius_px, center_y - self.badge_radius_px,
                        center_x + self.badge_radius_px, center_y + self.badge_radius_px
                    ], fill=(200, 200, 200), outline=(180, 180, 180), width=1)

            # 绘制剩余位置的占位符（实心）
            for i in range(len(image_items), len(positions)):
                center_x, center_y = positions[i]
                draw.ellipse([
                    center_x - self.badge_radius_px, center_y - self.badge_radius_px,
                    center_x + self.badge_radius_px, center_y + self.badge_radius_px
                ], fill=(220, 220, 220), outline=(200, 200, 200), width=1)

            # 缩放到预览大小
            preview_width = int(self.a4_width_px * preview_scale)
            preview_height = int(self.a4_height_px * preview_scale)
            preview_img = canvas.resize((preview_width, preview_height), Image.Resampling.LANCZOS)

            # 转换为QPixmap
            buffer = BytesIO()
            preview_img.save(buffer, format='PNG')
            buffer.seek(0)

            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            return pixmap

        except Exception as e:
            print(f"创建排版预览失败: {e}")
            # 返回空白预览
            blank_pixmap = QPixmap(400, 566)
            blank_pixmap.fill()  # 填充为白色
            return blank_pixmap
    
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
