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
        self.user_has_manually_scaled = False  # 跟踪用户是否手动缩放过

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

    def calculate_grid_layout(self):
        """计算网格布局的行列数"""
        if self.page_count <= 1:
            return 1, 1

        # 计算最接近正方形的行列布局
        import math
        sqrt_count = math.sqrt(self.page_count)

        # 优先选择行数较少的布局
        rows = int(sqrt_count)
        cols = math.ceil(self.page_count / rows)

        # 如果行数太少，调整为更平衡的布局
        if rows == 1 and self.page_count > 3:
            rows = 2
            cols = math.ceil(self.page_count / rows)

        return rows, cols

    def calculate_page_size(self):
        """计算单个页面的显示尺寸"""
        # 使用更大的基础尺寸，让100%缩放时看起来更合理
        # 基于屏幕DPI（96）计算，让1:1缩放接近真实尺寸
        base_width = 300  # 增加基础宽度，让100%缩放更合理
        base_height = int(base_width * self.a4_ratio)  # 保持A4比例

        # 应用当前缩放比例
        width = int(base_width * self.current_scale)
        height = int(base_height * self.current_scale)

        return QSize(width, height)

    def calculate_total_size(self):
        """计算所有页面的总尺寸（网格布局）"""
        if self.page_count == 0:
            return QSize(0, 0)

        rows, cols = self.calculate_grid_layout()
        page_size = self.calculate_page_size()

        # 总宽度 = 列数 * 页面宽度 + (列数-1) * 间距 + 2 * 边距
        total_width = (cols * page_size.width() +
                      (cols - 1) * self.page_spacing +
                      2 * self.margin)

        # 总高度 = 行数 * 页面高度 + (行数-1) * 间距 + 2 * 边距
        total_height = (rows * page_size.height() +
                       (rows - 1) * self.page_spacing +
                       2 * self.margin)

        return QSize(total_width, total_height)

    def get_page_rect(self, page_index):
        """获取指定页面的矩形区域（网格布局）"""
        if page_index < 0 or page_index >= self.page_count:
            return QRect()

        rows, cols = self.calculate_grid_layout()
        page_size = self.calculate_page_size()

        # 计算页面在网格中的行列位置
        row = page_index // cols
        col = page_index % cols

        # 计算页面位置
        x = (self.margin +
             col * (page_size.width() + self.page_spacing) +
             self.canvas_offset.x())

        y = (self.margin +
             row * (page_size.height() + self.page_spacing) +
             self.canvas_offset.y())

        # 智能居中显示：只有当内容小于窗口时才居中，否则允许超出边界
        total_size = self.calculate_total_size()
        widget_width = self.width()
        widget_height = self.height()

        # 计算居中偏移（只在内容小于窗口时应用）
        if total_size.width() <= widget_width:
            # 内容宽度小于窗口，水平居中
            center_offset_x = (widget_width - total_size.width()) // 2
        else:
            # 内容宽度大于窗口，不居中（允许拖拽查看）
            center_offset_x = 0

        if total_size.height() <= widget_height:
            # 内容高度小于窗口，垂直居中
            center_offset_y = (widget_height - total_size.height()) // 2
        else:
            # 内容高度大于窗口，不居中（允许拖拽查看）
            center_offset_y = 0

        x += center_offset_x
        y += center_offset_y

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
        self.current_scale = max(0.1, min(10.0, scale))  # 增加最大缩放倍数到10倍
        self.update()
        self.scale_changed.emit(self.current_scale)

    def zoom_in(self):
        """放大"""
        self.user_has_manually_scaled = True  # 标记为手动缩放
        self.set_scale(self.current_scale * 1.2)

    def zoom_out(self):
        """缩小"""
        self.user_has_manually_scaled = True  # 标记为手动缩放
        self.set_scale(self.current_scale / 1.2)

    def fit_to_window(self, force=False):
        """适应窗口大小（网格布局）"""
        # 如果用户已经手动缩放过，且不是强制适应，则跳过
        if self.user_has_manually_scaled and not force:
            return

        if self.page_count == 0:
            self.set_scale(1.0)
            return

        # 计算可用空间
        available_width = self.width() - 2 * self.margin
        available_height = self.height() - 2 * self.margin

        # 确保有足够的空间
        if available_width <= 0 or available_height <= 0:
            self.set_scale(0.1)
            return

        # 固定的基础A4尺寸（不应用缩放时）
        base_width = 300  # 基础宽度（与calculate_page_size保持一致）
        base_height = int(base_width * self.a4_ratio)  # 基础高度，保持A4比例

        # 单张图片时，尽量铺满预览窗口
        if self.page_count == 1:
            # 计算能够铺满窗口的缩放比例
            scale_by_width = available_width / base_width
            scale_by_height = available_height / base_height

            # 选择较小的缩放比例，确保页面完全可见
            optimal_scale = min(scale_by_width, scale_by_height)

            # 留出少量边距，让单张图片尽量大
            optimal_scale *= 0.95  # 只留出5%的边距

            # 限制缩放范围
            optimal_scale = max(optimal_scale, 0.1)   # 最小缩放比例
            optimal_scale = min(optimal_scale, 10.0)  # 最大缩放比例
        else:
            # 多张图片时，计算网格布局
            rows, cols = self.calculate_grid_layout()

            # 计算单页面可用尺寸（减去间距）
            single_page_width = (available_width - (cols - 1) * self.page_spacing) / cols
            single_page_height = (available_height - (rows - 1) * self.page_spacing) / rows

            # 根据可用空间计算需要的缩放比例
            scale_by_width = single_page_width / base_width
            scale_by_height = single_page_height / base_height

            # 选择较小的缩放比例，确保页面完全可见
            optimal_scale = min(scale_by_width, scale_by_height)

            # 留出一些边距，避免页面贴边
            optimal_scale *= 0.85  # 留出15%的边距

            # 限制缩放范围
            optimal_scale = max(optimal_scale, 0.05)  # 最小缩放比例
            optimal_scale = min(optimal_scale, 5.0)   # 最大缩放比例（多页面时适当限制）

        self.set_scale(optimal_scale)

        # 重置画布偏移，确保居中显示
        self.canvas_offset = QPoint(0, 0)

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
        # 首次显示时自动适应窗口（只在用户未手动缩放时）
        if self.page_count > 0:
            self.fit_to_window()  # 这里会检查user_has_manually_scaled标志
