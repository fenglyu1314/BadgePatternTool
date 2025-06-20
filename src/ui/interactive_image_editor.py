"""
交互式图片编辑器模块
实现带圆形遮罩的图片编辑功能
"""

from PySide6.QtWidgets import QLabel, QWidget
from PySide6.QtCore import Qt, QPoint, Signal, QRect
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen, QWheelEvent, QMouseEvent, QPaintEvent
from PIL import Image
from io import BytesIO
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import app_config
from common.error_handler import logger, show_error_message, error_handler, resource_manager, ImageProcessingError


class InteractiveImageEditor(QLabel):
    """交互式图片编辑器"""

    # 参数改变信号
    parameters_changed = Signal(float, int, int)  # scale, offset_x, offset_y

    def __init__(self):
        super().__init__()

        # 图片相关
        self.original_image = None  # PIL Image对象（原始分辨率）
        self.preview_image = None   # PIL Image对象（预览分辨率）
        self.image_path = None
        self.preview_scale_ratio = 1.0  # 预览图与原图的比例

        # 编辑参数
        self.image_scale = 1.0  # 图片缩放比例
        self.image_offset = QPoint(0, 0)  # 图片偏移
        self.min_scale = 0.1
        self.max_scale = 10.0  # 将根据图片大小动态调整

        # 圆形遮罩参数 - 使用配置中的徽章尺寸
        self.update_mask_radius()

        # 交互状态
        self.dragging = False
        self.last_drag_point = QPoint()

        # 图片缓存 - 性能优化
        self._cached_pixmap = None
        self._cache_scale = None
        self._cache_size = None
        self._cache_valid = False

        # 性能优化设置
        self._max_preview_resolution = 1024  # 最大预览分辨率
        self._cache_tolerance = 0.01  # 缓存容差，减少频繁重建

        # 缩放防抖定时器
        from PySide6.QtCore import QTimer
        self._scale_timer = QTimer()
        self._scale_timer.setSingleShot(True)
        self._scale_timer.timeout.connect(self._delayed_scale_update)
        self._pending_scale = None

        # 大图片优化：多级缓存
        self._prescaled_cache = {}
        self._max_prescale_cache = 5
        self._is_large_image = False  # 标记是否为大图片

        # 设置基本属性
        self.setMinimumSize(300, 300)
        self.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 2px solid #ccc;
                border-radius: 4px;
            }
        """)

        # 启用鼠标跟踪
        self.setMouseTracking(True)

    def update_mask_radius(self):
        """更新遮罩半径以匹配配置中的徽章尺寸"""
        # 计算在编辑器中显示的合适半径
        # 关键：遮罩半径必须与实际徽章半径保持正确的比例关系

        # 编辑器的显示区域大小
        editor_size = min(self.width(), self.height()) if hasattr(self, 'width') else 320

        # 计算合适的显示半径（占编辑器的约1/3）
        base_display_radius = min(editor_size // 3, 120)  # 最大不超过120像素
        base_display_radius = max(base_display_radius, 60)  # 最小不少于60像素

        # 重要：保存显示半径，用于与实际徽章半径的比例计算
        self.mask_radius = base_display_radius

        # 关键修复：确保遮罩大小与A4预览中的圆形大小一致
        # A4预览中使用的是实际徽章半径，所以这里也应该基于实际半径计算
        actual_radius_px = app_config.badge_radius_px  # 实际徽章半径（约401像素）

        # 计算显示比例：显示半径 / 实际半径
        # 这个比例用于将实际坐标转换为显示坐标
        self.display_to_actual_ratio = self.mask_radius / actual_radius_px

    @error_handler("加载图片失败", show_error=True, default_return=False)
    def load_image(self, image_path):
        """加载图片（优化：使用预览分辨率提升性能）"""
        if not image_path or not os.path.exists(image_path):
            raise ImageProcessingError(f"图片文件不存在: {image_path}")

        with resource_manager(None) as _:
            self.image_path = image_path

            # 使用资源管理器安全打开图片
            with resource_manager(Image.open(image_path)) as img:
                self.original_image = img.copy()

            # 转换为RGB模式
            if self.original_image.mode != 'RGB':
                self.original_image = self.original_image.convert('RGB')

            # 创建预览分辨率的图片
            self._create_preview_image()

            # 重新计算遮罩半径和比例（确保比例正确）
            # 必须在创建预览图之后调用，因为需要preview_scale_ratio
            self.update_mask_radius()

            # 计算初始缩放比例（使图片适应编辑器大小）
            self.calculate_initial_scale()

            # 重置偏移
            self.image_offset = QPoint(0, 0)

            # 清除缓存
            self._invalidate_cache()

            # 更新显示
            self.update()

            # 发送参数改变信号
            self.emit_parameters_changed()

            logger.info(f"成功加载图片: {os.path.basename(image_path)}")
            return True
    
    def calculate_initial_scale(self):
        """计算初始缩放比例（使用与CircleEditor相同的最佳缩放逻辑）"""
        if not self.original_image:
            return

        # 获取图片尺寸
        img_width, img_height = self.original_image.size

        # 使用与CircleEditor相同的最佳缩放计算
        # 计算使图片完全填满圆形所需的缩放比例
        badge_diameter_px = app_config.badge_diameter_px
        scale_x = badge_diameter_px / img_width
        scale_y = badge_diameter_px / img_height

        # 使用较大的缩放比例确保完全覆盖圆形
        optimal_scale = max(scale_x, scale_y)

        self.image_scale = optimal_scale

        # 限制缩放范围
        self.image_scale = max(self.min_scale, min(self.max_scale, self.image_scale))

    def _create_preview_image(self):
        """创建预览分辨率的图片（激进优化策略）"""
        if not self.original_image:
            return

        orig_width, orig_height = self.original_image.size
        pixel_count = orig_width * orig_height

        # 标记是否为大图片
        self._is_large_image = pixel_count > 8000000  # 超过800万像素

        # 根据原图大小动态调整预览尺寸
        if pixel_count > 16000000:  # 超过1600万像素（4K+）
            max_preview_size = 400   # 4K+图片使用400px预览，极致优化
        elif pixel_count > 8000000:  # 超过800万像素
            max_preview_size = 600   # 大图片使用600px预览
        elif pixel_count > 2000000:  # 超过200万像素
            max_preview_size = 800   # 中等图片使用800px预览
        else:
            max_preview_size = 1200  # 小图片可以使用更高分辨率

        # 计算预览图的缩放比例
        if orig_width > max_preview_size or orig_height > max_preview_size:
            scale_ratio = min(max_preview_size / orig_width, max_preview_size / orig_height)
            preview_width = int(orig_width * scale_ratio)
            preview_height = int(orig_height * scale_ratio)

            # 对超大图片使用两步缩放策略
            if pixel_count > 16000000:
                # 第一步：快速缩放到中等尺寸
                temp_size = 1024
                temp_ratio = min(temp_size / orig_width, temp_size / orig_height)
                temp_width = int(orig_width * temp_ratio)
                temp_height = int(orig_height * temp_ratio)

                temp_image = self.original_image.resize(
                    (temp_width, temp_height),
                    Image.Resampling.NEAREST  # 快速缩放
                )

                # 第二步：精确缩放到目标尺寸
                self.preview_image = temp_image.resize(
                    (preview_width, preview_height),
                    Image.Resampling.LANCZOS  # 高质量缩放
                )
                del temp_image  # 立即释放
            else:
                # 普通图片直接缩放
                self.preview_image = self.original_image.resize(
                    (preview_width, preview_height),
                    Image.Resampling.LANCZOS
                )

            self.preview_scale_ratio = scale_ratio
        else:
            # 图片本身就不大，直接使用原图
            self.preview_image = self.original_image.copy()
            self.preview_scale_ratio = 1.0

        # 根据图片大小动态调整最大缩放倍数
        if pixel_count > 16000000:  # 4K+图片
            self.max_scale = 6.0  # 增加最大缩放倍数
        elif pixel_count > 8000000:  # 大图片
            self.max_scale = 8.0
        else:
            self.max_scale = 10.0  # 小图片可以更大缩放

    def _invalidate_cache(self):
        """清除图片缓存"""
        # 显式删除QPixmap以释放内存
        if self._cached_pixmap:
            del self._cached_pixmap
        self._cached_pixmap = None
        self._cache_scale = None
        self._cache_size = None
        self._cache_valid = False

        # 清除预缩放缓存
        for key in list(self._prescaled_cache.keys()):
            del self._prescaled_cache[key]
        self._prescaled_cache.clear()

    def _is_cache_valid(self):
        """检查缓存是否有效"""
        if not self._cache_valid or not self._cached_pixmap:
            return False

        # 检查缩放比例是否改变（使用动态容差，减少频繁重建）
        if self._cache_scale is None or abs(self._cache_scale - self.image_scale) > self._cache_tolerance:
            return False

        # 检查图片尺寸是否改变
        if self.original_image:
            current_size = self.original_image.size
            if self._cache_size != current_size:
                return False

        return True
    
    def get_image_rect(self):
        """获取当前图片的显示矩形（与A4预览保持一致的算法）"""
        if not self.original_image:
            return QRect()

        # 关键修复：使用原图尺寸和实际缩放比例，确保与A4预览一致
        # A4预览中使用的是原图尺寸 * image_scale，这里也应该使用相同的计算方式
        orig_width, orig_height = self.original_image.size
        scaled_width = int(orig_width * self.image_scale)
        scaled_height = int(orig_height * self.image_scale)

        # 将实际尺寸转换为显示尺寸（使用display_to_actual_ratio）
        display_width = int(scaled_width * self.display_to_actual_ratio)
        display_height = int(scaled_height * self.display_to_actual_ratio)

        # 编辑器中心（对应圆形遮罩中心）
        editor_center_x = self.width() // 2
        editor_center_y = self.height() // 2

        # 简化偏移计算：直接使用image_offset作为显示偏移
        # 这样与简化的拖动逻辑保持一致，确保1:1响应
        display_offset_x = self.image_offset.x()
        display_offset_y = self.image_offset.y()

        # 计算图片左上角位置（与图片处理器算法保持一致）
        img_x = editor_center_x - display_width // 2 + display_offset_x
        img_y = editor_center_y - display_height // 2 + display_offset_y

        return QRect(img_x, img_y, display_width, display_height)
    
    def get_mask_rect(self):
        """获取圆形遮罩的矩形"""
        # 遮罩始终在编辑器中心
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        mask_x = center_x - self.mask_radius
        mask_y = center_y - self.mask_radius
        mask_size = self.mask_radius * 2
        
        return QRect(mask_x, mask_y, mask_size, mask_size)
    
    def paintEvent(self, event: QPaintEvent):
        """自定义绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 填充背景
        painter.fillRect(self.rect(), QColor(240, 240, 240))

        if not self.original_image:
            # 显示提示文字
            painter.setPen(QColor(150, 150, 150))
            painter.drawText(self.rect(), Qt.AlignCenter, "点击加载图片")
            return

        # 获取图片和遮罩矩形
        img_rect = self.get_image_rect()
        mask_rect = self.get_mask_rect()

        # 创建图片的QPixmap
        img_pixmap = self.create_image_pixmap()

        if img_pixmap and not img_pixmap.isNull():
            # 绘制图片
            painter.drawPixmap(img_rect, img_pixmap)

        # 绘制暗化遮罩（覆盖整个编辑区域，包括空白区域）
        self.draw_darkening_mask(painter, mask_rect)

        # 绘制圆形遮罩边框
        self.draw_mask_border(painter, mask_rect)

        # 绘制安全区圆圈
        self.draw_safety_circle(painter, mask_rect)

        # 绘制中心十字线
        self.draw_center_crosshair(painter)

        painter.end()
    
    def create_image_pixmap(self):
        """创建图片的QPixmap（与A4预览保持一致的尺寸计算）"""
        if not self.original_image:
            return None

        # 检查缓存是否有效
        if self._is_cache_valid():
            return self._cached_pixmap

        try:
            # 关键修复：使用原图尺寸计算，确保与A4预览一致
            orig_width, orig_height = self.original_image.size
            scaled_width = int(orig_width * self.image_scale)
            scaled_height = int(orig_height * self.image_scale)

            # 转换为显示尺寸
            display_width = int(scaled_width * self.display_to_actual_ratio)
            display_height = int(scaled_height * self.display_to_actual_ratio)

            # 使用预览图进行缩放（性能优化），但最终尺寸要匹配显示需求
            if self.preview_image:
                preview_width, preview_height = self.preview_image.size

                # 对大图片使用更激进的优化策略
                if self._is_large_image and self.image_scale > 2.0:
                    # 大图片高倍缩放：使用更小的中间尺寸
                    intermediate_scale = min(2.0, self.image_scale / 2.0)
                    intermediate_width = int(preview_width * intermediate_scale)
                    intermediate_height = int(preview_height * intermediate_scale)

                    # 两步缩放：先缩放到中间尺寸，再缩放到目标尺寸
                    intermediate_image = self.preview_image.resize(
                        (intermediate_width, intermediate_height),
                        Image.Resampling.NEAREST  # 快速缩放
                    )

                    scaled_image = intermediate_image.resize(
                        (display_width, display_height),
                        Image.Resampling.LANCZOS  # 高质量缩放
                    )
                    del intermediate_image  # 立即释放
                else:
                    # 普通情况：直接缩放到显示尺寸
                    # 对于大倍数缩放，使用NEAREST算法提升性能
                    if self.image_scale > 2.5:
                        resample_method = Image.Resampling.NEAREST
                    else:
                        resample_method = Image.Resampling.LANCZOS

                    scaled_image = self.preview_image.resize(
                        (display_width, display_height),
                        resample_method
                    )
            else:
                # 降级处理：直接使用原图
                scaled_image = self.original_image.resize(
                    (display_width, display_height),
                    Image.Resampling.LANCZOS
                )

            # 转换为QPixmap（预览图片，性能优化）
            buffer = BytesIO()
            try:
                # 预览图片统一使用PNG格式，质量和性能平衡
                scaled_image.save(buffer, format='PNG')
                buffer.seek(0)

                pixmap = QPixmap()
                pixmap.loadFromData(buffer.getvalue())

                # 更新缓存
                self._cached_pixmap = pixmap
                self._cache_scale = self.image_scale
                self._cache_size = self.original_image.size
                self._cache_valid = True

                return pixmap
            finally:
                # 确保释放内存
                buffer.close()
                del scaled_image

        except Exception as e:
            logger.error(f"创建图片pixmap失败: {e}", exc_info=True)
            return None
    
    def draw_darkening_mask(self, painter, mask_rect):
        """绘制分层暗化遮罩（圆外区域更深，出血区稍微变暗）"""
        # 保存当前状态
        painter.save()

        from PySide6.QtGui import QPainterPath

        # 计算安全区域矩形（等于徽章尺寸，不含出血区）
        total_radius_mm = app_config.badge_diameter_mm / 2  # 总半径（包含出血区）
        safety_radius_mm = app_config.badge_size_mm / 2     # 安全区半径（等于徽章半径）

        display_radius = mask_rect.width() / 2  # 当前显示的总半径
        safety_display_radius = display_radius * (safety_radius_mm / total_radius_mm)

        center_x = mask_rect.center().x()
        center_y = mask_rect.center().y()
        safety_rect = QRect(
            int(center_x - safety_display_radius),
            int(center_y - safety_display_radius),
            int(safety_display_radius * 2),
            int(safety_display_radius * 2)
        )

        # 第一层：圆形外部区域（深色遮罩）
        outside_alpha = int(255 * app_config.outside_opacity / 100)
        painter.setBrush(QColor(0, 0, 0, outside_alpha))
        painter.setPen(Qt.PenStyle.NoPen)

        full_path = QPainterPath()
        full_path.addRect(self.rect())

        main_circle_path = QPainterPath()
        main_circle_path.addEllipse(mask_rect)

        outside_path = full_path.subtracted(main_circle_path)
        painter.fillPath(outside_path, QColor(0, 0, 0, outside_alpha))

        # 第二层：出血区（主圆内但安全区外的区域）
        bleed_alpha = int(255 * app_config.bleed_opacity / 100)
        painter.setBrush(QColor(0, 0, 0, bleed_alpha))

        safety_circle_path = QPainterPath()
        safety_circle_path.addEllipse(safety_rect)

        bleed_area_path = main_circle_path.subtracted(safety_circle_path)
        painter.fillPath(bleed_area_path, QColor(0, 0, 0, bleed_alpha))

        # 恢复状态
        painter.restore()
    
    def draw_mask_border(self, painter, mask_rect):
        """绘制圆形遮罩边框"""
        painter.save()
        
        # 设置边框样式
        pen = QPen(QColor(255, 255, 255), 2)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        
        # 绘制圆形边框
        painter.drawEllipse(mask_rect)
        
        painter.restore()

    def draw_safety_circle(self, painter, mask_rect):
        """绘制安全区边框（徽章尺寸，不含出血区）"""
        painter.save()



        # 计算安全区半径（等于徽章尺寸的一半）
        total_radius_mm = app_config.badge_diameter_mm / 2  # 总半径（包含出血区）
        safety_radius_mm = app_config.badge_size_mm / 2     # 安全区半径（等于徽章半径）

        # 计算显示比例
        display_radius = mask_rect.width() / 2  # 当前显示的总半径
        safety_display_radius = display_radius * (safety_radius_mm / total_radius_mm)

        # 计算安全区圆圈的矩形
        center_x = mask_rect.center().x()
        center_y = mask_rect.center().y()
        safety_rect = QRect(
            int(center_x - safety_display_radius),
            int(center_y - safety_display_radius),
            int(safety_display_radius * 2),
            int(safety_display_radius * 2)
        )

        # 设置安全区边框样式（橙色虚线）
        pen = QPen(QColor(255, 165, 0), 1)  # 橙色
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # 绘制安全区圆圈
        painter.drawEllipse(safety_rect)

        painter.restore()

    def draw_center_crosshair(self, painter):
        """绘制中心十字线"""
        painter.save()
        
        # 设置十字线样式
        pen = QPen(QColor(255, 255, 255), 1)
        pen.setStyle(Qt.DotLine)
        painter.setPen(pen)
        
        # 计算中心点
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # 绘制十字线
        crosshair_size = 20
        painter.drawLine(center_x - crosshair_size, center_y, 
                        center_x + crosshair_size, center_y)
        painter.drawLine(center_x, center_y - crosshair_size, 
                        center_x, center_y + crosshair_size)
        
        painter.restore()
    
    def wheelEvent(self, event: QWheelEvent):
        """鼠标滚轮缩放（优化性能，使用防抖）"""
        if not self.original_image:
            return

        # 计算缩放因子
        delta = event.angleDelta().y()
        zoom_in = delta > 0
        zoom_factor = 1.05 if zoom_in else 1.0 / 1.05  # 减小缩放步长，更平滑

        # 应用缩放
        new_scale = self.image_scale * zoom_factor
        new_scale = max(self.min_scale, min(self.max_scale, new_scale))

        if new_scale != self.image_scale:
            self.image_scale = new_scale
            self._pending_scale = new_scale

            # 立即更新显示（使用旧缓存）
            self.update()

            # 使用防抖定时器延迟更新缓存和信号
            # 根据图片大小和缩放倍数动态调整延迟
            if self._is_large_image and self.image_scale > 2.0:
                delay = 100  # 大图片高倍缩放使用长延迟
            elif self._is_large_image:
                delay = 60   # 大图片使用中等延迟
            else:
                delay = 30   # 小图片使用短延迟

            self._scale_timer.stop()
            self._scale_timer.start(delay)

        event.accept()

    def _delayed_scale_update(self):
        """延迟的缩放更新（清除缓存并发送信号）"""
        if self._pending_scale is not None:
            self._invalidate_cache()  # 清除缓存
            self.emit_parameters_changed()
            self._pending_scale = None
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton and self.original_image:
            self.dragging = True
            self.last_drag_point = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件（简化的1:1拖动响应）"""
        if self.dragging and event.buttons() == Qt.LeftButton:
            # 计算拖拽偏移
            delta = event.pos() - self.last_drag_point

            # 简化方案：直接使用鼠标移动距离，不进行复杂的坐标转换
            # 这样可以确保1:1的拖动响应，避免计算错误导致的中断
            self.image_offset += delta
            self.last_drag_point = event.pos()

            # 立即更新显示（拖动不影响缓存）
            self.update()

            # 优化：拖动过程中不发送信号，避免干扰拖动状态
            # 信号将在鼠标释放时发送
        else:
            # 设置光标
            if self.original_image:
                self.setCursor(Qt.OpenHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            was_dragging = self.dragging
            self.dragging = False

            # 如果刚才在拖动，现在发送参数改变信号
            if was_dragging and self.original_image:
                self.emit_parameters_changed()

            if self.original_image:
                self.setCursor(Qt.OpenHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

        super().mouseReleaseEvent(event)
    
    def emit_parameters_changed(self):
        """发送参数改变信号（简化的坐标转换）"""
        if self.original_image:
            # 简化方案：将显示偏移转换为原图坐标系
            # 考虑显示比例和预览比例的综合影响
            if self.preview_scale_ratio > 0 and self.display_to_actual_ratio > 0:
                # 显示偏移 -> 实际偏移 -> 原图偏移
                actual_offset_x = int(self.image_offset.x() / self.display_to_actual_ratio)
                actual_offset_y = int(self.image_offset.y() / self.display_to_actual_ratio)
            else:
                # 降级处理
                actual_offset_x = self.image_offset.x()
                actual_offset_y = self.image_offset.y()

            self.parameters_changed.emit(self.image_scale, actual_offset_x, actual_offset_y)
    
    def set_parameters(self, scale, offset_x, offset_y):
        """设置编辑参数（简化的坐标转换）"""
        old_scale = self.image_scale
        self.image_scale = max(self.min_scale, min(self.max_scale, scale))

        # 简化方案：将原图坐标系的偏移转换为显示坐标系
        if self.display_to_actual_ratio > 0:
            # 原图偏移 -> 显示偏移
            display_offset_x = int(offset_x * self.display_to_actual_ratio)
            display_offset_y = int(offset_y * self.display_to_actual_ratio)
            self.image_offset = QPoint(display_offset_x, display_offset_y)
        else:
            # 降级处理
            self.image_offset = QPoint(offset_x, offset_y)

        # 只有缩放改变时才清除缓存
        if old_scale != self.image_scale:
            self._invalidate_cache()

        self.update()
    
    def reset_view(self):
        """重置视图"""
        if self.original_image:
            self.calculate_initial_scale()
            self.image_offset = QPoint(0, 0)
            self.update()
            self.emit_parameters_changed()
    
    def get_crop_parameters(self):
        """获取裁剪参数（用于最终裁剪）"""
        if not self.original_image:
            return None
        
        # 计算圆形遮罩在原始图片中的位置和大小
        mask_rect = self.get_mask_rect()
        img_rect = self.get_image_rect()
        
        # 计算遮罩中心在图片中的相对位置
        mask_center_x = mask_rect.center().x()
        mask_center_y = mask_rect.center().y()
        
        # 转换为图片坐标系
        relative_x = (mask_center_x - img_rect.x()) / img_rect.width()
        relative_y = (mask_center_y - img_rect.y()) / img_rect.height()
        
        # 转换为原始图片像素坐标
        orig_width, orig_height = self.original_image.size
        crop_center_x = relative_x * orig_width
        crop_center_y = relative_y * orig_height
        
        # 计算裁剪半径（在原始图片中）
        # 需要将显示半径转换为实际的徽章半径
        actual_badge_radius_px = app_config.badge_radius_px
        crop_radius = actual_badge_radius_px / self.image_scale
        
        # 返回原图坐标系的参数
        actual_offset_x = int(self.image_offset.x() / self.preview_scale_ratio)
        actual_offset_y = int(self.image_offset.y() / self.preview_scale_ratio)

        return {
            'center_x': crop_center_x,
            'center_y': crop_center_y,
            'radius': crop_radius,
            'scale': self.image_scale,
            'offset_x': actual_offset_x,
            'offset_y': actual_offset_y
        }

    def debug_parameters(self):
        """调试参数转换（用于验证坐标系转换是否正确）"""
        if not self.original_image:
            return

        print(f"=== 参数调试信息 ===")
        print(f"原图尺寸: {self.original_image.size}")
        print(f"预览图尺寸: {self.preview_image.size if self.preview_image else 'None'}")
        print(f"预览缩放比例: {self.preview_scale_ratio}")
        print(f"当前缩放: {self.image_scale}")
        print(f"预览偏移: ({self.image_offset.x()}, {self.image_offset.y()})")

        # 计算原图偏移
        if self.preview_scale_ratio > 0:
            actual_offset_x = int(self.image_offset.x() / self.preview_scale_ratio)
            actual_offset_y = int(self.image_offset.y() / self.preview_scale_ratio)
        else:
            actual_offset_x = self.image_offset.x()
            actual_offset_y = self.image_offset.y()

        print(f"原图偏移: ({actual_offset_x}, {actual_offset_y})")

        # 调试遮罩和图片位置关系
        print(f"=== 显示调试信息 ===")
        print(f"编辑器尺寸: {self.width()}x{self.height()}")
        print(f"遮罩半径: {self.mask_radius}")
        print(f"显示到实际比例: {self.display_to_actual_ratio}")

        mask_rect = self.get_mask_rect()
        img_rect = self.get_image_rect()
        print(f"遮罩矩形: ({mask_rect.x()}, {mask_rect.y()}, {mask_rect.width()}, {mask_rect.height()})")
        print(f"图片矩形: ({img_rect.x()}, {img_rect.y()}, {img_rect.width()}, {img_rect.height()})")
        print(f"===================")
