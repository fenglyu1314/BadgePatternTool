"""
多页面A4预览组件
在同一个预览窗口中显示多个A4画布，保持正确的A4比例
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPoint, Signal, QRect, QSize
from PySide6.QtGui import QPainter, QPixmap, QPen, QColor


class MultiPagePreviewWidget(QWidget):
    """多页面A4预览组件 - 在同一个画布上绘制多个A4页面"""

    # 信号
    scale_changed = Signal(float)  # 缩放变化信号

    def __init__(self):
        super().__init__()

        # A4基础尺寸（保持正确的A4比例）
        self.a4_base_width = 210   # A4宽度（毫米）
        self.a4_base_height = 297  # A4高度（毫米）
        self.a4_ratio = self.a4_base_height / self.a4_base_width  # A4比例 ≈ 1.414

        # 页面数据
        self.page_pixmaps = []  # 页面内容列表
        self.page_count = 0

        # 显示参数
        self.current_scale = 1.0  # 当前缩放比例
        self.canvas_offset = QPoint(0, 0)  # 画布偏移
        self.page_spacing = 15  # 页面间距（像素）
        self.margin = 15  # 边距（像素）

        # 交互状态
        self.is_dragging = False
        self.last_mouse_pos = QPoint()

        # 设置组件属性
        self.setStyleSheet("background-color: #404040;")
        self.setMouseTracking(True)

        # 不设置固定的最小尺寸，让布局自动调整

    def set_page_pixmaps(self, pixmaps):
        """设置所有页面的内容"""
        self.page_pixmaps = pixmaps if pixmaps else []
        self.page_count = len(self.page_pixmaps)

        # 重置偏移，确保页面居中显示
        self.canvas_offset = QPoint(0, 0)

        self.update()

    def set_page_count(self, count):
        """设置页面数量（用于兼容性）"""
        if count != self.page_count:
            # 调整pixmap列表大小
            if count > len(self.page_pixmaps):
                # 添加空的pixmap
                self.page_pixmaps.extend([None] * (count - len(self.page_pixmaps)))
            else:
                # 截断列表
                self.page_pixmaps = self.page_pixmaps[:count]

            self.page_count = count
            self.update()

    def set_page_pixmap(self, page_index, pixmap):
        """设置指定页面的内容"""
        if 0 <= page_index < len(self.page_pixmaps):
            self.page_pixmaps[page_index] = pixmap
            self.update()

    def get_page_count(self):
        """获取页面数量"""
        return self.page_count

    def calculate_page_size(self):
        """计算单个页面的显示尺寸"""
        # 根据可用空间动态计算基础尺寸
        if self.page_count == 0:
            base_width = 150
        else:
            # 计算可用宽度
            available_width = self.width() - 2 * self.margin
            if self.page_count > 1:
                available_width -= (self.page_count - 1) * self.page_spacing

            # 单页面可用宽度
            single_page_width = available_width / max(1, self.page_count)

            # 基础宽度（不应用缩放时的尺寸）
            base_width = max(100, min(300, single_page_width))  # 限制在合理范围内

        base_height = int(base_width * self.a4_ratio)  # 保持A4比例

        # 应用缩放
        width = int(base_width * self.current_scale)
        height = int(base_height * self.current_scale)

        return QSize(width, height)

    def calculate_total_size(self):
        """计算所有页面的总尺寸"""
        if self.page_count == 0:
            return QSize(0, 0)

        page_size = self.calculate_page_size()

        # 总宽度 = 页面数 * 页面宽度 + (页面数-1) * 间距 + 2 * 边距
        total_width = (self.page_count * page_size.width() +
                      (self.page_count - 1) * self.page_spacing +
                      2 * self.margin)

        # 总高度 = 页面高度 + 2 * 边距
        total_height = page_size.height() + 2 * self.margin

        return QSize(total_width, total_height)

    def get_page_rect(self, page_index):
        """获取指定页面的矩形区域"""
        if page_index < 0 or page_index >= self.page_count:
            return QRect()

        page_size = self.calculate_page_size()

        # 计算页面位置
        x = (self.margin +
             page_index * (page_size.width() + self.page_spacing) +
             self.canvas_offset.x())

        y = self.margin + self.canvas_offset.y()

        # 居中显示
        widget_center_x = self.width() // 2
        widget_center_y = self.height() // 2

        total_size = self.calculate_total_size()
        content_center_x = total_size.width() // 2
        content_center_y = total_size.height() // 2

        x += widget_center_x - content_center_x
        y += widget_center_y - content_center_y

        return QRect(x, y, page_size.width(), page_size.height())

    def paintEvent(self, event):
        """绘制所有页面"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制背景
        painter.fillRect(self.rect(), QColor(64, 64, 64))

        # 绘制每个页面
        for i in range(self.page_count):
            self.draw_page(painter, i)

    def draw_page(self, painter, page_index):
        """绘制单个页面"""
        page_rect = self.get_page_rect(page_index)

        # 绘制阴影
        shadow_offset = 3
        shadow_rect = QRect(
            page_rect.x() + shadow_offset,
            page_rect.y() + shadow_offset,
            page_rect.width(),
            page_rect.height()
        )
        painter.fillRect(shadow_rect, QColor(0, 0, 0, 80))

        # 绘制A4纸张背景
        painter.fillRect(page_rect, QColor(255, 255, 255))

        # 绘制A4纸张边框
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRect(page_rect)

        # 绘制页面内容
        if (page_index < len(self.page_pixmaps) and
            self.page_pixmaps[page_index] and
            not self.page_pixmaps[page_index].isNull()):

            pixmap = self.page_pixmaps[page_index]

            # 缩放内容以适应页面
            scaled_pixmap = pixmap.scaled(
                page_rect.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            # 居中绘制内容
            content_x = page_rect.x() + (page_rect.width() - scaled_pixmap.width()) // 2
            content_y = page_rect.y() + (page_rect.height() - scaled_pixmap.height()) // 2

            painter.drawPixmap(content_x, content_y, scaled_pixmap)

        # 绘制页码
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.drawText(
            page_rect.x() + 10,
            page_rect.y() + page_rect.height() - 10,
            f"第 {page_index + 1} 页"
        )

    def set_scale(self, scale):
        """设置缩放比例"""
        self.current_scale = max(0.1, min(3.0, scale))
        self.update()
        self.scale_changed.emit(self.current_scale)

    def zoom_in(self):
        """放大"""
        self.set_scale(self.current_scale * 1.2)

    def zoom_out(self):
        """缩小"""
        self.set_scale(self.current_scale / 1.2)

    def fit_to_window(self):
        """适应窗口大小"""
        if self.page_count == 0:
            self.set_scale(1.0)
            return

        # 计算合适的缩放比例
        available_width = self.width() - 2 * self.margin
        available_height = self.height() - 2 * self.margin

        # 确保有足够的空间
        if available_width <= 0 or available_height <= 0:
            self.set_scale(0.5)
            return

        # 考虑多页面水平排列
        if self.page_count > 0:
            # 计算单页面可用宽度
            single_page_width = (available_width - (self.page_count - 1) * self.page_spacing) / self.page_count

            # 基础页面尺寸（理想的A4比例）
            ideal_base_width = 150  # 理想基础宽度
            ideal_base_height = int(ideal_base_width * self.a4_ratio)

            # 根据宽度和高度计算缩放比例
            scale_by_width = single_page_width / ideal_base_width
            scale_by_height = available_height / ideal_base_height

            # 选择较小的缩放比例，确保页面完全可见，但不超过1.5倍
            optimal_scale = min(scale_by_width, scale_by_height, 1.5)
            optimal_scale = max(optimal_scale, 0.2)  # 最小缩放比例

            self.set_scale(optimal_scale)

    def wheelEvent(self, event):
        """鼠标滚轮事件 - 直接缩放"""
        # 直接使用滚轮进行缩放，更方便用户操作
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
        event.accept()

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.last_mouse_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.is_dragging:
            # 计算偏移量
            delta = event.pos() - self.last_mouse_pos

            # 更新画布偏移
            self.canvas_offset += delta
            self.update()

            self.last_mouse_pos = event.pos()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def resizeEvent(self, event):
        """窗口大小变化事件"""
        super().resizeEvent(event)
        # 窗口大小变化时，重新计算页面尺寸
        if self.page_count > 0:
            self.update()

    def showEvent(self, event):
        """组件显示事件"""
        super().showEvent(event)
        # 首次显示时自动适应窗口
        if self.page_count > 0:
            self.fit_to_window()
