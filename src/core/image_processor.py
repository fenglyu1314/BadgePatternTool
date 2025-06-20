"""
图片处理核心模块
实现圆形裁剪、缩放、移动等图片处理功能
"""

from io import BytesIO
from dataclasses import dataclass

# 导入公共模块
from common.imports import PIL_AVAILABLE, PYSIDE6_AVAILABLE, Image, ImageDraw, QPixmap
from common.error_handler import error_handler, resource_manager, logger, ImageProcessingError
from utils.config import app_config

@dataclass
class ImageProcessParams:
    """图片处理参数类"""
    image_path: str
    scale: float = 1.0
    offset_x: int = 0
    offset_y: int = 0
    rotation: int = 0

    def to_cache_key(self, extra=""):
        """生成缓存键"""
        return f"{self.image_path}:{self.scale}:{self.offset_x}:{self.offset_y}:{self.rotation}:{extra}"



class ImageProcessor:
    """图片处理器类"""
    
    def __init__(self):
        # 图片处理缓存
        self._crop_cache = {}
        self._preview_cache = {}
        self._max_cache_size = 30  # 减少缓存数量，节省内存
        self._max_preview_cache_size = 20  # 预览缓存单独限制

        # 缓存访问时间记录（用于LRU策略）
        self._cache_access_time = {}
        self._access_counter = 0

        # 内存使用监控
        self._cache_memory_limit = 100 * 1024 * 1024  # 100MB内存限制
        self._current_memory_usage = 0

    @property
    def badge_diameter_px(self):
        """获取当前圆形直径（像素）"""
        return app_config.badge_diameter_px

    @property
    def badge_radius_px(self):
        """获取当前圆形半径（像素）"""
        return app_config.badge_radius_px

    def _manage_cache(self, cache_dict, is_preview_cache=False):
        """管理缓存大小，防止内存过度使用（改进的LRU策略）"""
        max_size = self._max_preview_cache_size if is_preview_cache else self._max_cache_size

        # 检查缓存数量限制
        while len(cache_dict) > max_size:
            self._remove_oldest_cache_item(cache_dict)

        # 检查内存使用限制（估算）
        if self._current_memory_usage > self._cache_memory_limit:
            self._cleanup_memory_intensive_cache(cache_dict)

    def _remove_oldest_cache_item(self, cache_dict):
        """移除最旧的缓存项"""
        if self._cache_access_time:
            # 按访问时间排序，删除最旧的
            oldest_key = min(self._cache_access_time.keys(),
                           key=lambda k: self._cache_access_time.get(k, 0))
            if oldest_key in cache_dict:
                self._remove_cache_item(cache_dict, oldest_key)
        else:
            # 降级到简单策略
            if cache_dict:
                oldest_key = next(iter(cache_dict))
                self._remove_cache_item(cache_dict, oldest_key)

    def _remove_cache_item(self, cache_dict, key):
        """安全移除缓存项并释放内存"""
        try:
            if key in cache_dict:
                item = cache_dict[key]
                # 估算释放的内存
                if hasattr(item, 'size'):
                    # PIL Image对象
                    estimated_size = item.size[0] * item.size[1] * 3  # RGB
                    self._current_memory_usage -= estimated_size
                elif hasattr(item, 'width'):
                    # QPixmap对象
                    estimated_size = item.width() * item.height() * 4  # RGBA
                    self._current_memory_usage -= estimated_size

                del cache_dict[key]
                if key in self._cache_access_time:
                    del self._cache_access_time[key]

                logger.debug(f"移除缓存项: {key}")
        except Exception as e:
            logger.warning(f"移除缓存项失败: {e}")

    def _cleanup_memory_intensive_cache(self, cache_dict):
        """清理内存密集型缓存"""
        # 移除一半的缓存项以释放内存
        items_to_remove = len(cache_dict) // 2
        for _ in range(items_to_remove):
            if cache_dict:
                self._remove_oldest_cache_item(cache_dict)
            else:
                break
        logger.info(f"内存清理完成，当前估算内存使用: {self._current_memory_usage / 1024 / 1024:.1f}MB")

    def _update_cache_access(self, cache_key):
        """更新缓存访问时间"""
        self._access_counter += 1
        self._cache_access_time[cache_key] = self._access_counter

    def clear_cache(self):
        """清空所有缓存，释放内存"""
        self._crop_cache.clear()
        self._preview_cache.clear()
        self._cache_access_time.clear()
        if hasattr(self, '_mask_cache'):
            self._mask_cache.clear()
        self._current_memory_usage = 0
        self._access_counter = 0
        logger.info("图片处理缓存已清空")

    def get_cache_info(self):
        """获取缓存信息"""
        return {
            'crop_cache_size': len(self._crop_cache),
            'preview_cache_size': len(self._preview_cache),
            'estimated_memory_mb': self._current_memory_usage / 1024 / 1024,
            'access_counter': self._access_counter
        }

    def _get_cache_key(self, params, extra=""):
        """生成缓存键"""
        if isinstance(params, ImageProcessParams):
            return params.to_cache_key(extra)
        else:
            # 兼容旧接口
            image_path, scale, offset_x, offset_y, rotation = params
            return f"{image_path}:{scale}:{offset_x}:{offset_y}:{rotation}:{extra}"

    @error_handler("圆形裁剪失败", show_error=False)
    def create_circular_crop(self, image_path=None, scale=1.0, offset_x=0, offset_y=0, rotation=0, params=None):
        """
        创建圆形裁剪（带缓存优化）
        参数:
            image_path: 图片路径（兼容旧接口）
            scale: 缩放比例 (1.0 = 原始大小)
            offset_x: X轴偏移 (像素)
            offset_y: Y轴偏移 (像素)
            rotation: 旋转角度 (度)
            params: ImageProcessParams对象（推荐使用）
        返回: PIL.Image - 裁剪后的圆形图片
        """
        # 处理参数
        if params is not None:
            process_params = params
        else:
            if image_path is None:
                raise ImageProcessingError("必须提供image_path或params参数")
            process_params = ImageProcessParams(image_path, scale, offset_x, offset_y, rotation)

        # 检查缓存
        cache_key = process_params.to_cache_key()
        if cache_key in self._crop_cache:
            self._update_cache_access(cache_key)  # 更新访问时间
            return self._crop_cache[cache_key].copy()  # 返回副本避免修改缓存

        try:
            # 打开原始图片
            with Image.open(process_params.image_path) as original_img:
                # 转换为RGB模式
                if original_img.mode != 'RGB':
                    original_img = original_img.convert('RGB')

                # 应用旋转
                if process_params.rotation != 0:
                    original_img = original_img.rotate(process_params.rotation, expand=True, fillcolor=(255, 255, 255))

                # 计算缩放后的尺寸
                orig_width, orig_height = original_img.size
                new_width = int(orig_width * process_params.scale)
                new_height = int(orig_height * process_params.scale)

                # 应用缩放
                if process_params.scale != 1.0:
                    original_img = original_img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # 创建圆形裁剪区域
                circle_img = self._crop_to_circle(original_img, process_params.offset_x, process_params.offset_y)

                # 缓存结果
                self._manage_cache(self._crop_cache)
                cached_img = circle_img.copy()
                self._crop_cache[cache_key] = cached_img

                # 估算内存使用
                estimated_size = cached_img.size[0] * cached_img.size[1] * 4  # RGBA
                self._current_memory_usage += estimated_size

                return circle_img
                
        except Exception as e:
            logger.error(f"圆形裁剪失败: {e}", exc_info=True)
            # 返回空白圆形图片
            return self._create_blank_circle()
    
    def _crop_to_circle(self, img, offset_x=0, offset_y=0):
        """
        将图片裁剪为圆形（优化版本）
        参数:
            img: PIL.Image对象
            offset_x: X轴偏移
            offset_y: Y轴偏移
        返回: PIL.Image - 圆形图片
        """
        circle_size = self.badge_diameter_px
        img_width, img_height = img.size

        # 计算粘贴位置
        center_x = circle_size // 2
        center_y = circle_size // 2
        paste_x = center_x - img_width // 2 + offset_x
        paste_y = center_y - img_height // 2 + offset_y

        # 优化：直接创建RGBA图像，避免多次转换
        circle_img = Image.new('RGBA', (circle_size, circle_size), (255, 255, 255, 0))

        # 优化：只在图片与圆形有交集时才进行处理
        if (paste_x < circle_size and paste_y < circle_size and
            paste_x + img_width > 0 and paste_y + img_height > 0):

            # 创建白色背景并粘贴图片
            temp_canvas = Image.new('RGB', (circle_size, circle_size), (255, 255, 255))
            temp_canvas.paste(img, (paste_x, paste_y))

            # 创建圆形遮罩（复用遮罩以提高性能）
            mask = self._get_circle_mask(circle_size)

            # 应用遮罩
            circle_img.paste(temp_canvas, (0, 0))
            circle_img.putalpha(mask)

        return circle_img

    def _get_circle_mask(self, size):
        """获取圆形遮罩（带缓存）"""
        mask_key = f"mask_{size}"
        if not hasattr(self, '_mask_cache'):
            self._mask_cache = {}

        if mask_key not in self._mask_cache:
            mask = Image.new('L', (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse([0, 0, size, size], fill=255)
            self._mask_cache[mask_key] = mask

        return self._mask_cache[mask_key]
    
    def _create_blank_circle(self):
        """创建空白圆形图片"""
        circle_size = self.badge_diameter_px
        img = Image.new('RGB', (circle_size, circle_size), (240, 240, 240))
        
        # 绘制圆形边框
        draw = ImageDraw.Draw(img)
        draw.ellipse([2, 2, circle_size-2, circle_size-2], outline=(200, 200, 200), width=2)
        
        return img
    
    def create_preview_image(self, image_path=None, scale=1.0, offset_x=0, offset_y=0, rotation=0, preview_size=200, params=None):
        """
        创建预览图片（用于界面显示，带缓存优化）
        参数:
            image_path: 图片路径（兼容旧接口）
            scale: 缩放比例
            offset_x: X轴偏移
            offset_y: Y轴偏移
            rotation: 旋转角度
            preview_size: 预览图片大小
            params: ImageProcessParams对象（推荐使用）
        返回: QPixmap - 可用于PySide6显示的图片
        """
        if not PYSIDE6_AVAILABLE:
            logger.warning("PySide6不可用，无法创建预览图片")
            return None

        # 处理参数
        if params is not None:
            process_params = params
        else:
            if image_path is None:
                raise ImageProcessingError("必须提供image_path或params参数")
            process_params = ImageProcessParams(image_path, scale, offset_x, offset_y, rotation)

        # 检查预览缓存
        cache_key = process_params.to_cache_key(f"preview_{preview_size}")
        if cache_key in self._preview_cache:
            self._update_cache_access(cache_key)  # 更新访问时间
            return self._preview_cache[cache_key]

        try:
            # 创建圆形裁剪
            circle_img = self.create_circular_crop(params=process_params)

            # 缩放到预览大小
            if circle_img.size[0] != preview_size:
                circle_img = circle_img.resize((preview_size, preview_size), Image.Resampling.LANCZOS)

            # 转换为QPixmap
            with resource_manager(BytesIO()) as buffer:
                circle_img.save(buffer, format='PNG')
                buffer.seek(0)

                pixmap = QPixmap()
                pixmap.loadFromData(buffer.getvalue())

            # 缓存预览结果
            self._manage_cache(self._preview_cache, is_preview_cache=True)
            self._preview_cache[cache_key] = pixmap

            # 估算内存使用
            estimated_size = pixmap.width() * pixmap.height() * 4  # RGBA
            self._current_memory_usage += estimated_size

            return pixmap

        except Exception as e:
            logger.error(f"创建预览图片失败: {e}", exc_info=True)
            # 返回空白预览
            blank_pixmap = QPixmap(preview_size, preview_size)
            blank_pixmap.fill()  # 填充为白色
            return blank_pixmap
    
    def get_optimal_scale(self, image_path):
        """
        获取最佳缩放比例（使图片刚好填满圆形）
        参数:
            image_path: 图片路径
        返回: float - 最佳缩放比例
        """
        try:
            with Image.open(image_path) as img:
                img_width, img_height = img.size
                
                # 计算使图片完全填满圆形所需的缩放比例
                # 取较小边的缩放比例，确保图片完全覆盖圆形
                scale_x = self.badge_diameter_px / img_width
                scale_y = self.badge_diameter_px / img_height
                
                # 使用较大的缩放比例确保完全覆盖
                optimal_scale = max(scale_x, scale_y)
                
                return optimal_scale
                
        except Exception as e:
            logger.error(f"计算最佳缩放比例失败: {e}", exc_info=True)
            return 1.0
    
    def get_max_offset_range(self, image_path, scale=1.0):
        """
        获取最大偏移范围
        参数:
            image_path: 图片路径
            scale: 当前缩放比例
        返回: tuple - (max_offset_x, max_offset_y)
        """
        try:
            with Image.open(image_path) as img:
                img_width, img_height = img.size
                
                # 计算缩放后的尺寸
                scaled_width = int(img_width * scale)
                scaled_height = int(img_height * scale)
                
                # 计算最大偏移（图片边缘刚好接触圆形边缘）
                max_offset_x = max(0, (scaled_width - self.badge_diameter_px) // 2)
                max_offset_y = max(0, (scaled_height - self.badge_diameter_px) // 2)
                
                return max_offset_x, max_offset_y
                
        except Exception as e:
            logger.error(f"计算最大偏移范围失败: {e}", exc_info=True)
            return 0, 0

class CircleEditor:
    """圆形编辑器类，用于交互式编辑"""
    
    def __init__(self, image_path):
        self.image_path = image_path
        self.processor = ImageProcessor()
        
        # 编辑参数
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.rotation = 0
        
        # 获取最佳初始缩放
        self.reset_to_optimal()
    
    def reset_to_optimal(self):
        """重置到最佳参数"""
        self.scale = self.processor.get_optimal_scale(self.image_path)
        self.offset_x = 0
        self.offset_y = 0
        self.rotation = 0
    
    def set_scale(self, scale):
        """设置缩放比例"""
        self.scale = max(0.1, min(5.0, scale))  # 限制缩放范围
    
    def set_offset(self, offset_x, offset_y):
        """设置偏移"""
        max_x, max_y = self.processor.get_max_offset_range(self.image_path, self.scale)
        self.offset_x = max(-max_x, min(max_x, offset_x))
        self.offset_y = max(-max_y, min(max_y, offset_y))
    
    def set_rotation(self, rotation):
        """设置旋转角度"""
        self.rotation = rotation % 360
    
    def get_preview(self, preview_size=200):
        """获取当前参数的预览图片"""
        return self.processor.create_preview_image(
            self.image_path, self.scale, self.offset_x, self.offset_y, self.rotation, preview_size
        )
    
    def get_final_image(self):
        """获取最终的圆形图片"""
        return self.processor.create_circular_crop(
            self.image_path, self.scale, self.offset_x, self.offset_y, self.rotation
        )
