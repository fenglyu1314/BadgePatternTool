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

        # 布局缓存
        self._layout_cache = {}
        self._max_layout_cache = 20

    def _manage_layout_cache(self):
        """管理布局缓存大小"""
        if len(self._layout_cache) >= self._max_layout_cache:
            # 删除最旧的缓存项
            oldest_key = next(iter(self._layout_cache))
            del self._layout_cache[oldest_key]

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
        计算网格排列布局（带缓存优化）
        参数:
            spacing_mm: 圆形间距（毫米）
            margin_mm: 页边距（毫米）
        返回: dict - 布局信息
        """
        # 检查缓存
        cache_key = f"grid_{spacing_mm}_{margin_mm}_{app_config.badge_diameter_mm}"
        if cache_key in self._layout_cache:
            return self._layout_cache[cache_key].copy()

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
        
        result = {
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

        # 缓存结果
        self._manage_layout_cache()
        self._layout_cache[cache_key] = result.copy()

        return result
    
    def calculate_compact_layout(self, spacing_mm=DEFAULT_SPACING, margin_mm=DEFAULT_MARGIN):
        """
        计算紧密排列布局（六边形蜂巢密排）
        优化算法：实现4-3-4模式的紧凑排列，最大化利用A4空间
        参数:
            spacing_mm: 圆形间距（毫米）
            margin_mm: 页边距（毫米）
        返回: dict - 布局信息
        """
        # 检查缓存
        cache_key = f"compact_{spacing_mm}_{margin_mm}_{app_config.badge_diameter_mm}"
        if cache_key in self._layout_cache:
            return self._layout_cache[cache_key].copy()

        # 转换为像素
        spacing_px = mm_to_pixels(spacing_mm)
        margin_px = mm_to_pixels(margin_mm)

        # 计算可用区域
        available_width = self.a4_width_px - 2 * margin_px
        available_height = self.a4_height_px - 2 * margin_px

        # 圆心之间的最小距离
        min_center_distance = self.badge_diameter_px + spacing_px

        # 计算最优列数和间距
        max_cols, horizontal_spacing, start_x = self._calculate_compact_columns(
            available_width, margin_px, spacing_px, min_center_distance
        )

        # 计算垂直间距和偏移
        vertical_spacing, middle_col_offset = self._calculate_compact_vertical_spacing(
            horizontal_spacing, min_center_distance
        )

        # 生成所有位置
        layout_params = {
            'max_cols': max_cols,
            'start_x': start_x,
            'horizontal_spacing': horizontal_spacing,
            'margin_px': margin_px,
            'vertical_spacing': vertical_spacing,
            'middle_col_offset': middle_col_offset
        }
        positions = self._generate_compact_positions(layout_params)

        result = {
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

        # 缓存结果
        self._manage_layout_cache()
        self._layout_cache[cache_key] = result.copy()

        return result

    def _calculate_compact_columns(self, available_width, margin_px, spacing_px, min_center_distance):
        """计算紧凑布局的列数和水平间距"""
        # 第一步：计算可以放置的列数（保守估计）
        max_cols = self._find_max_columns(available_width, spacing_px)

        # 第二步：尝试使用六边形网格间距
        hex_horizontal_factor = math.sqrt(3) / 2  # ≈ 0.866
        theoretical_hex_spacing = self.badge_diameter_px * hex_horizontal_factor + spacing_px

        # 基于六边形间距重新计算列数
        max_cols_hex = int((available_width + theoretical_hex_spacing) // theoretical_hex_spacing)
        max_cols_hex = max(1, max_cols_hex)

        # 选择最优方案
        if max_cols_hex > max_cols:
            # 六边形间距可以放下更多列
            max_cols = max_cols_hex
            horizontal_spacing = theoretical_hex_spacing
            start_x = margin_px + self.badge_radius_px
        else:
            # 使用均匀分布方式
            horizontal_spacing, start_x = self._calculate_uniform_spacing(
                max_cols, available_width, margin_px, min_center_distance
            )

        return max_cols, horizontal_spacing, start_x

    def _find_max_columns(self, available_width, spacing_px):
        """查找可以放置的最大列数"""
        max_cols = 1

        for test_cols in range(1, 5):  # 最多测试4列
            if test_cols == 1:
                total_width_needed = self.badge_diameter_px
            else:
                # 计算实际可用的水平空间
                available_for_spacing = available_width - test_cols * self.badge_diameter_px
                if available_for_spacing < 0:
                    break

                # 计算间距
                actual_spacing = available_for_spacing / (test_cols - 1)
                min_required_spacing = max(0, spacing_px * 0.5)  # 允许间距减半
                if actual_spacing < min_required_spacing:
                    break

                total_width_needed = test_cols * self.badge_diameter_px + (test_cols - 1) * actual_spacing

            if total_width_needed <= available_width:
                max_cols = test_cols
            else:
                break

        return max_cols

    def _calculate_uniform_spacing(self, max_cols, available_width, margin_px, min_center_distance):
        """计算均匀分布的间距和起始位置"""
        if max_cols == 1:
            horizontal_spacing = min_center_distance
            start_x = margin_px + available_width / 2  # 居中
        else:
            # 计算实际间距
            available_for_spacing = available_width - max_cols * self.badge_diameter_px
            actual_spacing = available_for_spacing / (max_cols - 1)
            horizontal_spacing = self.badge_diameter_px + actual_spacing
            start_x = margin_px + self.badge_radius_px

        return horizontal_spacing, start_x

    def _calculate_compact_vertical_spacing(self, horizontal_spacing, min_center_distance):
        """计算紧凑布局的垂直间距"""
        # 六边形网格的垂直间距 = 水平间距 * √3/2
        theoretical_vertical = horizontal_spacing * math.sqrt(3) / 2
        # 使用理论值和最小距离的较大者，确保不重叠
        vertical_spacing = max(theoretical_vertical, min_center_distance)
        # 中间列的垂直偏移
        middle_col_offset = vertical_spacing / 2

        return vertical_spacing, middle_col_offset

    def _generate_compact_positions(self, layout_params):
        """生成紧凑布局的所有位置"""
        positions = []

        for col in range(layout_params['max_cols']):
            # 计算列的X位置
            if layout_params['max_cols'] == 1:
                x = layout_params['start_x']
            else:
                x = layout_params['start_x'] + col * layout_params['horizontal_spacing']

            # 边界检查
            if (x - self.badge_radius_px < layout_params['margin_px'] or
                x + self.badge_radius_px > self.a4_width_px - layout_params['margin_px']):
                continue

            # 计算当前列的Y起始位置
            if col % 2 == 0:  # 偶数列
                y_start = layout_params['margin_px'] + self.badge_radius_px
            else:  # 奇数列 - 向下偏移
                y_start = layout_params['margin_px'] + self.badge_radius_px + layout_params['middle_col_offset']

            # 在当前列中放置圆形
            y = y_start
            while y + self.badge_radius_px <= self.a4_height_px - layout_params['margin_px']:
                positions.append((int(x), int(y)))
                y += layout_params['vertical_spacing']

        return positions
    
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
            layout = self._get_layout(layout_type, spacing_mm, margin_mm)

            # 创建画布和绘制对象
            canvas, draw = self._create_preview_canvas(margin_mm)

            # 放置图片
            self._place_images_on_canvas(canvas, draw, image_items, layout['positions'])

            # 绘制占位符
            self._draw_placeholders(draw, image_items, layout['positions'])

            # 转换为QPixmap
            return self._canvas_to_pixmap(canvas, preview_scale)

        except Exception as e:
            print(f"创建排版预览失败: {e}")
            return self._create_blank_preview()

    def _get_layout(self, layout_type, spacing_mm, margin_mm):
        """获取布局信息"""
        if layout_type == 'grid':
            return self.calculate_grid_layout(spacing_mm, margin_mm)
        else:
            return self.calculate_compact_layout(spacing_mm, margin_mm)

    def _create_preview_canvas(self, margin_mm):
        """创建预览画布"""
        # 创建A4画布
        canvas = Image.new('RGB', (self.a4_width_px, self.a4_height_px), (255, 255, 255))

        # 绘制页边距线
        draw = ImageDraw.Draw(canvas)
        margin_px = mm_to_pixels(margin_mm)
        draw.rectangle([
            margin_px, margin_px,
            self.a4_width_px - margin_px, self.a4_height_px - margin_px
        ], outline=(200, 200, 200), width=2)

        return canvas, draw

    def _place_images_on_canvas(self, canvas, draw, image_items, positions):
        """在画布上放置图片"""
        from core.image_processor import ImageProcessor
        processor = ImageProcessor()
        image_cache = {}

        for i, image_item in enumerate(image_items):
            if i >= len(positions):
                break

            try:
                # 获取或创建圆形图片
                circle_img = self._get_cached_circle_image(
                    processor, image_cache, image_item
                )

                # 计算粘贴位置
                center_x, center_y = positions[i]
                paste_x = center_x - self.badge_radius_px
                paste_y = center_y - self.badge_radius_px

                # 粘贴到画布
                if circle_img.mode == 'RGBA':
                    canvas.paste(circle_img, (paste_x, paste_y), circle_img)
                else:
                    canvas.paste(circle_img, (paste_x, paste_y))

            except Exception as e:
                print(f"放置图片失败 {image_item.filename}: {e}")
                self._draw_error_placeholder(draw, positions[i])

    def _get_cached_circle_image(self, processor, image_cache, image_item):
        """获取缓存的圆形图片"""
        cache_key = f"{image_item.file_path}:{image_item.scale}:{image_item.offset_x}:{image_item.offset_y}:{image_item.rotation}"

        if cache_key in image_cache:
            return image_cache[cache_key]

        circle_img = processor.create_circular_crop(
            image_item.file_path,
            image_item.scale,
            image_item.offset_x,
            image_item.offset_y,
            image_item.rotation
        )
        image_cache[cache_key] = circle_img
        return circle_img

    def _draw_error_placeholder(self, draw, position):
        """绘制错误占位符"""
        center_x, center_y = position
        draw.ellipse([
            center_x - self.badge_radius_px, center_y - self.badge_radius_px,
            center_x + self.badge_radius_px, center_y + self.badge_radius_px
        ], fill=(200, 200, 200), outline=(180, 180, 180), width=1)

    def _draw_placeholders(self, draw, image_items, positions):
        """绘制剩余位置的占位符"""
        for i in range(len(image_items), len(positions)):
            center_x, center_y = positions[i]
            draw.ellipse([
                center_x - self.badge_radius_px, center_y - self.badge_radius_px,
                center_x + self.badge_radius_px, center_y + self.badge_radius_px
            ], fill=(220, 220, 220), outline=(200, 200, 200), width=1)

    def _canvas_to_pixmap(self, canvas, preview_scale):
        """将画布转换为QPixmap"""
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

    def _create_blank_preview(self):
        """创建空白预览"""
        blank_pixmap = QPixmap(400, 566)
        blank_pixmap.fill()
        return blank_pixmap
    
    def calculate_multi_page_layout(self, image_count, layout_type='grid',
                                   spacing_mm=DEFAULT_SPACING, margin_mm=DEFAULT_MARGIN):
        """
        计算多页面布局
        参数:
            image_count: 需要排版的图片总数
            layout_type: 布局类型 ('grid' 或 'compact')
            spacing_mm: 间距（毫米）
            margin_mm: 页边距（毫米）
        返回: dict - 多页面布局信息
        """
        # 获取单页布局信息
        if layout_type == 'grid':
            single_page_layout = self.calculate_grid_layout(spacing_mm, margin_mm)
        else:
            single_page_layout = self.calculate_compact_layout(spacing_mm, margin_mm)

        max_per_page = single_page_layout['max_count']

        # 计算需要的页面数
        total_pages = max(1, (image_count + max_per_page - 1) // max_per_page)

        # 为每个页面生成布局信息
        pages = []
        remaining_images = image_count

        for page_index in range(total_pages):
            # 计算当前页面的图片数量
            images_on_page = min(remaining_images, max_per_page)

            # 复制单页布局信息
            page_layout = single_page_layout.copy()
            page_layout['page_index'] = page_index
            page_layout['images_on_page'] = images_on_page
            page_layout['total_pages'] = total_pages

            pages.append(page_layout)
            remaining_images -= images_on_page

        return {
            'type': layout_type,
            'total_pages': total_pages,
            'max_per_page': max_per_page,
            'total_images': image_count,
            'pages': pages,
            'spacing_mm': spacing_mm,
            'margin_mm': margin_mm
        }

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

    def create_multi_page_preview(self, image_items, layout_type='grid',
                                 spacing_mm=DEFAULT_SPACING, margin_mm=DEFAULT_MARGIN,
                                 preview_scale=0.5):
        """
        创建多页面排版预览图片列表
        参数:
            image_items: 图片项目列表
            layout_type: 布局类型 ('grid' 或 'compact')
            spacing_mm: 间距（毫米）
            margin_mm: 页边距（毫米）
            preview_scale: 预览缩放比例
        返回: list[QPixmap] - 每页的预览图片列表
        """
        if not PYSIDE6_AVAILABLE:
            print("PySide6不可用，无法创建多页面排版预览")
            return []

        try:
            # 计算多页面布局
            multi_layout = self.calculate_multi_page_layout(
                len(image_items), layout_type, spacing_mm, margin_mm
            )

            page_previews = []
            image_index = 0

            # 为每个页面生成预览
            for page_info in multi_layout['pages']:
                # 获取当前页面的图片
                page_images = image_items[image_index:image_index + page_info['images_on_page']]

                # 创建单页预览
                page_preview = self.create_layout_preview(
                    page_images, layout_type, spacing_mm, margin_mm, preview_scale
                )

                page_previews.append(page_preview)
                image_index += page_info['images_on_page']

            return page_previews

        except Exception as e:
            print(f"创建多页面排版预览失败: {e}")
            return [self._create_blank_preview()]
