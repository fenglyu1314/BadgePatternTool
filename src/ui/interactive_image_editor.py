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


class InteractiveImageEditor(QLabel):
    """交互式图片编辑器"""

    # 参数改变信号
    parameters_changed = Signal(float, int, int)  # scale, offset_x, offset_y

    def __init__(self):
        super().__init__()

        # 图片相关
        self.original_image = None  # PIL Image对象
        self.image_path = None

        # 编辑参数
        self.image_scale = 1.0  # 图片缩放比例
        self.image_offset = QPoint(0, 0)  # 图片偏移
        self.min_scale = 0.1
        self.max_scale = 5.0

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

        # 缩放防抖定时器
        from PySide6.QtCore import QTimer
        self._scale_timer = QTimer()
        self._scale_timer.setSingleShot(True)
        self._scale_timer.timeout.connect(self._delayed_scale_update)
        self._pending_scale = None

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

        # 计算显示半径与实际徽章半径的比例
        # 这个比例将用于确保预览效果与实际裁剪效果一致
        actual_radius_px = app_config.badge_radius_px  # 实际半径（约401像素）
        self.display_to_actual_ratio = self.mask_radius / actual_radius_px

    def load_image(self, image_path):
        """加载图片"""
        try:
            self.image_path = image_path
            self.original_image = Image.open(image_path)

            # 转换为RGB模式
            if self.original_image.mode != 'RGB':
                self.original_image = self.original_image.convert('RGB')

            # 重新计算遮罩半径和比例（确保比例正确）
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

            return True

        except Exception as e:
            print(f"加载图片失败: {e}")
            self.original_image = None
            self.image_path = None
            self._invalidate_cache()
            self.update()
            return False
    
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

    def _invalidate_cache(self):
        """清除图片缓存"""
        # 显式删除QPixmap以释放内存
        if self._cached_pixmap:
            del self._cached_pixmap
        self._cached_pixmap = None
        self._cache_scale = None
        self._cache_size = None
        self._cache_valid = False

    def _is_cache_valid(self):
        """检查缓存是否有效"""
        if not self._cache_valid or not self._cached_pixmap:
            return False

        # 检查缩放比例是否改变
        if self._cache_scale != self.image_scale:
            return False

        # 检查图片尺寸是否改变
        if self.original_image:
            current_size = self.original_image.size
            if self._cache_size != current_size:
                return False

        return True
    
    def get_image_rect(self):
        """获取当前图片的显示矩形"""
        if not self.original_image:
            return QRect()

        # 计算缩放后的图片尺寸
        img_width, img_height = self.original_image.size
        scaled_width = int(img_width * self.image_scale)
        scaled_height = int(img_height * self.image_scale)

        # 关键修复：将实际尺寸按显示比例缩放，确保预览与实际裁剪一致
        if hasattr(self, 'display_to_actual_ratio'):
            display_scaled_width = int(scaled_width * self.display_to_actual_ratio)
            display_scaled_height = int(scaled_height * self.display_to_actual_ratio)
        else:
            # 降级处理：如果比例未计算，使用原始逻辑
            display_scaled_width = scaled_width
            display_scaled_height = scaled_height

        # 计算图片在编辑器中的位置（居中 + 偏移）
        editor_center_x = self.width() // 2
        editor_center_y = self.height() // 2

        # 优化：偏移量直接使用，不进行比例缩放，确保拖动响应自然
        display_offset_x = self.image_offset.x()
        display_offset_y = self.image_offset.y()

        img_x = editor_center_x - display_scaled_width // 2 + display_offset_x
        img_y = editor_center_y - display_scaled_height // 2 + display_offset_y

        return QRect(img_x, img_y, display_scaled_width, display_scaled_height)
    
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
            
            # 创建暗化遮罩
            self.draw_darkening_mask(painter, img_rect, mask_rect)
        
        # 绘制圆形遮罩边框
        self.draw_mask_border(painter, mask_rect)
        
        # 绘制中心十字线
        self.draw_center_crosshair(painter)
        
        painter.end()
    
    def create_image_pixmap(self):
        """创建图片的QPixmap（带缓存优化）"""
        if not self.original_image:
            return None

        # 检查缓存是否有效
        if self._is_cache_valid():
            return self._cached_pixmap

        try:
            # 计算缩放后的尺寸
            img_width, img_height = self.original_image.size
            scaled_width = int(img_width * self.image_scale)
            scaled_height = int(img_height * self.image_scale)

            # 缩放图片
            scaled_image = self.original_image.resize(
                (scaled_width, scaled_height),
                Image.Resampling.LANCZOS
            )

            # 转换为QPixmap
            buffer = BytesIO()
            try:
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
            print(f"创建图片pixmap失败: {e}")
            return None
    
    def draw_darkening_mask(self, painter, img_rect, mask_rect):
        """绘制暗化遮罩（圆形外部区域变暗）"""
        # 保存当前状态
        painter.save()
        
        # 设置半透明黑色
        painter.setBrush(QColor(0, 0, 0, 100))
        painter.setPen(Qt.NoPen)
        
        # 计算图片和遮罩的交集区域
        intersection = img_rect.intersected(self.rect())
        
        if not intersection.isEmpty():
            # 创建裁剪路径（排除圆形区域）
            from PySide6.QtGui import QPainterPath, QRegion
            
            # 创建整个图片区域的路径
            full_path = QPainterPath()
            full_path.addRect(intersection)
            
            # 创建圆形路径
            circle_path = QPainterPath()
            circle_path.addEllipse(mask_rect)
            
            # 从图片区域减去圆形区域
            darkening_path = full_path.subtracted(circle_path)
            
            # 绘制暗化区域
            painter.fillPath(darkening_path, QColor(0, 0, 0, 100))
        
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
            self._scale_timer.stop()
            self._scale_timer.start(50)  # 50ms防抖延迟

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
        """鼠标移动事件（优化拖动响应速度）"""
        if self.dragging and event.buttons() == Qt.LeftButton:
            # 计算拖拽偏移
            delta = event.pos() - self.last_drag_point

            # 优化：增加拖动敏感度，根据显示比例调整
            sensitivity_factor = 2.0  # 增加拖动敏感度
            if hasattr(self, 'display_to_actual_ratio') and self.display_to_actual_ratio > 0:
                # 根据显示比例调整敏感度，确保拖动距离合理
                adjusted_delta = QPoint(
                    int(delta.x() * sensitivity_factor / self.display_to_actual_ratio),
                    int(delta.y() * sensitivity_factor / self.display_to_actual_ratio)
                )
            else:
                adjusted_delta = delta * sensitivity_factor

            self.image_offset += adjusted_delta
            self.last_drag_point = event.pos()

            # 立即更新显示（拖动不影响缓存）
            self.update()
            self.emit_parameters_changed()
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
            self.dragging = False
            if self.original_image:
                self.setCursor(Qt.OpenHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        
        super().mouseReleaseEvent(event)
    
    def emit_parameters_changed(self):
        """发送参数改变信号"""
        if self.original_image:
            # 计算相对于图片中心的偏移（像素）
            offset_x = self.image_offset.x()
            offset_y = self.image_offset.y()
            
            self.parameters_changed.emit(self.image_scale, offset_x, offset_y)
    
    def set_parameters(self, scale, offset_x, offset_y):
        """设置编辑参数"""
        old_scale = self.image_scale
        self.image_scale = max(self.min_scale, min(self.max_scale, scale))
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
        
        return {
            'center_x': crop_center_x,
            'center_y': crop_center_y,
            'radius': crop_radius,
            'scale': self.image_scale,
            'offset_x': self.image_offset.x(),
            'offset_y': self.image_offset.y()
        }
