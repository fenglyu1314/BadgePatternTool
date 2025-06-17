"""
交互式预览标签
支持鼠标滚轮缩放和拖动平移的QLabel子类
"""

from PySide6.QtWidgets import QLabel, QScrollArea
from PySide6.QtCore import Qt, QPoint, QRect, Signal
from PySide6.QtGui import QPixmap, QWheelEvent, QMouseEvent, QPaintEvent, QPainter, QColor, QPen


class InteractivePreviewLabel(QLabel):
    """
    交互式预览标签
    支持鼠标滚轮缩放和拖动平移
    """
    
    # 信号：缩放比例改变
    scale_changed = Signal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 缩放相关
        self.scale_factor = 1.0
        self.min_scale = 0.1
        self.max_scale = 3.0
        self.scale_step = 0.1
        
        # 拖动相关
        self.dragging = False
        self.last_pan_point = QPoint()
        self.pan_offset = QPoint(0, 0)
        
        # 原始图片
        self.original_pixmap = None
        self.scaled_pixmap = None
        
        # 设置鼠标跟踪
        self.setMouseTracking(True)
        
        # 设置样式 - A4画布保持白色背景，添加阴影效果
        self.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #aaa;
                border-radius: 2px;
            }
        """)
        self.setAlignment(Qt.AlignCenter)
        
    def set_pixmap(self, pixmap):
        """设置要显示的图片"""
        if pixmap and not pixmap.isNull():
            self.original_pixmap = pixmap
            self.update_display()
        else:
            self.original_pixmap = None
            self.scaled_pixmap = None
            self.clear()
    
    def update_display(self):
        """更新显示"""
        if not self.original_pixmap:
            return
            
        # 计算缩放后的尺寸
        scaled_size = self.original_pixmap.size() * self.scale_factor
        
        # 创建缩放后的图片
        self.scaled_pixmap = self.original_pixmap.scaled(
            scaled_size, 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        # 更新显示
        self.setPixmap(self.scaled_pixmap)
        
        # 发送缩放改变信号
        self.scale_changed.emit(self.scale_factor)
    
    def fit_to_window(self):
        """适应窗口大小"""
        if not self.original_pixmap:
            return
            
        # 计算适应窗口的缩放比例
        widget_size = self.size()
        pixmap_size = self.original_pixmap.size()
        
        scale_x = widget_size.width() / pixmap_size.width()
        scale_y = widget_size.height() / pixmap_size.height()
        
        # 使用较小的缩放比例确保完全显示
        self.scale_factor = min(scale_x, scale_y, 1.0)  # 不超过原始大小
        self.scale_factor = max(self.scale_factor, self.min_scale)
        
        # 重置平移偏移
        self.pan_offset = QPoint(0, 0)
        
        self.update_display()
    
    def reset_view(self):
        """重置视图"""
        self.scale_factor = 1.0
        self.pan_offset = QPoint(0, 0)
        self.update_display()
    
    def wheelEvent(self, event: QWheelEvent):
        """鼠标滚轮事件 - 缩放"""
        if not self.original_pixmap:
            return
            
        # 获取滚轮增量
        delta = event.angleDelta().y()
        
        # 计算缩放因子
        if delta > 0:
            # 向上滚动 - 放大
            new_scale = self.scale_factor + self.scale_step
        else:
            # 向下滚动 - 缩小
            new_scale = self.scale_factor - self.scale_step
        
        # 限制缩放范围
        new_scale = max(self.min_scale, min(self.max_scale, new_scale))
        
        if new_scale != self.scale_factor:
            self.scale_factor = new_scale
            self.update_display()
        
        event.accept()
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件 - 开始拖动"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.last_pan_point = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件 - 拖动"""
        if self.dragging and self.scaled_pixmap:
            # 计算移动距离
            delta = event.pos() - self.last_pan_point
            self.pan_offset += delta
            self.last_pan_point = event.pos()
            
            # 更新显示位置（这里简化处理，实际可以通过重写paintEvent实现更精确的控制）
            self.update()
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件 - 结束拖动"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.setCursor(Qt.ArrowCursor)
        
        super().mouseReleaseEvent(event)
    
    def paintEvent(self, event: QPaintEvent):
        """绘制事件 - 支持平移显示，添加A4画布阴影效果"""
        if not self.scaled_pixmap:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 计算绘制位置（居中 + 平移偏移）
        widget_rect = self.rect()
        pixmap_rect = self.scaled_pixmap.rect()

        # 居中位置
        center_x = (widget_rect.width() - pixmap_rect.width()) // 2
        center_y = (widget_rect.height() - pixmap_rect.height()) // 2

        # 加上平移偏移
        draw_x = center_x + self.pan_offset.x()
        draw_y = center_y + self.pan_offset.y()

        # 绘制A4画布阴影
        shadow_offset = 3
        shadow_rect = QRect(draw_x + shadow_offset, draw_y + shadow_offset,
                           pixmap_rect.width(), pixmap_rect.height())
        painter.fillRect(shadow_rect, QColor(0, 0, 0, 50))  # 半透明黑色阴影

        # 绘制A4画布白色背景
        canvas_rect = QRect(draw_x, draw_y, pixmap_rect.width(), pixmap_rect.height())
        painter.fillRect(canvas_rect, Qt.white)

        # 绘制A4画布边框
        painter.setPen(QPen(QColor(170, 170, 170), 1))
        painter.drawRect(canvas_rect)

        # 绘制图片内容
        painter.drawPixmap(draw_x, draw_y, self.scaled_pixmap)

        painter.end()
    
    def get_scale_factor(self):
        """获取当前缩放比例"""
        return self.scale_factor
    
    def set_scale_factor(self, scale):
        """设置缩放比例"""
        scale = max(self.min_scale, min(self.max_scale, scale))
        if scale != self.scale_factor:
            self.scale_factor = scale
            self.update_display()


class InteractiveScrollArea(QScrollArea):
    """
    交互式滚动区域
    包含InteractivePreviewLabel的滚动区域
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 创建交互式标签
        self.preview_label = InteractivePreviewLabel()
        self.setWidget(self.preview_label)
        
        # 设置滚动区域属性
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # 设置灰色背景以突出A4画布，并添加阴影效果
        self.setStyleSheet("""
            QScrollArea {
                background-color: #d0d0d0;
                border: 1px solid #999;
                border-radius: 4px;
            }
            QScrollArea > QWidget {
                background-color: #d0d0d0;
            }
        """)

        # 连接信号
        self.preview_label.scale_changed.connect(self.on_scale_changed)
    
    def set_pixmap(self, pixmap):
        """设置图片"""
        self.preview_label.set_pixmap(pixmap)
        # 默认适应窗口
        self.preview_label.fit_to_window()
    
    def fit_to_window(self):
        """适应窗口"""
        self.preview_label.fit_to_window()
    
    def reset_view(self):
        """重置视图"""
        self.preview_label.reset_view()
    
    def get_scale_factor(self):
        """获取缩放比例"""
        return self.preview_label.get_scale_factor()
    
    def on_scale_changed(self, scale):
        """缩放改变事件"""
        # 可以在这里添加缩放改变的处理逻辑
        # scale: 当前缩放比例
        pass
