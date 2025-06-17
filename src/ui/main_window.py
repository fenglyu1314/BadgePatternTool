"""
主窗口界面模块 - PySide6版本
实现BadgePatternTool的主界面布局
"""

import sys
import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QListWidget, QTabWidget, QFrame,
    QSlider, QRadioButton, QComboBox, QButtonGroup, QSpinBox,
    QScrollArea, QMessageBox, QFileDialog, QStatusBar,
    QMenuBar, QMenu, QSplitter, QGroupBox, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPixmap, QPainter, QAction

# 添加父目录到路径以便导入utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import *
from utils.file_handler import FileHandler, ImageItem
from core.image_processor import ImageProcessor, CircleEditor
from core.layout_engine import LayoutEngine
from core.export_manager import ExportManager

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化业务逻辑组件
        self.file_handler = FileHandler()
        self.image_processor = ImageProcessor()
        self.layout_engine = LayoutEngine()
        self.export_manager = ExportManager()
        self.image_items = []  # 存储ImageItem对象列表
        self.current_selection = None  # 当前选中的图片项
        self.current_editor = None  # 当前的圆形编辑器

        # 初始化界面变量
        self.layout_mode = "grid"
        self.spacing_value = DEFAULT_SPACING
        self.margin_value = DEFAULT_MARGIN
        self.export_format = "pdf"
        self.scale_value = 1.0
        self.offset_x_value = 0
        self.offset_y_value = 0
        self.preview_scale_value = 0.5  # 预览缩放比例

        self.setup_window()
        self.create_menu()
        self.create_layout()
        self.create_status_bar()
        
    def setup_window(self):
        """设置窗口基本属性"""
        self.setWindowTitle(f"{APP_TITLE} v{APP_VERSION}")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # 设置窗口居中
        screen = self.screen().availableGeometry()
        x = (screen.width() - WINDOW_WIDTH) // 2
        y = (screen.height() - WINDOW_HEIGHT) // 2
        self.move(x, y)
        
        # 设置最小窗口大小
        self.setMinimumSize(800, 600)
        
    def create_menu(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        import_action = QAction("导入图片...", self)
        import_action.triggered.connect(self.import_images)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        export_pdf_action = QAction("导出PDF...", self)
        export_pdf_action.triggered.connect(self.export_pdf)
        file_menu.addAction(export_pdf_action)
        
        export_png_action = QAction("导出PNG...", self)
        export_png_action.triggered.connect(self.export_png)
        file_menu.addAction(export_png_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑")
        
        select_all_action = QAction("全选", self)
        select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(select_all_action)
        
        clear_all_action = QAction("清空列表", self)
        clear_all_action.triggered.connect(self.clear_all)
        edit_menu.addAction(clear_all_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图")
        
        refresh_action = QAction("刷新预览", self)
        refresh_action.triggered.connect(self.refresh_preview)
        view_menu.addAction(refresh_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_layout(self):
        """创建主界面布局"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 创建三个主要区域
        self.create_image_list_panel(splitter)
        self.create_edit_preview_panel(splitter)
        self.create_settings_panel(splitter)
        
        # 设置分割器比例
        splitter.setSizes([250, 600, 200])
        
    def create_image_list_panel(self, parent):
        """创建图片列表面板（左侧）"""
        # 图片列表框架
        list_frame = QGroupBox("图片列表")
        list_frame.setFixedWidth(280)  # 增加宽度以容纳数量控制
        parent.addWidget(list_frame)

        layout = QVBoxLayout(list_frame)

        # 导入按钮
        import_btn = QPushButton("导入图片")
        import_btn.clicked.connect(self.import_images)
        layout.addWidget(import_btn)

        # 图片列表
        self.image_listbox = QListWidget()
        self.image_listbox.itemSelectionChanged.connect(self.on_image_select)
        layout.addWidget(self.image_listbox)

        # 数量控制区域
        quantity_group = QGroupBox("数量设置")
        layout.addWidget(quantity_group)

        quantity_layout = QVBoxLayout(quantity_group)

        # 数量标签和输入框
        quantity_input_layout = QHBoxLayout()

        quantity_input_layout.addWidget(QLabel("数量:"))

        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setRange(1, 50)  # 最多50个
        self.quantity_spinbox.setValue(1)
        self.quantity_spinbox.valueChanged.connect(self.on_quantity_change)
        quantity_input_layout.addWidget(self.quantity_spinbox)

        quantity_layout.addLayout(quantity_input_layout)

        # 快速设置按钮
        quick_btn_layout = QHBoxLayout()

        btn_1 = QPushButton("1")
        btn_1.clicked.connect(lambda: self.set_quantity(1))
        quick_btn_layout.addWidget(btn_1)

        btn_5 = QPushButton("5")
        btn_5.clicked.connect(lambda: self.set_quantity(5))
        quick_btn_layout.addWidget(btn_5)

        btn_10 = QPushButton("10")
        btn_10.clicked.connect(lambda: self.set_quantity(10))
        quick_btn_layout.addWidget(btn_10)

        quantity_layout.addLayout(quick_btn_layout)

        # 操作按钮
        btn_layout = QHBoxLayout()

        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(self.delete_selected)
        btn_layout.addWidget(delete_btn)

        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self.clear_all)
        btn_layout.addWidget(clear_btn)

        layout.addLayout(btn_layout)
        
    def create_edit_preview_panel(self, parent):
        """创建编辑预览面板（中间）"""
        # 编辑预览框架
        preview_frame = QGroupBox("编辑预览区")
        parent.addWidget(preview_frame)
        
        layout = QVBoxLayout(preview_frame)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 单图编辑标签页
        self.edit_tab = QWidget()
        self.tab_widget.addTab(self.edit_tab, "单图编辑")
        self.create_edit_area()
        
        # A4排版预览标签页
        self.layout_tab = QWidget()
        self.tab_widget.addTab(self.layout_tab, "A4排版预览")
        self.create_layout_area()
        
    def create_settings_panel(self, parent):
        """创建参数设置面板（右侧）"""
        # 设置面板框架
        settings_frame = QGroupBox("参数设置")
        settings_frame.setFixedWidth(200)
        parent.addWidget(settings_frame)
        
        layout = QVBoxLayout(settings_frame)
        
        # 布局设置组
        layout_group = QGroupBox("布局设置")
        layout.addWidget(layout_group)
        
        layout_layout = QVBoxLayout(layout_group)
        
        # 布局模式选择
        layout_layout.addWidget(QLabel("排列模式:"))
        
        self.layout_button_group = QButtonGroup()
        
        grid_radio = QRadioButton("网格排列")
        grid_radio.setChecked(True)
        grid_radio.toggled.connect(lambda: self.set_layout_mode("grid"))
        self.layout_button_group.addButton(grid_radio)
        layout_layout.addWidget(grid_radio)
        
        compact_radio = QRadioButton("紧密排列")
        compact_radio.toggled.connect(lambda: self.set_layout_mode("compact"))
        self.layout_button_group.addButton(compact_radio)
        layout_layout.addWidget(compact_radio)
        
        # 间距设置
        layout_layout.addWidget(QLabel("间距(mm):"))
        self.spacing_slider = QSlider(Qt.Horizontal)
        self.spacing_slider.setRange(0, 20)
        self.spacing_slider.setValue(int(DEFAULT_SPACING))
        self.spacing_slider.valueChanged.connect(self.on_spacing_change)
        layout_layout.addWidget(self.spacing_slider)
        
        # 导出设置组
        export_group = QGroupBox("导出设置")
        layout.addWidget(export_group)
        
        export_layout = QVBoxLayout(export_group)
        
        # 导出格式
        export_layout.addWidget(QLabel("输出格式:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["pdf", "png", "jpg"])
        export_layout.addWidget(self.format_combo)
        
        # 自动排版按钮
        auto_layout_btn = QPushButton("自动排版")
        auto_layout_btn.clicked.connect(self.auto_layout)
        export_layout.addWidget(auto_layout_btn)

        # 导出按钮
        export_btn = QPushButton("导出文件")
        export_btn.clicked.connect(self.export_file)
        export_layout.addWidget(export_btn)

        # 添加弹性空间
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
    def create_edit_area(self):
        """创建编辑区域"""
        layout = QHBoxLayout(self.edit_tab)

        # 预览区域
        preview_frame = QGroupBox("圆形预览")
        preview_frame.setFixedWidth(280)
        layout.addWidget(preview_frame)

        preview_layout = QVBoxLayout(preview_frame)

        # 预览标签
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(250, 250)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 2px solid #ccc; background-color: white;")
        preview_layout.addWidget(self.preview_label)

        # 控制面板
        control_frame = QGroupBox("编辑控制")
        layout.addWidget(control_frame)

        control_layout = QVBoxLayout(control_frame)

        # 缩放控制
        scale_group = QGroupBox("缩放")
        control_layout.addWidget(scale_group)

        scale_layout = QVBoxLayout(scale_group)

        self.scale_label = QLabel("缩放: 1.0")
        scale_layout.addWidget(self.scale_label)

        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(10, 300)  # 0.1 到 3.0
        self.scale_slider.setValue(100)  # 1.0
        self.scale_slider.valueChanged.connect(self.on_scale_change)
        scale_layout.addWidget(self.scale_slider)

        # 位置控制
        position_group = QGroupBox("位置调整")
        control_layout.addWidget(position_group)

        position_layout = QVBoxLayout(position_group)

        # X轴偏移
        self.offset_x_label = QLabel("X偏移: 0")
        position_layout.addWidget(self.offset_x_label)

        self.offset_x_slider = QSlider(Qt.Horizontal)
        self.offset_x_slider.setRange(-100, 100)
        self.offset_x_slider.setValue(0)
        self.offset_x_slider.valueChanged.connect(self.on_position_change)
        position_layout.addWidget(self.offset_x_slider)

        # Y轴偏移
        self.offset_y_label = QLabel("Y偏移: 0")
        position_layout.addWidget(self.offset_y_label)

        self.offset_y_slider = QSlider(Qt.Horizontal)
        self.offset_y_slider.setRange(-100, 100)
        self.offset_y_slider.setValue(0)
        self.offset_y_slider.valueChanged.connect(self.on_position_change)
        position_layout.addWidget(self.offset_y_slider)

        # 操作按钮
        btn_layout = QHBoxLayout()

        reset_btn = QPushButton("重置")
        reset_btn.clicked.connect(self.reset_edit)
        btn_layout.addWidget(reset_btn)

        apply_btn = QPushButton("应用")
        apply_btn.clicked.connect(self.apply_edit)
        btn_layout.addWidget(apply_btn)

        control_layout.addLayout(btn_layout)

        # 添加弹性空间
        control_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # 初始显示提示
        self.show_edit_hint()
        
    def create_layout_area(self):
        """创建A4排版预览区域"""
        layout = QHBoxLayout(self.layout_tab)

        # 预览区域
        preview_frame = QGroupBox("A4排版预览")
        layout.addWidget(preview_frame)

        preview_layout = QVBoxLayout(preview_frame)

        # 信息栏
        info_layout = QHBoxLayout()

        title_label = QLabel("A4排版预览")
        title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        info_layout.addWidget(title_label)

        info_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # 布局信息标签
        self.layout_info_label = QLabel("")
        self.layout_info_label.setStyleSheet("color: #666; font-size: 10px;")
        info_layout.addWidget(self.layout_info_label)

        preview_layout.addLayout(info_layout)

        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        preview_layout.addWidget(scroll_area)

        # 预览标签
        self.layout_preview_label = QLabel()
        self.layout_preview_label.setAlignment(Qt.AlignCenter)
        self.layout_preview_label.setStyleSheet("border: 1px solid #ccc; background-color: white;")
        scroll_area.setWidget(self.layout_preview_label)

        # 控制面板
        control_frame = QGroupBox("排版控制")
        control_frame.setFixedWidth(200)
        layout.addWidget(control_frame)

        control_layout = QVBoxLayout(control_frame)

        # 布局模式
        layout_mode_group = QGroupBox("排列模式")
        control_layout.addWidget(layout_mode_group)

        layout_mode_layout = QVBoxLayout(layout_mode_group)

        self.layout_mode_group = QButtonGroup()

        grid_radio2 = QRadioButton("网格排列")
        grid_radio2.setChecked(True)
        grid_radio2.toggled.connect(lambda: self.set_layout_mode("grid") if grid_radio2.isChecked() else None)
        self.layout_mode_group.addButton(grid_radio2)
        layout_mode_layout.addWidget(grid_radio2)

        compact_radio2 = QRadioButton("紧密排列")
        compact_radio2.toggled.connect(lambda: self.set_layout_mode("compact") if compact_radio2.isChecked() else None)
        self.layout_mode_group.addButton(compact_radio2)
        layout_mode_layout.addWidget(compact_radio2)

        # 间距控制
        spacing_group = QGroupBox("间距设置")
        control_layout.addWidget(spacing_group)

        spacing_layout = QVBoxLayout(spacing_group)

        self.spacing_label2 = QLabel(f"间距: {self.spacing_value}mm")
        spacing_layout.addWidget(self.spacing_label2)

        self.spacing_slider2 = QSlider(Qt.Horizontal)
        self.spacing_slider2.setRange(0, 20)
        self.spacing_slider2.setValue(int(self.spacing_value))
        self.spacing_slider2.valueChanged.connect(self.on_spacing_change2)
        spacing_layout.addWidget(self.spacing_slider2)

        # 页边距控制
        margin_group = QGroupBox("页边距")
        control_layout.addWidget(margin_group)

        margin_layout = QVBoxLayout(margin_group)

        self.margin_label = QLabel(f"边距: {self.margin_value}mm")
        margin_layout.addWidget(self.margin_label)

        self.margin_slider = QSlider(Qt.Horizontal)
        self.margin_slider.setRange(5, 30)
        self.margin_slider.setValue(int(self.margin_value))
        self.margin_slider.valueChanged.connect(self.on_margin_change)
        margin_layout.addWidget(self.margin_slider)

        # 预览缩放控制
        preview_group = QGroupBox("预览缩放")
        control_layout.addWidget(preview_group)

        preview_layout_inner = QVBoxLayout(preview_group)

        self.preview_scale_label = QLabel(f"缩放: {int(self.preview_scale_value * 100)}%")
        preview_layout_inner.addWidget(self.preview_scale_label)

        self.preview_scale_slider = QSlider(Qt.Horizontal)
        self.preview_scale_slider.setRange(20, 100)  # 20% 到 100%
        self.preview_scale_slider.setValue(int(self.preview_scale_value * 100))
        self.preview_scale_slider.valueChanged.connect(self.on_preview_scale_change)
        preview_layout_inner.addWidget(self.preview_scale_slider)

        # 操作按钮
        btn_layout = QVBoxLayout()

        refresh_btn = QPushButton("刷新预览")
        refresh_btn.clicked.connect(self.update_layout_preview)
        btn_layout.addWidget(refresh_btn)

        auto_layout_btn2 = QPushButton("自动排版")
        auto_layout_btn2.clicked.connect(self.auto_layout)
        btn_layout.addWidget(auto_layout_btn2)

        control_layout.addLayout(btn_layout)

        # 添加弹性空间
        control_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # 初始显示提示
        self.show_layout_hint()
        
    # 事件处理方法
    def import_images(self):
        """导入图片"""
        try:
            # 选择图片文件
            file_paths = self.file_handler.select_images(self)

            if not file_paths:
                return

            # 检查图片数量限制
            total_count = len(self.image_items) + len(file_paths)
            if total_count > MAX_IMAGE_COUNT:
                QMessageBox.warning(
                    self,
                    "数量限制",
                    f"最多只能导入{MAX_IMAGE_COUNT}张图片，当前已有{len(self.image_items)}张"
                )
                return

            # 添加图片到列表
            added_count = 0
            for file_path in file_paths:
                try:
                    # 检查是否已存在
                    if any(item.file_path == file_path for item in self.image_items):
                        continue

                    # 创建图片项
                    image_item = ImageItem(file_path)
                    self.image_items.append(image_item)

                    # 添加到界面列表
                    display_text = f"{image_item.get_display_name()} ({image_item.get_size_text()}) [×{image_item.quantity}]"
                    self.image_listbox.addItem(display_text)

                    added_count += 1

                except Exception as e:
                    print(f"添加图片失败 {file_path}: {e}")
                    continue

            # 更新状态
            if added_count > 0:
                self.status_bar.showMessage(f"成功导入 {added_count} 张图片，总计 {len(self.image_items)} 张")
                # 选中最后一个添加的项
                if self.image_items:
                    last_index = len(self.image_items) - 1
                    self.image_listbox.setCurrentRow(last_index)

                # 更新A4排版预览
                self.update_layout_preview()
            else:
                self.status_bar.showMessage("没有新图片被添加")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入图片时发生错误：{str(e)}")
            self.status_bar.showMessage("图片导入失败")
        
    def export_pdf(self):
        """导出PDF"""
        self.export_file_with_format('pdf')

    def export_png(self):
        """导出PNG"""
        self.export_file_with_format('png')

    def export_file(self):
        """导出文件"""
        format_type = self.format_combo.currentText()
        self.export_file_with_format(format_type)

    def export_file_with_format(self, format_type):
        """
        导出文件（通用方法）
        参数: format_type - 文件格式 ('pdf', 'png', 'jpg')
        """
        try:
            # 获取展开后的图片列表
            expanded_images = self.get_expanded_image_list()

            # 验证导出设置
            is_valid, error_msg = self.export_manager.validate_export_settings(expanded_images, "temp")
            if not is_valid:
                QMessageBox.warning(self, "导出失败", error_msg)
                return

            # 获取当前设置
            layout_type = self.layout_mode
            spacing_mm = self.spacing_value
            margin_mm = self.margin_value

            # 选择保存路径
            suggested_filename = self.export_manager.get_suggested_filename(format_type.upper(), layout_type)

            if format_type.lower() == 'pdf':
                file_filter = "PDF文件 (*.pdf)"
                default_ext = ".pdf"
            elif format_type.lower() == 'png':
                file_filter = "PNG文件 (*.png)"
                default_ext = ".png"
            else:  # jpg
                file_filter = "JPEG文件 (*.jpg)"
                default_ext = ".jpg"

            from PySide6.QtWidgets import QFileDialog
            output_path, _ = QFileDialog.getSaveFileName(
                self,
                f"保存{format_type.upper()}文件",
                suggested_filename,
                file_filter
            )

            if not output_path:
                return  # 用户取消

            # 确保文件扩展名正确
            if not output_path.lower().endswith(default_ext):
                output_path += default_ext

            # 显示进度提示
            self.status_bar.showMessage(f"正在导出{format_type.upper()}文件...")

            # 执行导出
            if format_type.lower() == 'pdf':
                success, count = self.export_manager.export_to_pdf(
                    expanded_images, output_path, layout_type, spacing_mm, margin_mm
                )
            else:
                success, count = self.export_manager.export_to_image(
                    expanded_images, output_path, format_type.upper(),
                    layout_type, spacing_mm, margin_mm
                )

            if success:
                self.status_bar.showMessage(f"{format_type.upper()}导出成功")
                QMessageBox.information(
                    self,
                    "导出成功",
                    f"成功导出{count}张图片到{format_type.upper()}文件！\n\n"
                    f"文件路径：{output_path}\n"
                    f"布局模式：{'网格排列' if layout_type == 'grid' else '紧密排列'}\n"
                    f"图片数量：{count}张"
                )

                # 询问是否打开文件夹
                reply = QMessageBox.question(
                    self,
                    "打开文件夹",
                    "是否打开文件所在文件夹？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                if reply == QMessageBox.Yes:
                    import subprocess
                    import platform
                    if platform.system() == "Windows":
                        subprocess.run(['explorer', '/select,', output_path.replace('/', '\\')])
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.run(['open', '-R', output_path])
                    else:  # Linux
                        subprocess.run(['xdg-open', os.path.dirname(output_path)])

            else:
                self.status_bar.showMessage(f"{format_type.upper()}导出失败")
                QMessageBox.critical(self, "导出失败", f"导出{format_type.upper()}文件时发生错误")

        except Exception as e:
            self.status_bar.showMessage("导出失败")
            QMessageBox.critical(self, "错误", f"导出过程中发生错误：{str(e)}")
        
    def select_all(self):
        """全选"""
        QMessageBox.information(self, "提示", "全选功能开发中...")
        
    def clear_all(self):
        """清空列表"""
        if self.image_items:
            reply = QMessageBox.question(
                self,
                "确认",
                "确定要清空所有图片吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.image_items.clear()
                self.image_listbox.clear()
                self.current_selection = None
                self.current_editor = None
                self.status_bar.showMessage("已清空图片列表")
        
    def delete_selected(self):
        """删除选中项"""
        current_row = self.image_listbox.currentRow()
        if current_row >= 0 and current_row < len(self.image_items):
            # 删除数据
            deleted_item = self.image_items.pop(current_row)
            # 删除界面项
            self.image_listbox.takeItem(current_row)
            # 清除选择
            self.current_selection = None
            self.current_editor = None
            self.status_bar.showMessage(f"已删除: {deleted_item.get_display_name()}")

            # 如果还有项目，选中相邻的项
            if self.image_items:
                new_index = min(current_row, len(self.image_items) - 1)
                self.image_listbox.setCurrentRow(new_index)

            # 更新预览
            self.update_layout_preview()
        
    def refresh_preview(self):
        """刷新预览"""
        QMessageBox.information(self, "提示", "刷新预览功能开发中...")
        
    def on_image_select(self):
        """图片选择事件"""
        current_row = self.image_listbox.currentRow()
        if current_row >= 0 and current_row < len(self.image_items):
            self.current_selection = self.image_items[current_row]
            item_info = f"已选择: {self.current_selection.get_display_name()} " \
                       f"({self.current_selection.get_size_text()}, {self.current_selection.get_file_size_text()})"
            self.status_bar.showMessage(item_info)

            # 更新数量控制
            self.quantity_spinbox.setValue(self.current_selection.quantity)

            # 加载图片编辑器
            self.load_image_editor()
        else:
            self.current_selection = None
            self.current_editor = None
            self.quantity_spinbox.setValue(1)
            
    def set_layout_mode(self, mode):
        """设置布局模式"""
        self.layout_mode = mode
        self.status_bar.showMessage(f"布局模式: {'网格排列' if mode == 'grid' else '紧密排列'}")
        
    def on_spacing_change(self, value):
        """间距改变事件"""
        self.spacing_value = value
        self.status_bar.showMessage(f"间距设置: {value}mm")
        
    def load_image_editor(self):
        """加载图片编辑器"""
        if self.current_selection:
            try:
                # 创建圆形编辑器
                self.current_editor = CircleEditor(self.current_selection.file_path)

                # 更新控制滑块的值
                self.scale_slider.setValue(int(self.current_editor.scale * 100))
                self.offset_x_slider.setValue(self.current_editor.offset_x)
                self.offset_y_slider.setValue(self.current_editor.offset_y)

                # 更新标签
                self.scale_label.setText(f"缩放: {self.current_editor.scale:.1f}")
                self.offset_x_label.setText(f"X偏移: {self.current_editor.offset_x}")
                self.offset_y_label.setText(f"Y偏移: {self.current_editor.offset_y}")

                # 更新预览
                self.update_edit_preview()

            except Exception as e:
                print(f"加载编辑器失败: {e}")
                self.show_edit_hint()

    def show_edit_hint(self):
        """显示编辑提示"""
        self.preview_label.setText("选择左侧图片\n开始编辑")
        self.preview_label.setStyleSheet("border: 2px solid #ccc; background-color: #f5f5f5; color: #666;")

    def update_edit_preview(self):
        """更新编辑预览"""
        if self.current_editor:
            try:
                # 获取预览图片
                preview_pixmap = self.current_editor.get_preview(preview_size=240)

                # 显示预览图片
                self.preview_label.setPixmap(preview_pixmap)
                self.preview_label.setStyleSheet("border: 2px solid #ccc; background-color: white;")

            except Exception as e:
                print(f"更新预览失败: {e}")
                self.show_edit_hint()
        else:
            self.show_edit_hint()

    def on_scale_change(self, value):
        """缩放改变事件"""
        if self.current_editor:
            scale = value / 100.0  # 转换为0.1-3.0范围
            self.scale_value = scale
            self.scale_label.setText(f"缩放: {scale:.1f}")
            self.current_editor.set_scale(scale)
            self.update_edit_preview()

    def on_position_change(self):
        """位置改变事件"""
        if self.current_editor:
            offset_x = self.offset_x_slider.value()
            offset_y = self.offset_y_slider.value()

            self.offset_x_value = offset_x
            self.offset_y_value = offset_y

            self.offset_x_label.setText(f"X偏移: {offset_x}")
            self.offset_y_label.setText(f"Y偏移: {offset_y}")

            self.current_editor.set_offset(offset_x, offset_y)
            self.update_edit_preview()

    def reset_edit(self):
        """重置编辑参数"""
        if self.current_editor:
            self.current_editor.reset_to_optimal()

            # 更新控制滑块
            self.scale_slider.setValue(int(self.current_editor.scale * 100))
            self.offset_x_slider.setValue(self.current_editor.offset_x)
            self.offset_y_slider.setValue(self.current_editor.offset_y)

            # 更新预览
            self.update_edit_preview()

            self.status_bar.showMessage("已重置编辑参数")

    def apply_edit(self):
        """应用编辑"""
        if self.current_editor and self.current_selection:
            # 保存编辑参数到图片项
            self.current_selection.scale = self.current_editor.scale
            self.current_selection.offset_x = self.current_editor.offset_x
            self.current_selection.offset_y = self.current_editor.offset_y
            self.current_selection.rotation = self.current_editor.rotation
            self.current_selection.is_processed = True

            self.status_bar.showMessage("编辑参数已应用")

            # 更新A4排版预览
            self.update_layout_preview()

            QMessageBox.information(self, "提示", "编辑参数已保存，可在A4排版预览中查看效果")

    def show_layout_hint(self):
        """显示排版提示"""
        self.layout_preview_label.setText("导入图片后\n自动显示排版预览\n\n可使用滚动条\n查看完整A4页面")
        self.layout_preview_label.setStyleSheet("border: 1px solid #ccc; background-color: #f5f5f5; color: #666;")
        self.layout_info_label.setText("")

    def on_spacing_change2(self, value):
        """A4预览区间距改变事件"""
        self.spacing_value = value
        self.spacing_label2.setText(f"间距: {value}mm")
        # 同步主设置区的滑块
        self.spacing_slider.setValue(value)
        self.update_layout_preview()

    def on_margin_change(self, value):
        """页边距改变事件"""
        self.margin_value = value
        self.margin_label.setText(f"边距: {value}mm")
        self.update_layout_preview()

    def on_preview_scale_change(self, value):
        """预览缩放改变事件"""
        scale = value / 100.0
        self.preview_scale_value = scale
        self.preview_scale_label.setText(f"缩放: {value}%")
        self.update_layout_preview()

    def get_expanded_image_list(self):
        """获取展开后的图片列表（根据数量复制）"""
        expanded_list = []
        for image_item in self.image_items:
            for _ in range(image_item.quantity):
                expanded_list.append(image_item)
        return expanded_list

    def update_layout_preview(self):
        """更新A4排版预览"""
        if not self.image_items:
            self.show_layout_hint()
            return

        try:
            # 获取当前设置
            layout_type = self.layout_mode
            spacing_mm = self.spacing_value
            margin_mm = self.margin_value

            # 获取展开后的图片列表
            expanded_images = self.get_expanded_image_list()

            # 创建排版预览
            preview_pixmap = self.layout_engine.create_layout_preview(
                expanded_images, layout_type, spacing_mm, margin_mm,
                preview_scale=self.preview_scale_value
            )

            # 更新预览显示
            self.layout_preview_label.setPixmap(preview_pixmap)
            self.layout_preview_label.setStyleSheet("border: 1px solid #ccc; background-color: white;")

            # 调整标签大小以适应图片
            self.layout_preview_label.resize(preview_pixmap.size())

            # 更新布局信息
            layout_info = self.layout_engine.get_layout_info(layout_type, spacing_mm, margin_mm)
            total_images = len(expanded_images)
            unique_images = len(self.image_items)
            info_text = f"可放置: {layout_info['max_count']}个 | 总数: {total_images}个 | 种类: {unique_images}个"
            self.layout_info_label.setText(info_text)

            # 更新状态栏
            self.status_bar.showMessage(f"排版预览已更新 - {layout_info['type']}模式，共{total_images}个图片")

        except Exception as e:
            print(f"更新排版预览失败: {e}")
            self.show_layout_hint()

    def auto_layout(self):
        """自动排版（为所有图片应用最佳参数）"""
        if not self.image_items:
            QMessageBox.warning(self, "提示", "请先导入图片")
            return

        try:
            processed_count = 0
            for image_item in self.image_items:
                if not image_item.is_processed:
                    # 计算最佳缩放
                    optimal_scale = self.image_processor.get_optimal_scale(image_item.file_path)

                    # 应用最佳参数
                    image_item.scale = optimal_scale
                    image_item.offset_x = 0
                    image_item.offset_y = 0
                    image_item.rotation = 0
                    image_item.is_processed = True

                    processed_count += 1

            # 更新预览
            self.update_layout_preview()

            if processed_count > 0:
                self.status_bar.showMessage(f"自动排版完成，处理了 {processed_count} 张图片")
                QMessageBox.information(self, "完成", f"自动排版完成！\n处理了 {processed_count} 张图片")
            else:
                QMessageBox.information(self, "提示", "所有图片都已处理过")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"自动排版失败：{str(e)}")

    def on_quantity_change(self, value):
        """数量改变事件"""
        if self.current_selection:
            self.current_selection.quantity = value
            self.update_image_list_display()
            self.update_layout_preview()
            self.status_bar.showMessage(f"已设置数量: {value}")

    def set_quantity(self, quantity):
        """设置数量"""
        if self.current_selection:
            self.current_selection.quantity = quantity
            self.quantity_spinbox.setValue(quantity)
            self.update_image_list_display()
            self.update_layout_preview()
            self.status_bar.showMessage(f"已设置数量: {quantity}")
        else:
            QMessageBox.warning(self, "提示", "请先选择一张图片")

    def update_image_list_display(self):
        """更新图片列表显示"""
        current_row = self.image_listbox.currentRow()

        # 重新构建列表显示
        self.image_listbox.clear()
        for image_item in self.image_items:
            display_text = f"{image_item.get_display_name()} ({image_item.get_size_text()}) [×{image_item.quantity}]"
            self.image_listbox.addItem(display_text)

        # 恢复选择
        if current_row >= 0 and current_row < len(self.image_items):
            self.image_listbox.setCurrentRow(current_row)

    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于",
            f"{APP_TITLE} v{APP_VERSION}\n\n"
            "徽章图案制作工具\n"
            "支持图片裁剪和A4排版\n\n"
            "基于PySide6开发"
        )
