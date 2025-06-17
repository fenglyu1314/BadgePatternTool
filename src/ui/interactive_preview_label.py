"""
交互式预览标签模块
实现支持缩放、拖拽的A4预览组件
"""

from PySide6.QtWidgets import QLabel, QScrollArea
from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QPixmap, QWheelEvent, QMouseEvent


class InteractivePreviewLabel(QLabel):
    """支持缩放和拖拽的A4预览标签"""

    # 缩放改变信号
    scale_changed = Signal(float)

    def __init__(self):
        super().__init__()

        # A4纸张尺寸（毫米）
        self.a4_width_mm = 210
        self.a4_height_mm = 297

        # 基础显示尺寸（像素）- A4比例
        self.base_width = 400
        self.base_height = int(self.base_width * (self.a4_height_mm / self.a4_width_mm))  # 约566像素

        # 缩放相关
        self.scale_factor = 1.0
        self.min_scale = 0.1
        self.max_scale = 5.0

        # A4画布位置（用于拖拽）
        self.canvas_offset = QPoint(0, 0)

        # 拖拽相关
        self.dragging = False
        self.last_pan_point = QPoint()

        # 设置基本属性 - 移除居中对齐，因为我们要自定义绘制
        self.setMinimumSize(200, 200)

        # 设置透明背景，因为我们要在paintEvent中自定义绘制
        self.setStyleSheet("""
            QLabel {
                background-color: transparent;
            }
        """)

        # 启用鼠标跟踪
        self.setMouseTracking(True)

        # 排版内容pixmap
        self.content_pixmap = None
    
    def set_pixmap(self, pixmap):
        """设置排版内容pixmap"""
        self.content_pixmap = pixmap
        self.update()  # 触发重绘

    def get_a4_canvas_rect(self):
        """获取A4画布的矩形区域"""
        from PySide6.QtCore import QRect

        # 计算当前A4画布的显示尺寸
        current_width = int(self.base_width * self.scale_factor)
        current_height = int(self.base_height * self.scale_factor)

        # 计算A4画布在控件中的位置（居中 + 偏移）
        widget_center_x = self.width() // 2
        widget_center_y = self.height() // 2

        canvas_x = widget_center_x - current_width // 2 + self.canvas_offset.x()
        canvas_y = widget_center_y - current_height // 2 + self.canvas_offset.y()

        return QRect(canvas_x, canvas_y, current_width, current_height)

    def paintEvent(self, event):
        """自定义绘制事件"""
        from PySide6.QtGui import QPainter, QColor, QPen

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 获取A4画布矩形
        canvas_rect = self.get_a4_canvas_rect()

        # 绘制A4画布阴影（偏移几个像素）
        shadow_rect = canvas_rect.adjusted(4, 4, 4, 4)
        painter.fillRect(shadow_rect, QColor(0, 0, 0, 50))  # 半透明黑色阴影

        # 绘制A4画布背景（白色）
        painter.fillRect(canvas_rect, QColor(255, 255, 255))

        # 绘制A4画布边框
        pen = QPen(QColor(119, 119, 119), 2)  # #777 颜色
        painter.setPen(pen)
        painter.drawRect(canvas_rect)

        # 如果有排版内容，绘制到A4画布上
        if self.content_pixmap and not self.content_pixmap.isNull():
            painter.setRenderHint(QPainter.SmoothPixmapTransform)

            # 将排版内容缩放到当前A4画布尺寸
            scaled_content = self.content_pixmap.scaled(
                canvas_rect.width(), canvas_rect.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

            # 居中绘制排版内容
            content_x = canvas_rect.x() + (canvas_rect.width() - scaled_content.width()) // 2
            content_y = canvas_rect.y() + (canvas_rect.height() - scaled_content.height()) // 2
            painter.drawPixmap(content_x, content_y, scaled_content)

        painter.end()
    
    def wheelEvent(self, event: QWheelEvent):
        """鼠标滚轮缩放A4画布"""
        # 计算缩放因子
        delta = event.angleDelta().y()
        zoom_in = delta > 0
        zoom_factor = 1.1 if zoom_in else 1.0 / 1.1

        # 应用缩放
        new_scale = self.scale_factor * zoom_factor
        new_scale = max(self.min_scale, min(self.max_scale, new_scale))

        if new_scale != self.scale_factor:
            self.scale_factor = new_scale
            self.update()  # 触发重绘
            self.scale_changed.emit(self.scale_factor)

        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            # 检查是否点击在A4画布区域内
            canvas_rect = self.get_a4_canvas_rect()
            if canvas_rect.contains(event.pos()):
                self.dragging = True
                self.last_pan_point = event.pos()
                self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件"""
        if self.dragging and event.buttons() == Qt.LeftButton:
            # 计算拖拽偏移
            delta = event.pos() - self.last_pan_point
            self.canvas_offset += delta
            self.last_pan_point = event.pos()
            self.update()  # 触发重绘
        else:
            # 检查鼠标是否在A4画布区域内，改变光标
            canvas_rect = self.get_a4_canvas_rect()
            if canvas_rect.contains(event.pos()):
                self.setCursor(Qt.OpenHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            # 检查鼠标是否还在A4画布区域内
            canvas_rect = self.get_a4_canvas_rect()
            if canvas_rect.contains(event.pos()):
                self.setCursor(Qt.OpenHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)
    
    def get_scale_factor(self):
        """获取当前缩放因子"""
        return self.scale_factor
    
    def set_scale_factor(self, scale):
        """设置缩放因子"""
        scale = max(self.min_scale, min(self.max_scale, scale))
        if scale != self.scale_factor:
            self.scale_factor = scale
            self.update()  # 触发重绘
            self.scale_changed.emit(self.scale_factor)

    def fit_to_size(self, target_size):
        """适应指定尺寸"""
        # 计算A4画布适应目标尺寸的缩放比例，留出一些边距
        margin = 50  # 边距像素
        available_width = target_size.width() - margin * 2
        available_height = target_size.height() - margin * 2

        scale_x = available_width / self.base_width
        scale_y = available_height / self.base_height
        scale = min(scale_x, scale_y)
        self.set_scale_factor(scale)

        # 重置画布位置到中心
        self.canvas_offset = QPoint(0, 0)

    def reset_scale(self):
        """重置缩放"""
        self.set_scale_factor(1.0)
        # 重置画布位置到中心
        self.canvas_offset = QPoint(0, 0)


class InteractiveScrollArea(QScrollArea):
    """交互式滚动区域"""

    def __init__(self):
        super().__init__()

        # 创建预览标签
        self.preview_label = InteractivePreviewLabel()
        self.setWidget(self.preview_label)

        # 设置滚动区域属性 - 禁用自动调整大小，因为我们要固定大小
        self.setWidgetResizable(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 设置深灰色背景以突出A4画布
        self.setStyleSheet("""
            QScrollArea {
                background-color: #404040;
                border: 2px solid #666;
                border-radius: 6px;
            }
            QScrollArea > QWidget {
                background-color: #404040;
            }
            QScrollArea::viewport {
                background-color: #404040;
            }
        """)

        # 连接信号
        self.preview_label.scale_changed.connect(self.on_scale_changed)

        # 设置预览标签的大小为滚动区域的大小
        self.resizeEvent = self._on_resize

    def _on_resize(self, event):
        """滚动区域大小改变事件"""
        # 让预览标签填满整个滚动区域
        self.preview_label.resize(self.viewport().size())
        super().resizeEvent(event)

    def set_pixmap(self, pixmap):
        """设置预览图片"""
        self.preview_label.set_pixmap(pixmap)

    def fit_to_window(self):
        """适应窗口大小"""
        # 获取可视区域大小
        viewport_size = self.viewport().size()
        self.preview_label.fit_to_size(viewport_size)

    def reset_view(self):
        """重置视图"""
        self.preview_label.reset_scale()

    def get_scale_factor(self):
        """获取缩放比例"""
        return self.preview_label.get_scale_factor()

    def on_scale_changed(self, scale):
        """缩放改变事件"""
        # 可以在这里添加缩放改变的处理逻辑
        pass
