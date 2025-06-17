"""
主窗口界面模块 - PySide6版本
实现BadgePatternTool的主界面布局
"""

import sys
import os

# PySide6 GUI组件导入
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QListWidgetItem,
    QSlider, QRadioButton, QComboBox, QButtonGroup, QSpinBox,
    QMessageBox, QStatusBar, QSplitter, QGroupBox,
    QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QSize, QPoint
from PySide6.QtGui import QAction, QIcon

# 添加父目录到路径以便导入模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 项目模块导入
from utils.config import (
    APP_TITLE, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT,
    DEFAULT_SPACING, DEFAULT_MARGIN, DEFAULT_LAYOUT, DEFAULT_EXPORT_FORMAT,
    MAX_IMAGE_COUNT, app_config
)
from utils.file_handler import FileHandler, ImageItem
from core.image_processor import ImageProcessor, CircleEditor
from core.layout_engine import LayoutEngine
from core.export_manager import ExportManager
from ui.interactive_preview_label import InteractiveScrollArea
from ui.interactive_image_editor import InteractiveImageEditor

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
        self.layout_mode = DEFAULT_LAYOUT
        self.spacing_value = DEFAULT_SPACING
        self.margin_value = DEFAULT_MARGIN
        self.export_format = DEFAULT_EXPORT_FORMAT.lower()
        self.scale_value = 1.0
        self.offset_x_value = 0
        self.offset_y_value = 0
        self.preview_scale_value = 0.5  # 预览缩放比例

        # 初始化防抖定时器
        self.setup_debounce_timers()

        # 设置配置监听器
        app_config.add_listener(self.on_config_changed)

        self.setup_window()
        self.create_menu()
        self.create_layout()
        self.create_status_bar()

        # 初始化时显示灰色圆形预览
        self.update_layout_preview()

        # 延迟适应窗口（等待界面完全加载）
        QTimer.singleShot(100, self.fit_preview_to_window)

    def setup_debounce_timers(self):
        """设置防抖定时器"""
        # 编辑预览更新定时器（用于缩放和位置调整）
        self.edit_preview_timer = QTimer()
        self.edit_preview_timer.setSingleShot(True)
        self.edit_preview_timer.timeout.connect(self.delayed_update_edit_preview)

        # 布局预览更新定时器（用于A4排版预览）
        self.layout_preview_timer = QTimer()
        self.layout_preview_timer.setSingleShot(True)
        self.layout_preview_timer.timeout.connect(self.delayed_update_layout_preview)

        # 图片列表更新定时器（用于数量变化）
        self.list_update_timer = QTimer()
        self.list_update_timer.setSingleShot(True)
        self.list_update_timer.timeout.connect(self.delayed_update_image_list)

        # 防抖延迟时间（毫秒）
        self.debounce_delay = 150  # 150ms延迟，平衡响应性和性能
        self.layout_debounce_delay = 300  # 布局预览使用更长的延迟

    def setup_window(self):
        """设置窗口基本属性"""
        self.setWindowTitle(f"{APP_TITLE} v{APP_VERSION}")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)

        # 设置窗口居中
        screen = self.screen().availableGeometry()
        x = (screen.width() - WINDOW_WIDTH) // 2
        y = (screen.height() - WINDOW_HEIGHT) // 2
        self.move(x, y)

        # 设置固定窗口大小（不可调整）
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        # 设置窗口标志：禁用最大化按钮，保留最小化和关闭按钮
        flags = Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint | Qt.WindowTitleHint
        self.setWindowFlags(flags)
        
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

        # 打印功能
        print_action = QAction("打印...", self)
        print_action.setShortcut("Ctrl+P")
        print_action.triggered.connect(self.print_layout)
        file_menu.addAction(print_action)

        print_preview_action = QAction("打印预览...", self)
        print_preview_action.triggered.connect(self.print_preview)
        file_menu.addAction(print_preview_action)

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
        
        # 创建四个主要区域
        self.create_image_list_panel(splitter)      # 1. 图片列表
        self.create_single_edit_panel(splitter)     # 2. 单图编辑区域
        self.create_a4_preview_panel(splitter)      # 3. A4排版预览
        self.create_control_panel(splitter)         # 4. 排版控制和导出

        # 设置各列固定宽度
        # 禁用分割器的拖拽调整
        splitter.setChildrenCollapsible(False)

        # 设置固定宽度（总计1380px，窗口1420px，留40px边距）
        # 图片列表: 260px, 单图编辑: 340px, A4预览: 480px, 控制面板: 300px
        column_widths = [260, 340, 480, 300]
        splitter.setSizes(column_widths)

        # 设置各个面板的固定宽度
        for i in range(splitter.count()):
            splitter.widget(i).setMinimumWidth(column_widths[i])
            splitter.widget(i).setMaximumWidth(column_widths[i])
        
    def create_image_list_panel(self, parent):
        """创建图片列表面板（左侧）"""
        # 图片列表框架
        list_frame = QGroupBox("图片列表")
        # 宽度由splitter控制，不需要单独设置
        parent.addWidget(list_frame)

        layout = QVBoxLayout(list_frame)

        # 导入按钮
        import_btn = QPushButton("导入图片")
        import_btn.clicked.connect(self.import_images)
        layout.addWidget(import_btn)

        # 图片列表
        self.image_listbox = QListWidget()
        self.image_listbox.itemSelectionChanged.connect(self.on_image_select)

        # 设置列表显示模式和样式
        self.image_listbox.setViewMode(QListWidget.ListMode)  # 列表模式，显示图标和文字
        self.image_listbox.setIconSize(QSize(48, 48))  # 设置图标大小
        self.image_listbox.setSpacing(2)  # 设置项目间距
        self.image_listbox.setUniformItemSizes(True)  # 统一项目大小

        layout.addWidget(self.image_listbox)

        # 操作按钮
        btn_layout = QHBoxLayout()

        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(self.delete_selected)
        btn_layout.addWidget(delete_btn)

        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self.clear_all)
        btn_layout.addWidget(clear_btn)

        layout.addLayout(btn_layout)

    def create_single_edit_panel(self, parent):
        """创建单图编辑面板（中间）"""
        # 单图编辑框架
        edit_frame = QGroupBox("单图编辑区")
        parent.addWidget(edit_frame)

        layout = QVBoxLayout(edit_frame)

        # 交互式图片编辑器（直接添加，无额外框框）
        self.interactive_editor = InteractiveImageEditor()
        self.interactive_editor.setFixedSize(320, 320)  # 增加高度，给更多编辑空间
        layout.addWidget(self.interactive_editor)

        # 更新遮罩半径以匹配配置
        self.interactive_editor.update_mask_radius()

        # 连接编辑器信号
        self.interactive_editor.parameters_changed.connect(self.on_editor_parameters_changed)

        # 编辑控制区域（直接添加，无额外框框）
        self.create_edit_controls(layout)

    def create_a4_preview_panel(self, parent):
        """创建A4排版预览面板（第三列）"""
        # A4预览面板框架
        preview_frame = QGroupBox("A4排版预览")
        parent.addWidget(preview_frame)

        layout = QVBoxLayout(preview_frame)

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

        layout.addLayout(info_layout)

        # 交互式滚动区域
        self.interactive_scroll_area = InteractiveScrollArea()
        # 设置最小尺寸以保持A4比例
        # A4比例约为1:1.414，设置合适的最小尺寸
        min_width = 350  # 最小宽度
        min_height = int(min_width * 1.414)  # 按A4比例计算高度
        self.interactive_scroll_area.setMinimumSize(min_width, min_height)
        layout.addWidget(self.interactive_scroll_area)

        # 获取内部的预览标签引用（为了兼容现有代码）
        self.layout_preview_label = self.interactive_scroll_area.preview_label

        # 视图控制按钮
        view_control_layout = QHBoxLayout()

        fit_btn = QPushButton("适应窗口")
        fit_btn.clicked.connect(self.fit_preview_to_window)
        view_control_layout.addWidget(fit_btn)

        reset_view_btn = QPushButton("重置视图")
        reset_view_btn.clicked.connect(self.reset_preview_view)
        view_control_layout.addWidget(reset_view_btn)

        refresh_btn = QPushButton("刷新预览")
        refresh_btn.clicked.connect(self.update_layout_preview)
        view_control_layout.addWidget(refresh_btn)

        layout.addLayout(view_control_layout)

    def create_control_panel(self, parent):
        """创建排版控制和导出面板（第四列）"""
        # 控制面板框架
        control_frame = QGroupBox("排版控制")
        parent.addWidget(control_frame)

        layout = QVBoxLayout(control_frame)

        # 布局模式
        layout_mode_group = QGroupBox("排列模式")
        layout.addWidget(layout_mode_group)

        layout_mode_layout = QVBoxLayout(layout_mode_group)

        self.layout_button_group = QButtonGroup()

        grid_radio = QRadioButton("网格排列")
        grid_radio.setChecked(DEFAULT_LAYOUT == "grid")
        grid_radio.toggled.connect(lambda: self.set_layout_mode("grid"))
        self.layout_button_group.addButton(grid_radio)
        layout_mode_layout.addWidget(grid_radio)

        compact_radio = QRadioButton("紧密排列")
        compact_radio.setChecked(DEFAULT_LAYOUT == "compact")
        compact_radio.toggled.connect(lambda: self.set_layout_mode("compact"))
        self.layout_button_group.addButton(compact_radio)
        layout_mode_layout.addWidget(compact_radio)

        # 间距控制
        spacing_group = QGroupBox("间距设置")
        layout.addWidget(spacing_group)

        spacing_layout = QVBoxLayout(spacing_group)

        self.spacing_label = QLabel(f"间距: {self.spacing_value}mm")
        spacing_layout.addWidget(self.spacing_label)

        self.spacing_slider = QSlider(Qt.Horizontal)
        self.spacing_slider.setRange(0, 20)
        self.spacing_slider.setValue(int(self.spacing_value))
        self.spacing_slider.valueChanged.connect(self.on_spacing_change)
        spacing_layout.addWidget(self.spacing_slider)

        # 页边距控制
        margin_group = QGroupBox("页边距")
        layout.addWidget(margin_group)

        margin_layout = QVBoxLayout(margin_group)

        self.margin_label = QLabel(f"边距: {self.margin_value}mm")
        margin_layout.addWidget(self.margin_label)

        self.margin_slider = QSlider(Qt.Horizontal)
        self.margin_slider.setRange(0, 30)  # 允许0mm最小页边距
        self.margin_slider.setValue(int(self.margin_value))
        self.margin_slider.valueChanged.connect(self.on_margin_change)
        margin_layout.addWidget(self.margin_slider)

        # 圆形尺寸设置
        size_group = QGroupBox("圆形尺寸")
        layout.addWidget(size_group)

        size_layout = QVBoxLayout(size_group)

        # 直径设置
        diameter_layout = QHBoxLayout()
        diameter_layout.addWidget(QLabel("直径:"))

        self.diameter_spinbox = QSpinBox()
        self.diameter_spinbox.setRange(10, 100)  # 10-100mm
        self.diameter_spinbox.setValue(int(app_config.badge_diameter_mm))
        self.diameter_spinbox.setSuffix("mm")
        self.diameter_spinbox.valueChanged.connect(self.on_diameter_change)
        diameter_layout.addWidget(self.diameter_spinbox)

        size_layout.addLayout(diameter_layout)

        # 预设按钮
        preset_layout = QHBoxLayout()

        btn_25 = QPushButton("25mm")
        btn_25.clicked.connect(lambda: self.set_diameter(25))
        preset_layout.addWidget(btn_25)

        btn_32 = QPushButton("32mm")
        btn_32.clicked.connect(lambda: self.set_diameter(32))
        preset_layout.addWidget(btn_32)

        btn_58 = QPushButton("58mm")
        btn_58.clicked.connect(lambda: self.set_diameter(58))
        preset_layout.addWidget(btn_58)

        btn_68 = QPushButton("68mm")
        btn_68.clicked.connect(lambda: self.set_diameter(68))
        preset_layout.addWidget(btn_68)

        size_layout.addLayout(preset_layout)

        # 导出设置组
        export_group = QGroupBox("导出设置")
        layout.addWidget(export_group)

        export_layout = QVBoxLayout(export_group)

        # 导出格式
        export_layout.addWidget(QLabel("输出格式:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["pdf", "png", "jpg"])
        # 设置默认选择
        default_index = self.format_combo.findText(DEFAULT_EXPORT_FORMAT.lower())
        if default_index >= 0:
            self.format_combo.setCurrentIndex(default_index)
        export_layout.addWidget(self.format_combo)

        # 自动排版按钮
        auto_layout_btn = QPushButton("自动排版")
        auto_layout_btn.clicked.connect(self.auto_layout)
        export_layout.addWidget(auto_layout_btn)

        # 导出按钮
        export_btn = QPushButton("导出文件")
        export_btn.clicked.connect(self.export_file)
        export_layout.addWidget(export_btn)

        # 打印按钮
        print_btn = QPushButton("打印")
        print_btn.clicked.connect(self.print_layout)
        print_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        export_layout.addWidget(print_btn)

        # 添加弹性空间
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def create_edit_controls(self, parent_layout):
        """创建编辑控制区域"""
        # 缩放控制（直接添加，无框框）
        self.scale_label = QLabel("图片缩放: 1.0")
        self.scale_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        parent_layout.addWidget(self.scale_label)

        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(10, 300)  # 0.1 到 3.0
        self.scale_slider.setValue(100)  # 1.0
        self.scale_slider.valueChanged.connect(self.on_scale_change)
        parent_layout.addWidget(self.scale_slider)

        # X轴偏移（直接添加，无框框）
        self.offset_x_label = QLabel("X偏移: 0")
        self.offset_x_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        parent_layout.addWidget(self.offset_x_label)

        self.offset_x_slider = QSlider(Qt.Horizontal)
        self.offset_x_slider.setRange(-100, 100)
        self.offset_x_slider.setValue(0)
        self.offset_x_slider.valueChanged.connect(self.on_position_change)
        parent_layout.addWidget(self.offset_x_slider)

        # Y轴偏移（直接添加，无框框）
        self.offset_y_label = QLabel("Y偏移: 0")
        self.offset_y_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        parent_layout.addWidget(self.offset_y_label)

        self.offset_y_slider = QSlider(Qt.Horizontal)
        self.offset_y_slider.setRange(-100, 100)
        self.offset_y_slider.setValue(0)
        self.offset_y_slider.valueChanged.connect(self.on_position_change)
        parent_layout.addWidget(self.offset_y_slider)

        # 数量控制（直接添加，无框框）
        quantity_input_layout = QHBoxLayout()
        quantity_label = QLabel("数量:")
        quantity_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        quantity_input_layout.addWidget(quantity_label)

        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setRange(1, 50)  # 最多50个
        self.quantity_spinbox.setValue(1)
        self.quantity_spinbox.valueChanged.connect(self.on_quantity_change)
        quantity_input_layout.addWidget(self.quantity_spinbox)

        # 快速设置按钮
        btn_1 = QPushButton("1")
        btn_1.setMaximumWidth(30)
        btn_1.clicked.connect(lambda: self.set_quantity(1))
        quantity_input_layout.addWidget(btn_1)

        btn_5 = QPushButton("5")
        btn_5.setMaximumWidth(30)
        btn_5.clicked.connect(lambda: self.set_quantity(5))
        quantity_input_layout.addWidget(btn_5)

        btn_10 = QPushButton("10")
        btn_10.setMaximumWidth(30)
        btn_10.clicked.connect(lambda: self.set_quantity(10))
        quantity_input_layout.addWidget(btn_10)

        parent_layout.addLayout(quantity_input_layout)

        # 操作按钮（直接添加，无框框）
        btn_layout = QHBoxLayout()

        reset_btn = QPushButton("重置")
        reset_btn.clicked.connect(self.reset_edit)
        btn_layout.addWidget(reset_btn)

        apply_btn = QPushButton("应用")
        apply_btn.clicked.connect(self.apply_edit)
        btn_layout.addWidget(apply_btn)

        parent_layout.addLayout(btn_layout)

        # 初始显示提示
        self.show_edit_hint()

    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
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

                    # 添加到界面列表（带缩略图）
                    self.add_image_item_to_list(image_item)

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

                # 自动处理新导入的图片（应用最佳参数）
                self.auto_process_new_images()

                # 重新加载当前选中的编辑器（因为缩放值已更新）
                if self.current_selection:
                    self.load_image_editor()

                # 更新A4排版预览
                self.update_layout_preview()

                # 延迟适应窗口（确保预览图片已加载）
                QTimer.singleShot(200, self.fit_preview_to_window)
            else:
                self.status_bar.showMessage("没有新图片被添加")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入图片时发生错误：{str(e)}")
            self.status_bar.showMessage("图片导入失败")

    def auto_process_new_images(self):
        """自动处理新导入的图片（应用最佳参数）"""
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

            if processed_count > 0:
                print(f"自动处理了 {processed_count} 张新图片")

        except Exception as e:
            print(f"自动处理图片失败: {e}")

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

        # 更新布局预览
        self.layout_preview_timer.stop()
        self.layout_preview_timer.start(self.layout_debounce_delay)

    def load_image_editor(self):
        """加载图片编辑器"""
        if self.current_selection:
            try:
                # 加载图片到交互式编辑器
                success = self.interactive_editor.load_image(self.current_selection.file_path)

                if success:
                    # 创建圆形编辑器（用于兼容性）
                    self.current_editor = CircleEditor(self.current_selection.file_path)

                    # 如果图片项已有编辑参数，应用到编辑器
                    if hasattr(self.current_selection, 'scale'):
                        self.interactive_editor.set_parameters(
                            self.current_selection.scale,
                            self.current_selection.offset_x,
                            self.current_selection.offset_y
                        )
                        self.current_editor.scale = self.current_selection.scale
                        self.current_editor.offset_x = self.current_selection.offset_x
                        self.current_editor.offset_y = self.current_selection.offset_y

                    # 更新控制滑块的值
                    self.update_sliders_from_editor()
                else:
                    self.show_edit_hint()

            except Exception as e:
                print(f"加载编辑器失败: {e}")
                self.show_edit_hint()

    def show_edit_hint(self):
        """显示编辑提示"""
        # 清空交互式编辑器
        self.interactive_editor.original_image = None
        self.interactive_editor.update()

    def update_sliders_from_editor(self):
        """从编辑器更新滑块值"""
        if self.current_editor:
            # 更新控制滑块的值
            self.scale_slider.setValue(int(self.current_editor.scale * 100))
            self.offset_x_slider.setValue(self.current_editor.offset_x)
            self.offset_y_slider.setValue(self.current_editor.offset_y)

            # 更新标签
            self.scale_label.setText(f"图片缩放: {self.current_editor.scale:.1f}")
            self.offset_x_label.setText(f"X偏移: {self.current_editor.offset_x}")
            self.offset_y_label.setText(f"Y偏移: {self.current_editor.offset_y}")

    def on_editor_parameters_changed(self, scale, offset_x, offset_y):
        """交互式编辑器参数改变事件"""
        if self.current_editor:
            # 更新圆形编辑器参数
            self.current_editor.scale = scale
            self.current_editor.offset_x = offset_x
            self.current_editor.offset_y = offset_y

            # 更新滑块（不触发信号）
            self.scale_slider.blockSignals(True)
            self.offset_x_slider.blockSignals(True)
            self.offset_y_slider.blockSignals(True)

            self.scale_slider.setValue(int(scale * 100))
            self.offset_x_slider.setValue(offset_x)
            self.offset_y_slider.setValue(offset_y)

            self.scale_slider.blockSignals(False)
            self.offset_x_slider.blockSignals(False)
            self.offset_y_slider.blockSignals(False)

            # 更新标签
            self.scale_label.setText(f"图片缩放: {scale:.1f}")
            self.offset_x_label.setText(f"X偏移: {offset_x}")
            self.offset_y_label.setText(f"Y偏移: {offset_y}")

    def on_scale_change(self, value):
        """缩放改变事件（带防抖）"""
        if self.current_editor:
            scale = value / 100.0  # 转换为0.1-3.0范围
            self.scale_value = scale
            self.scale_label.setText(f"图片缩放: {scale:.1f}")
            self.current_editor.set_scale(scale)

            # 同步到交互式编辑器
            if hasattr(self, 'interactive_editor') and self.interactive_editor.original_image:
                self.interactive_editor.image_scale = scale
                self.interactive_editor.update()

            # 使用防抖定时器延迟更新预览
            self.edit_preview_timer.stop()
            self.edit_preview_timer.start(self.debounce_delay)

    def on_position_change(self):
        """位置改变事件（带防抖）"""
        if self.current_editor:
            offset_x = self.offset_x_slider.value()
            offset_y = self.offset_y_slider.value()

            self.offset_x_value = offset_x
            self.offset_y_value = offset_y

            self.offset_x_label.setText(f"X偏移: {offset_x}")
            self.offset_y_label.setText(f"Y偏移: {offset_y}")

            self.current_editor.set_offset(offset_x, offset_y)

            # 同步到交互式编辑器
            if hasattr(self, 'interactive_editor') and self.interactive_editor.original_image:
                self.interactive_editor.image_offset = QPoint(offset_x, offset_y)
                self.interactive_editor.update()

            # 使用防抖定时器延迟更新预览
            self.edit_preview_timer.stop()
            self.edit_preview_timer.start(self.debounce_delay)

    def reset_edit(self):
        """重置编辑参数"""
        if self.current_editor:
            self.current_editor.reset_to_optimal()

            # 更新控制滑块
            self.scale_slider.setValue(int(self.current_editor.scale * 100))
            self.offset_x_slider.setValue(self.current_editor.offset_x)
            self.offset_y_slider.setValue(self.current_editor.offset_y)

            # 同步到交互式编辑器
            if hasattr(self, 'interactive_editor'):
                self.interactive_editor.reset_view()

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
        self.layout_preview_label.setText("导入图片后\n自动显示排版预览\n\n支持鼠标滚轮缩放\n支持拖动平移")
        self.layout_preview_label.setStyleSheet("border: 1px solid #ccc; background-color: #f5f5f5; color: #666;")
        self.layout_info_label.setText("")

    def on_spacing_change(self, value):
        """间距改变事件（带防抖）"""
        self.spacing_value = value
        self.spacing_label.setText(f"间距: {value}mm")
        self.status_bar.showMessage(f"间距设置: {value}mm")

        # 使用防抖定时器延迟更新布局预览
        self.layout_preview_timer.stop()
        self.layout_preview_timer.start(self.debounce_delay)

    def on_margin_change(self, value):
        """页边距改变事件（带防抖）"""
        self.margin_value = value
        self.margin_label.setText(f"边距: {value}mm")

        # 使用防抖定时器延迟更新布局预览
        self.layout_preview_timer.stop()
        self.layout_preview_timer.start(self.debounce_delay)

    def on_preview_scale_change(self, value):
        """预览缩放改变事件（带防抖）"""
        scale = value / 100.0
        self.preview_scale_value = scale
        self.preview_scale_label.setText(f"预览缩放: {value}%")

        # 同步到InteractiveScrollArea的缩放
        if hasattr(self, 'interactive_scroll_area'):
            self.interactive_scroll_area.preview_label.set_scale_factor(scale)

        # 使用防抖定时器延迟更新布局预览
        self.layout_preview_timer.stop()
        self.layout_preview_timer.start(self.debounce_delay)

    def get_expanded_image_list(self):
        """获取展开后的图片列表（根据数量复制）"""
        expanded_list = []
        for image_item in self.image_items:
            for _ in range(image_item.quantity):
                expanded_list.append(image_item)
        return expanded_list

    def update_layout_preview(self):
        """更新A4排版预览"""
        try:
            # 获取当前设置
            layout_type = self.layout_mode
            spacing_mm = self.spacing_value
            margin_mm = self.margin_value

            # 获取展开后的图片列表
            expanded_images = self.get_expanded_image_list()

            # 创建排版预览（即使没有图片也显示灰色圆形占位符）
            preview_pixmap = self.layout_engine.create_layout_preview(
                expanded_images, layout_type, spacing_mm, margin_mm,
                preview_scale=self.preview_scale_value
            )

            # 更新预览显示（使用交互式组件）
            self.interactive_scroll_area.set_pixmap(preview_pixmap)

            # 更新布局信息
            layout_info = self.layout_engine.get_layout_info(layout_type, spacing_mm, margin_mm)
            total_images = len(expanded_images)
            unique_images = len(self.image_items)

            if not self.image_items:
                # 没有图片时显示布局容量信息
                info_text = f"可放置: {layout_info['max_count']}个 | 当前: 0个 | 导入图片开始使用"
                self.status_bar.showMessage(f"排版预览 - {layout_info['type']}模式，可放置{layout_info['max_count']}个圆形")
            else:
                # 有图片时显示详细信息
                info_text = f"可放置: {layout_info['max_count']}个 | 总数: {total_images}个 | 种类: {unique_images}个"
                self.status_bar.showMessage(f"排版预览已更新 - {layout_info['type']}模式，共{total_images}个图片")

            self.layout_info_label.setText(info_text)

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
        """数量改变事件（带防抖）"""
        if self.current_selection:
            self.current_selection.quantity = value
            self.status_bar.showMessage(f"已设置数量: {value}")

            # 立即更新列表显示（轻量级操作）
            self.update_current_item_display()

            # 使用较长延迟更新布局预览（重量级操作）
            self.layout_preview_timer.stop()
            self.layout_preview_timer.start(self.layout_debounce_delay)

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

    def add_image_item_to_list(self, image_item):
        """添加图片项到列表（带缩略图）"""
        try:
            # 创建缩略图
            thumbnail = image_item.create_thumbnail((48, 48))

            # 创建显示文本
            display_text = f"{image_item.get_display_name()}\n({image_item.get_size_text()}) [×{image_item.quantity}]"

            # 创建列表项
            list_item = QListWidgetItem()
            list_item.setText(display_text)

            # 设置图标（缩略图）
            if thumbnail:
                list_item.setIcon(QIcon(thumbnail))

            # 添加到列表
            self.image_listbox.addItem(list_item)

        except Exception as e:
            print(f"添加图片项到列表失败: {e}")
            # 降级处理：只添加文本
            display_text = f"{image_item.get_display_name()} ({image_item.get_size_text()}) [×{image_item.quantity}]"
            self.image_listbox.addItem(display_text)

    def update_image_list_display(self):
        """更新图片列表显示"""
        current_row = self.image_listbox.currentRow()

        # 重新构建列表显示
        self.image_listbox.clear()
        for image_item in self.image_items:
            self.add_image_item_to_list(image_item)

        # 恢复选择
        if current_row >= 0 and current_row < len(self.image_items):
            self.image_listbox.setCurrentRow(current_row)

    def update_edit_preview(self):
        """更新编辑预览（兼容性方法）"""
        # 新版本使用交互式编辑器，这个方法主要用于兼容性
        pass

    def delayed_update_edit_preview(self):
        """延迟更新编辑预览（防抖）"""
        try:
            self.update_edit_preview()
        except Exception as e:
            print(f"延迟更新编辑预览失败: {e}")

    def delayed_update_layout_preview(self):
        """延迟更新布局预览（防抖）"""
        try:
            self.update_layout_preview()
        except Exception as e:
            print(f"延迟更新布局预览失败: {e}")

    def delayed_update_image_list(self):
        """延迟更新图片列表（防抖）"""
        try:
            self.update_image_list_display()
        except Exception as e:
            print(f"延迟更新图片列表失败: {e}")

    def update_current_item_display(self):
        """更新当前选中项的显示（轻量级操作）"""
        try:
            current_row = self.image_listbox.currentRow()
            if current_row >= 0 and current_row < len(self.image_items):
                image_item = self.image_items[current_row]

                # 更新当前项的文本
                display_text = f"{image_item.get_display_name()}\n({image_item.get_size_text()}) [×{image_item.quantity}]"
                current_item = self.image_listbox.item(current_row)
                if current_item:
                    current_item.setText(display_text)
        except Exception as e:
            print(f"更新当前项显示失败: {e}")

    def fit_preview_to_window(self):
        """适应窗口显示预览"""
        try:
            self.interactive_scroll_area.fit_to_window()
            self.status_bar.showMessage("预览已适应窗口大小")
        except Exception as e:
            print(f"适应窗口失败: {e}")

    def reset_preview_view(self):
        """重置预览视图"""
        try:
            self.interactive_scroll_area.reset_view()
            self.status_bar.showMessage("预览视图已重置")
        except Exception as e:
            print(f"重置视图失败: {e}")

    def on_diameter_change(self, value):
        """圆形直径改变事件"""
        app_config.badge_diameter_mm = value
        self.status_bar.showMessage(f"圆形直径已设置为: {value}mm")

    def set_diameter(self, diameter):
        """设置圆形直径"""
        self.diameter_spinbox.setValue(diameter)
        app_config.badge_diameter_mm = diameter
        self.status_bar.showMessage(f"圆形直径已设置为: {diameter}mm")

    def on_config_changed(self, key, old_value, new_value):
        """配置变化事件"""
        # 避免未使用参数警告
        _ = old_value, new_value

        if key == 'badge_diameter_mm':
            # 重新创建所有编辑器和预览
            self.current_editor = None

            # 如果有选中的图片，重新加载编辑器
            if self.current_selection:
                self.load_image_editor()

            # 延迟更新布局预览
            self.layout_preview_timer.stop()
            self.layout_preview_timer.start(self.layout_debounce_delay)

    def print_layout(self):
        """打印当前A4排版"""
        try:
            # 检查是否有图片可以打印
            expanded_images = self.get_expanded_image_list()
            if not expanded_images:
                QMessageBox.warning(self, "打印失败", "没有图片可以打印，请先导入图片。")
                return

            # 导入打印相关模块
            from PySide6.QtPrintSupport import QPrinter, QPrintDialog

            # 创建打印机对象（使用高分辨率模式，其他设置让用户在对话框中控制）
            printer = QPrinter(QPrinter.HighResolution)

            # 只设置基本的输出格式，其他设置交给用户
            printer.setOutputFormat(QPrinter.NativeFormat)  # 使用本地打印格式

            # 显示打印对话框（用户可以在此设置纸张、方向、边距等）
            print_dialog = QPrintDialog(printer, self)
            print_dialog.setWindowTitle("打印A4排版")

            if print_dialog.exec() == QPrintDialog.Accepted:
                # 执行打印
                self.status_bar.showMessage("正在打印...")

                # 生成打印内容（使用标准槽函数）
                try:
                    self._current_print_images = expanded_images
                    self.paint_requested_handler(printer)
                    self.status_bar.showMessage("打印完成")
                    QMessageBox.information(self, "打印成功", "A4排版已发送到打印机！")
                except Exception as print_error:
                    self.status_bar.showMessage("打印失败")
                    QMessageBox.warning(self, "打印失败", f"打印过程中发生错误：{str(print_error)}")
            else:
                self.status_bar.showMessage("打印已取消")

        except ImportError:
            QMessageBox.critical(
                self,
                "打印功能不可用",
                "打印功能需要Qt打印支持模块，请确保已正确安装PySide6。"
            )
        except Exception as e:
            QMessageBox.critical(self, "打印错误", f"打印时发生错误：{str(e)}")
            self.status_bar.showMessage("打印失败")

    def print_preview(self):
        """打印预览"""
        try:
            # 检查是否有图片可以预览
            expanded_images = self.get_expanded_image_list()
            if not expanded_images:
                QMessageBox.warning(self, "预览失败", "没有图片可以预览，请先导入图片。")
                return

            # 导入打印预览相关模块
            from PySide6.QtPrintSupport import QPrintPreviewDialog
            from PySide6.QtCore import Qt

            # 创建打印预览对话框（使用默认设置，用户可以在预览中调整）
            preview_dialog = QPrintPreviewDialog(self)
            preview_dialog.setWindowTitle("打印预览 - A4排版")

            # 连接预览信号（参考文章的标准方式）
            # 保存expanded_images到实例变量，供槽函数使用
            self._current_print_images = expanded_images
            preview_dialog.paintRequested.connect(self.paint_requested_handler)

            # 打印预览窗口最大化（参考文章建议）
            preview_dialog.setWindowState(Qt.WindowMaximized)

            # 显示预览对话框
            preview_dialog.exec()

        except ImportError:
            QMessageBox.critical(
                self,
                "打印预览不可用",
                "打印预览功能需要Qt打印支持模块，请确保已正确安装PySide6。"
            )
        except Exception as e:
            QMessageBox.critical(self, "预览错误", f"打印预览时发生错误：{str(e)}")

    def _pil_to_qpixmap(self, pil_image):
        """将PIL图片转换为QPixmap"""
        try:
            from PySide6.QtGui import QPixmap
            from io import BytesIO
            from PIL import Image

            # 将PIL图片保存到字节流
            buffer = BytesIO()
            # 如果是RGBA模式，转换为RGB
            if pil_image.mode == 'RGBA':
                # 创建白色背景
                background = Image.new('RGB', pil_image.size, (255, 255, 255))
                background.paste(pil_image, mask=pil_image.split()[-1])  # 使用alpha通道作为遮罩
                pil_image = background

            pil_image.save(buffer, format='PNG')
            buffer.seek(0)

            # 从字节流创建QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            return pixmap

        except Exception as e:
            print(f"PIL到QPixmap转换失败: {e}")
            # 返回空白pixmap
            from PySide6.QtGui import QPixmap
            blank_pixmap = QPixmap(100, 100)
            blank_pixmap.fill()
            return blank_pixmap

    def paint_requested_handler(self, printer):
        """打印预览槽函数 - 预先生成A4图片再打印"""
        try:
            from PySide6.QtGui import QPainter

            # 获取当前要打印的图片列表
            expanded_images = getattr(self, '_current_print_images', [])

            # 预先生成完整的A4排版图片（高分辨率用于打印）
            print("正在生成A4排版图片...")
            a4_pixmap = self._generate_print_ready_a4_image(expanded_images)

            if not a4_pixmap or a4_pixmap.isNull():
                print("生成A4排版图片失败")
                return

            # 创建QPainter并直接绘制预生成的A4图片
            painter = QPainter(printer)

            # 获取整个纸张区域（而不是可打印区域，避免双重边距）
            from PySide6.QtPrintSupport import QPrinter
            from PySide6.QtCore import QRect
            paper_rect_f = printer.paperRect(QPrinter.Unit.DevicePixel)

            # 转换QRectF为QRect（drawPixmap需要QRect参数）
            paper_rect = QRect(
                int(paper_rect_f.x()),
                int(paper_rect_f.y()),
                int(paper_rect_f.width()),
                int(paper_rect_f.height())
            )

            # 直接将完整的A4图片绘制到整个纸张区域
            # 这样可以确保与导出图片的效果完全一致，避免双重边距
            painter.drawPixmap(paper_rect, a4_pixmap)

            print(f"打印区域: {paper_rect.width()}x{paper_rect.height()}像素")
            print(f"图片尺寸: {a4_pixmap.width()}x{a4_pixmap.height()}像素")

            painter.end()
            print("A4图片已发送到打印机")

        except Exception as e:
            print(f"打印渲染失败: {e}")
            import traceback
            traceback.print_exc()

    def _generate_print_ready_a4_image(self, expanded_images):
        """
        生成打印就绪的A4图片（使用与导出图片相同的逻辑确保一致性）
        参数:
            expanded_images: 展开后的图片列表
        返回: QPixmap - 高分辨率的A4排版图片
        """
        try:
            from PySide6.QtGui import QPixmap
            from PIL import Image
            from io import BytesIO

            # 使用导出管理器生成图片，确保与导出功能完全一致
            print("使用导出逻辑生成打印图片...")

            # 计算布局（与导出图片使用相同的逻辑）
            if self.layout_mode == 'grid':
                layout = self.layout_engine.calculate_grid_layout(self.spacing_value, self.margin_value)
            else:
                layout = self.layout_engine.calculate_compact_layout(self.spacing_value, self.margin_value)

            # 创建A4画布（与导出图片使用相同的尺寸和DPI）
            from utils.config import PRINT_DPI
            canvas_img = Image.new('RGB', (self.layout_engine.a4_width_px, self.layout_engine.a4_height_px), (255, 255, 255))

            # 处理每个图片（与导出图片使用相同的逻辑）
            positions = layout['positions']
            processed_count = 0

            for i, image_item in enumerate(expanded_images):
                if i >= len(positions):
                    break  # 超出可放置数量

                try:
                    # 获取圆形图片
                    from core.image_processor import ImageProcessor
                    processor = ImageProcessor()

                    circle_img = processor.create_circular_crop(
                        image_item.file_path,
                        image_item.scale,
                        image_item.offset_x,
                        image_item.offset_y,
                        image_item.rotation
                    )

                    # 计算粘贴位置（圆心位置转换为左上角位置）
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
                    # 继续处理下一张图片

            # 转换为QPixmap（与导出图片使用相同的转换逻辑）
            buffer = BytesIO()
            canvas_img.save(buffer, format='PNG', dpi=(PRINT_DPI, PRINT_DPI))
            buffer.seek(0)

            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())

            if pixmap and not pixmap.isNull():
                print(f"生成打印图片成功: {pixmap.width()}x{pixmap.height()}像素，处理了{processed_count}张图片")
                return pixmap
            else:
                print("转换为QPixmap失败")
                return None

        except Exception as e:
            print(f"生成打印图片失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def render_to_printer(self, printer, expanded_images):
        """将A4排版渲染到打印机（兼容旧接口）"""
        # 设置当前打印图片并调用标准槽函数
        self._current_print_images = expanded_images
        self.paint_requested_handler(printer)

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
