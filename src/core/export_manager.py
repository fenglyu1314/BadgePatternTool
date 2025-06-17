"""
导出管理模块
实现PDF、PNG、JPG等格式的高质量导出功能
"""

import os
import sys
from datetime import datetime

from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import DEFAULT_SPACING, DEFAULT_MARGIN, PRINT_DPI
from core.layout_engine import LayoutEngine
from core.image_processor import ImageProcessor

class ExportManager:
    """导出管理器类"""
    
    def __init__(self):
        self.layout_engine = LayoutEngine()
        self.image_processor = ImageProcessor()
        
    def export_to_pdf(self, image_items, output_path, layout_type='grid', 
                     spacing_mm=DEFAULT_SPACING, margin_mm=DEFAULT_MARGIN):
        """
        导出为PDF文件
        参数:
            image_items: 图片项目列表
            output_path: 输出文件路径
            layout_type: 布局类型
            spacing_mm: 间距
            margin_mm: 页边距
        返回: bool - 是否成功
        """
        try:
            # 计算布局
            if layout_type == 'grid':
                layout = self.layout_engine.calculate_grid_layout(spacing_mm, margin_mm)
            else:
                layout = self.layout_engine.calculate_compact_layout(spacing_mm, margin_mm)
            
            # 创建PDF画布
            c = canvas.Canvas(output_path, pagesize=A4)

            # 转换比例（从像素到points）
            # 300 DPI: 1 inch = 300 pixels = 72 points
            pixel_to_point = 72.0 / PRINT_DPI
            
            # 处理每个图片
            positions = layout['positions']
            processed_count = 0
            
            for i, image_item in enumerate(image_items):
                if i >= len(positions):
                    break  # 超出可放置数量
                
                try:
                    # 获取圆形图片
                    circle_img = self.image_processor.create_circular_crop(
                        image_item.file_path,
                        image_item.scale,
                        image_item.offset_x,
                        image_item.offset_y,
                        image_item.rotation
                    )
                    
                    # 保存临时图片文件
                    temp_img_path = f"temp_circle_{i}.png"
                    circle_img.save(temp_img_path, "PNG", dpi=(PRINT_DPI, PRINT_DPI))
                    
                    # 计算在PDF中的位置
                    center_x_px, center_y_px = positions[i]
                    
                    # 转换坐标系（PDF坐标系原点在左下角）
                    center_x_pt = center_x_px * pixel_to_point
                    center_y_pt = (self.layout_engine.a4_height_px - center_y_px) * pixel_to_point
                    
                    # 计算图片左下角位置
                    img_size_pt = self.layout_engine.badge_diameter_px * pixel_to_point
                    x_pt = center_x_pt - img_size_pt / 2
                    y_pt = center_y_pt - img_size_pt / 2
                    
                    # 在PDF中绘制图片
                    c.drawImage(temp_img_path, x_pt, y_pt, 
                              width=img_size_pt, height=img_size_pt)
                    
                    # 删除临时文件
                    if os.path.exists(temp_img_path):
                        os.remove(temp_img_path)
                    
                    processed_count += 1
                    
                except Exception as e:
                    print(f"处理图片失败 {image_item.filename}: {e}")
                    continue
            
            # 添加页面信息（可选）
            self._add_page_info(c, processed_count, layout_type, spacing_mm, margin_mm)
            
            # 保存PDF
            c.save()
            
            return True, processed_count
            
        except Exception as e:
            print(f"PDF导出失败: {e}")
            return False, 0
    
    def export_to_image(self, image_items, output_path, format_type='PNG',
                       layout_type='grid', spacing_mm=DEFAULT_SPACING, margin_mm=DEFAULT_MARGIN):
        """
        导出为图片文件（PNG/JPG）
        参数:
            image_items: 图片项目列表
            output_path: 输出文件路径
            format_type: 图片格式 ('PNG' 或 'JPEG')
            layout_type: 布局类型
            spacing_mm: 间距
            margin_mm: 页边距
        返回: tuple - (是否成功, 处理数量)
        """
        try:
            # 计算布局
            if layout_type == 'grid':
                layout = self.layout_engine.calculate_grid_layout(spacing_mm, margin_mm)
            else:
                layout = self.layout_engine.calculate_compact_layout(spacing_mm, margin_mm)
            
            # 创建A4画布
            canvas_img = Image.new('RGB', (self.layout_engine.a4_width_px, self.layout_engine.a4_height_px), (255, 255, 255))
            
            # 处理每个图片
            positions = layout['positions']
            processed_count = 0
            
            for i, image_item in enumerate(image_items):
                if i >= len(positions):
                    break
                
                try:
                    # 获取圆形图片
                    circle_img = self.image_processor.create_circular_crop(
                        image_item.file_path,
                        image_item.scale,
                        image_item.offset_x,
                        image_item.offset_y,
                        image_item.rotation
                    )
                    
                    # 计算粘贴位置
                    center_x, center_y = positions[i]
                    paste_x = center_x - self.layout_engine.badge_radius_px
                    paste_y = center_y - self.layout_engine.badge_radius_px
                    
                    # 粘贴到画布（使用透明度遮罩）
                    if circle_img.mode == 'RGBA':
                        canvas_img.paste(circle_img, (paste_x, paste_y), circle_img)
                    else:
                        canvas_img.paste(circle_img, (paste_x, paste_y))
                    
                    processed_count += 1
                    
                except Exception as e:
                    print(f"处理图片失败 {image_item.filename}: {e}")
                    continue
            
            # 保存图片
            if format_type.upper() == 'JPEG':
                canvas_img.save(output_path, "JPEG", quality=95, dpi=(PRINT_DPI, PRINT_DPI))
            else:
                canvas_img.save(output_path, "PNG", dpi=(PRINT_DPI, PRINT_DPI))
            
            return True, processed_count
            
        except Exception as e:
            print(f"图片导出失败: {e}")
            return False, 0
    
    def _add_page_info(self, canvas_obj, image_count, layout_type, spacing_mm, margin_mm):
        """
        在PDF中添加页面信息
        参数:
            canvas_obj: reportlab画布对象
            image_count: 图片数量
            layout_type: 布局类型
            spacing_mm: 间距
            margin_mm: 页边距
        """
        try:
            # 设置字体
            canvas_obj.setFont("Helvetica", 8)
            
            # 页面底部信息
            info_text = f"BadgePatternTool | Images: {image_count} | Layout: {layout_type} | " \
                       f"Spacing: {spacing_mm}mm | Margin: {margin_mm}mm | " \
                       f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # 在页面底部绘制信息
            canvas_obj.drawString(20, 20, info_text)
            
        except Exception as e:
            print(f"添加页面信息失败: {e}")
    
    def get_suggested_filename(self, format_type='PDF', layout_type='grid'):
        """
        获取建议的文件名
        参数:
            format_type: 文件格式
            layout_type: 布局类型
        返回: str - 建议的文件名
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        layout_name = '网格' if layout_type == 'grid' else '紧密'
        
        filename = f"徽章排版_{layout_name}_{timestamp}.{format_type.lower()}"
        return filename
    
    def validate_export_settings(self, image_items, output_path):
        """
        验证导出设置
        参数:
            image_items: 图片项目列表
            output_path: 输出路径
        返回: tuple - (是否有效, 错误信息)
        """
        # 检查图片列表
        if not image_items:
            return False, "没有可导出的图片"
        
        # 检查是否有已处理的图片
        processed_items = [item for item in image_items if item.is_processed]
        if not processed_items:
            return False, "没有已处理的图片，请先编辑图片或使用自动排版"
        
        # 检查输出路径
        if not output_path:
            return False, "请指定输出文件路径"
        
        # 检查输出目录是否存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                return False, f"无法创建输出目录: {str(e)}"
        
        # 检查文件是否可写
        try:
            # 尝试创建测试文件
            test_path = output_path + ".test"
            with open(test_path, 'w') as f:
                f.write("test")
            os.remove(test_path)
        except Exception as e:
            return False, f"无法写入文件: {str(e)}"
        
        return True, ""
