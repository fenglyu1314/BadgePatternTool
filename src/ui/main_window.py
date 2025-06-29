"""
主窗口界面模块 - PySide6版本
实现BadgePatternTool的主界面布局
"""

import traceback
from io import BytesIO

# PySide6 GUI组件导入
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QListWidgetItem,
    QSlider, QRadioButton, QComboBox, QButtonGroup, QSpinBox,
    QMessageBox, QStatusBar, QSplitter, QGroupBox,
    QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QSize, QPoint, QMarginsF, QRect
from PySide6.QtGui import QAction, QIcon, QPixmap, QPainter, QPageLayout, QBitmap
from PySide6.QtPrintSupport import QPrinter
from PIL import Image

# 导入公共模块
from common.constants import (
    APP_TITLE, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT,
    DEFAULT_SPACING_MM, DEFAULT_MARGIN_MM, DEFAULT_LAYOUT, DEFAULT_EXPORT_FORMAT,
    MAX_IMAGE_COUNT, COLUMN_WIDTHS
)
from common.path_utils import get_icon_path
from common.error_handler import logger, show_error_message, show_info_message

# 项目模块导入
from utils.config import app_config
from utils.file_handler import FileHandler, ImageItem
from core.image_processor import ImageProcessor, CircleEditor
from core.layout_engine import LayoutEngine
from core.export_manager import ExportManager
from ui.interactive_image_editor import InteractiveImageEditor
from ui.multi_page_preview_widget import MultiPagePreviewWidget

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()

        try:
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
            self.spacing_value = DEFAULT_SPACING_MM
            self.margin_value = DEFAULT_MARGIN_MM
            self.export_format = DEFAULT_EXPORT_FORMAT.lower()
            self.scale_value = 1.0
            self.offset_x_value = 0
            self.offset_y_value = 0
            self.preview_scale_value = 0.5  # 预览缩放比例

            # 初始化防抖定时器
            self.setup_debounce_timers()

            # A4预览缓存状态
            self._last_preview_hash = None
            self._preview_cache_valid = False

            # 打印页面缓存（高分辨率版本）
            self._cached_print_pages = []

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

            logger.info("主窗口初始化完成")

        except Exception as e:
            logger.error(f"主窗口初始化失败: {e}", exc_info=True)
            show_error_message("初始化错误", f"程序初始化失败：{str(e)}")
            raise

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

        # 防抖延迟时间（毫秒）- 优化性能
        self.debounce_delay = 100  # 减少到100ms，提高响应性
        self.layout_debounce_delay = 500  # 增加到500ms，减少A4预览的频繁更新
        self.quantity_debounce_delay = 800  # 数量变化使用更长延迟，避免频繁重建预览

    def setup_window(self):
        """设置窗口基本属性"""
        self.setWindowTitle(f"{APP_TITLE} v{APP_VERSION}")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)

        # 设置窗口图标
        try:
            icon_path = get_icon_path("icon.ico")
            if icon_path.exists():
                icon = QIcon(str(icon_path))
                if not icon.isNull():
                    self.setWindowIcon(icon)
                    logger.info(f"窗口图标加载成功: {icon_path.name}")
                else:
                    logger.warning("图标文件无效")
            else:
                logger.warning("未找到窗口图标文件")
        except Exception as e:
            logger.error(f"设置窗口图标失败: {e}")

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

        clear_all_action = QAction("清空列表", self)
        clear_all_action.triggered.connect(self.clear_all)
        edit_menu.addAction(clear_all_action)
        
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
        splitter = QSplitter(Qt.Orientation.Horizontal)
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
        column_widths = COLUMN_WIDTHS
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
        self.image_listbox.setViewMode(QListWidget.ViewMode.ListMode)  # 列表模式，显示图标和文字
        self.image_listbox.setIconSize(QSize(48, 48))  # 设置图标大小
        self.image_listbox.setSpacing(2)  # 设置项目间距
        self.image_listbox.setUniformItemSizes(True)  # 统一项目大小

        # 启用拖拽功能
        self.image_listbox.setAcceptDrops(True)
        self.image_listbox.setDragDropMode(QListWidget.DragDropMode.DropOnly)

        # 重写拖拽事件处理
        self.setup_drag_drop()

        layout.addWidget(self.image_listbox)

        # 操作按钮
        btn_layout = QHBoxLayout()

        copy_btn = QPushButton("复制")
        copy_btn.clicked.connect(self.copy_selected)
        btn_layout.addWidget(copy_btn)

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
        # A4预览面板框架（与其他区域保持一致的样式）
        preview_frame = QGroupBox("排版预览")
        parent.addWidget(preview_frame)

        layout = QVBoxLayout(preview_frame)

        # 信息栏
        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(5)

        # 布局信息标签（与其他区域保持一致的字体大小）
        self.layout_info_label = QLabel("每页可放置: 0个 | 当前: 0个")
        self.layout_info_label.setStyleSheet("color: #666; padding: 2px;")
        info_layout.addWidget(self.layout_info_label)

        info_layout.addStretch()  # 推到右边

        # 缩放倍率显示标签
        self.preview_scale_info_label = QLabel("缩放: 100%")
        self.preview_scale_info_label.setStyleSheet("color: #666; padding: 2px; font-size: 11px;")
        info_layout.addWidget(self.preview_scale_info_label)

        layout.addLayout(info_layout)

        # A4预览组件（占用大部分空间）- 使用多页面预览组件
        self.multi_page_preview = MultiPagePreviewWidget()
        self.multi_page_preview.setMinimumHeight(400)
        # 设置拉伸因子，让预览组件占用大部分空间
        layout.addWidget(self.multi_page_preview, 1)  # 拉伸因子为1

        # 视图控制按钮（放在预览区域下面）
        view_control_layout = QHBoxLayout()
        view_control_layout.setContentsMargins(0, 0, 0, 0)
        view_control_layout.setSpacing(5)

        fit_btn = QPushButton("适应窗口")
        fit_btn.clicked.connect(self.fit_preview_to_window)
        view_control_layout.addWidget(fit_btn)

        reset_view_btn = QPushButton("重置视图")
        reset_view_btn.clicked.connect(self.reset_preview_view)
        view_control_layout.addWidget(reset_view_btn)

        layout.addLayout(view_control_layout)

        # 连接预览标签的信号
        if hasattr(self.multi_page_preview, 'scale_changed'):
            self.multi_page_preview.scale_changed.connect(self.on_preview_scale_changed)

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

        self.spacing_slider = QSlider(Qt.Orientation.Horizontal)
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

        self.margin_slider = QSlider(Qt.Orientation.Horizontal)
        self.margin_slider.setRange(5, 30)  # 最小5mm（打印机限制），最大30mm
        self.margin_slider.setValue(int(self.margin_value))
        self.margin_slider.valueChanged.connect(self.on_margin_change)
        margin_layout.addWidget(self.margin_slider)

        # 徽章尺寸设置
        size_group = QGroupBox("徽章尺寸")
        layout.addWidget(size_group)

        size_layout = QVBoxLayout(size_group)

        # 徽章尺寸设置
        badge_layout = QHBoxLayout()
        badge_layout.addWidget(QLabel("徽章:"))

        self.badge_size_spinbox = QSpinBox()
        self.badge_size_spinbox.setRange(10, 100)  # 10-100mm，支持75mm
        self.badge_size_spinbox.setValue(int(app_config.badge_size_mm))
        self.badge_size_spinbox.setSuffix("mm")
        self.badge_size_spinbox.valueChanged.connect(self.on_badge_size_change)
        badge_layout.addWidget(self.badge_size_spinbox)

        size_layout.addLayout(badge_layout)

        # 出血半径设置
        bleed_layout = QHBoxLayout()
        bleed_layout.addWidget(QLabel("出血半径:"))

        self.bleed_size_spinbox = QSpinBox()
        self.bleed_size_spinbox.setRange(0, 10)  # 0-10mm（半径）
        self.bleed_size_spinbox.setValue(int(app_config.bleed_size_mm))
        self.bleed_size_spinbox.setSuffix("mm")
        self.bleed_size_spinbox.valueChanged.connect(self.on_bleed_size_change)
        bleed_layout.addWidget(self.bleed_size_spinbox)

        size_layout.addLayout(bleed_layout)

        # 总直径显示
        self.total_diameter_label = QLabel(f"总直径: {app_config.badge_diameter_mm}mm")
        self.total_diameter_label.setStyleSheet("font-weight: bold; color: #666;")
        size_layout.addWidget(self.total_diameter_label)

        # 预设按钮
        preset_layout = QHBoxLayout()

        btn_32 = QPushButton("32+5")
        btn_32.clicked.connect(lambda: self.set_badge_preset(32, 5))
        preset_layout.addWidget(btn_32)

        btn_58 = QPushButton("58+5")
        btn_58.clicked.connect(lambda: self.set_badge_preset(58, 5))
        preset_layout.addWidget(btn_58)

        btn_75 = QPushButton("75+5")
        btn_75.clicked.connect(lambda: self.set_badge_preset(75, 5))
        preset_layout.addWidget(btn_75)

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
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def create_edit_controls(self, parent_layout):
        """创建编辑控制区域"""
        # 遮罩透明度设置（移到最上面）
        mask_group = QGroupBox("遮罩设置")
        parent_layout.addWidget(mask_group)

        mask_layout = QVBoxLayout(mask_group)

        # 圆形外部透明度
        outside_layout = QHBoxLayout()
        outside_layout.addWidget(QLabel("外部区域:"))

        self.outside_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.outside_opacity_slider.setRange(0, 100)
        self.outside_opacity_slider.setValue(app_config.outside_opacity)
        self.outside_opacity_slider.valueChanged.connect(self.on_outside_opacity_change)
        outside_layout.addWidget(self.outside_opacity_slider)

        self.outside_opacity_label = QLabel(f"{app_config.outside_opacity}%")
        self.outside_opacity_label.setMinimumWidth(40)
        outside_layout.addWidget(self.outside_opacity_label)

        mask_layout.addLayout(outside_layout)

        # 出血区透明度
        bleed_opacity_layout = QHBoxLayout()
        bleed_opacity_layout.addWidget(QLabel("出血区:"))

        self.bleed_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.bleed_opacity_slider.setRange(0, 100)
        self.bleed_opacity_slider.setValue(app_config.bleed_opacity)
        self.bleed_opacity_slider.valueChanged.connect(self.on_bleed_opacity_change)
        bleed_opacity_layout.addWidget(self.bleed_opacity_slider)

        self.bleed_opacity_label = QLabel(f"{app_config.bleed_opacity}%")
        self.bleed_opacity_label.setMinimumWidth(40)
        bleed_opacity_layout.addWidget(self.bleed_opacity_label)

        mask_layout.addLayout(bleed_opacity_layout)

        # 缩放控制（直接添加，无框框）
        self.scale_label = QLabel("图片缩放: 1.0")
        self.scale_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        parent_layout.addWidget(self.scale_label)

        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(10, 1000)  # 0.1 到 10.0
        self.scale_slider.setValue(100)  # 1.0
        self.scale_slider.valueChanged.connect(self.on_scale_change)
        parent_layout.addWidget(self.scale_slider)

        # X轴偏移（直接添加，无框框）
        self.offset_x_label = QLabel("X偏移: 0")
        self.offset_x_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        parent_layout.addWidget(self.offset_x_label)

        self.offset_x_slider = QSlider(Qt.Orientation.Horizontal)
        self.offset_x_slider.setRange(-100, 100)
        self.offset_x_slider.setValue(0)
        self.offset_x_slider.valueChanged.connect(self.on_position_change)
        parent_layout.addWidget(self.offset_x_slider)

        # Y轴偏移（直接添加，无框框）
        self.offset_y_label = QLabel("Y偏移: 0")
        self.offset_y_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        parent_layout.addWidget(self.offset_y_label)

        self.offset_y_slider = QSlider(Qt.Orientation.Horizontal)
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

    def setup_drag_drop(self):
        """设置拖拽功能"""
        # 保存原始的拖拽事件处理方法
        original_dragEnterEvent = self.image_listbox.dragEnterEvent
        original_dragMoveEvent = self.image_listbox.dragMoveEvent
        original_dropEvent = self.image_listbox.dropEvent

        def dragEnterEvent(event):
            """拖拽进入事件"""
            if event.mimeData().hasUrls():
                # 检查是否包含图片文件
                urls = event.mimeData().urls()
                has_images = False
                for url in urls:
                    if url.isLocalFile():
                        file_path = url.toLocalFile()
                        if self.file_handler.validate_image_file(file_path):
                            has_images = True
                            break

                if has_images:
                    event.acceptProposedAction()
                    return

            event.ignore()

        def dragMoveEvent(event):
            """拖拽移动事件"""
            if event.mimeData().hasUrls():
                event.acceptProposedAction()
            else:
                event.ignore()

        def dropEvent(event):
            """拖拽放下事件"""
            if event.mimeData().hasUrls():
                urls = event.mimeData().urls()
                file_paths = []

                for url in urls:
                    if url.isLocalFile():
                        file_path = url.toLocalFile()
                        if self.file_handler.validate_image_file(file_path):
                            file_paths.append(file_path)

                if file_paths:
                    # 使用现有的导入逻辑处理文件
                    self.import_files_from_paths(file_paths)
                    event.acceptProposedAction()
                else:
                    QMessageBox.warning(self, "拖拽导入", "没有找到有效的图片文件")
                    event.ignore()
            else:
                event.ignore()

        # 替换事件处理方法
        self.image_listbox.dragEnterEvent = dragEnterEvent
        self.image_listbox.dragMoveEvent = dragMoveEvent
        self.image_listbox.dropEvent = dropEvent
        
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
                    # 移除重复检查，允许同一文件多次导入
                    # 创建图片项
                    image_item = ImageItem(file_path)
                    self.image_items.append(image_item)

                    # 添加到界面列表（带缩略图）
                    self.add_image_item_to_list(image_item)

                    added_count += 1

                except Exception as e:
                    print(f"添加图片失败 {file_path}: {e}")
                    continue

            # 清除预览缓存
            self._preview_cache_valid = False

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

    def import_files_from_paths(self, file_paths):
        """从文件路径列表导入图片（用于拖拽导入）"""
        try:
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
                self.status_bar.showMessage(f"拖拽导入成功 {added_count} 张图片，总计 {len(self.image_items)} 张")
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
            QMessageBox.critical(self, "错误", f"拖拽导入图片时发生错误：{str(e)}")
            self.status_bar.showMessage("拖拽导入失败")

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
                # 使用kwargs方式传递参数给export_to_image
                success, count = self.export_manager.export_to_image(
                    expanded_images, output_path,
                    format_type=format_type.upper(),
                    layout_type=layout_type,
                    spacing_mm=spacing_mm,
                    margin_mm=margin_mm
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
        
    def copy_selected(self):
        """复制选中项"""
        current_row = self.image_listbox.currentRow()
        if current_row >= 0 and current_row < len(self.image_items):
            try:
                # 获取选中的图片项
                selected_item = self.image_items[current_row]

                # 创建副本
                copied_item = selected_item.copy()

                # 插入到选中项的下一位
                insert_index = current_row + 1
                self.image_items.insert(insert_index, copied_item)

                # 更新界面列表显示
                self.update_image_list_display()

                # 选中新复制的项
                self.image_listbox.setCurrentRow(insert_index)

                # 更新预览
                self.update_layout_preview()

                self.status_bar.showMessage(f"已复制: {copied_item.get_display_name()}")

            except Exception as e:
                QMessageBox.critical(self, "错误", f"复制图片失败：{str(e)}")
        else:
            QMessageBox.warning(self, "提示", "请先选择要复制的图片")

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

            # 清除预览缓存
            self._preview_cache_valid = False

            self.status_bar.showMessage(f"已删除: {deleted_item.get_display_name()}")

            # 如果还有项目，选中相邻的项
            if self.image_items:
                new_index = min(current_row, len(self.image_items) - 1)
                self.image_listbox.setCurrentRow(new_index)

            # 更新预览
            self.update_layout_preview()
        

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
        """交互式编辑器参数改变事件（优化性能）"""
        if self.current_editor:
            # 更新圆形编辑器参数
            self.current_editor.scale = scale
            self.current_editor.offset_x = offset_x
            self.current_editor.offset_y = offset_y

            # 只有在值真正改变时才更新滑块
            current_scale_value = int(scale * 100)
            if self.scale_slider.value() != current_scale_value:
                self.scale_slider.blockSignals(True)
                self.scale_slider.setValue(current_scale_value)
                self.scale_slider.blockSignals(False)
                self.scale_label.setText(f"图片缩放: {scale:.1f}")

            if self.offset_x_slider.value() != offset_x:
                self.offset_x_slider.blockSignals(True)
                self.offset_x_slider.setValue(offset_x)
                self.offset_x_slider.blockSignals(False)
                self.offset_x_label.setText(f"X偏移: {offset_x}")

            if self.offset_y_slider.value() != offset_y:
                self.offset_y_slider.blockSignals(True)
                self.offset_y_slider.setValue(offset_y)
                self.offset_y_slider.blockSignals(False)
                self.offset_y_label.setText(f"Y偏移: {offset_y}")

    def on_scale_change(self, value):
        """缩放改变事件（带防抖）"""
        if self.current_editor:
            scale = value / 100.0  # 转换为0.1-10.0范围

            # 避免重复处理相同的值
            if abs(self.scale_value - scale) < 0.01:
                return

            self.scale_value = scale
            self.scale_label.setText(f"图片缩放: {scale:.1f}")
            self.current_editor.set_scale(scale)

            # 同步到交互式编辑器（立即更新，因为有缓存优化）
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

            # 避免重复处理相同的值
            if self.offset_x_value == offset_x and self.offset_y_value == offset_y:
                return

            self.offset_x_value = offset_x
            self.offset_y_value = offset_y

            self.offset_x_label.setText(f"X偏移: {offset_x}")
            self.offset_y_label.setText(f"Y偏移: {offset_y}")

            self.current_editor.set_offset(offset_x, offset_y)

            # 同步到交互式编辑器（立即更新，位置变化不影响缓存）
            if hasattr(self, 'interactive_editor') and self.interactive_editor.original_image:
                # 需要将原图坐标系的偏移转换为预览坐标系
                preview_offset_x = int(offset_x * self.interactive_editor.preview_scale_ratio)
                preview_offset_y = int(offset_y * self.interactive_editor.preview_scale_ratio)
                self.interactive_editor.image_offset = QPoint(preview_offset_x, preview_offset_y)
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
        # MultiPagePreviewWidget 不支持 setText，改为在状态栏显示提示
        self.layout_info_label.setText("导入图片后自动显示排版预览")
        if hasattr(self, 'status_bar'):
            self.status_bar.showMessage("支持鼠标滚轮缩放和拖动平移")

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

    def on_preview_scale_changed(self, scale):
        """处理多页面预览组件的缩放变化"""
        # 更新缩放倍率显示
        percentage = int(scale * 100)
        self.preview_scale_info_label.setText(f"缩放: {percentage}%")

    def on_preview_scale_change(self, value):
        """预览缩放改变事件（带防抖）"""
        scale = value / 100.0
        self.preview_scale_value = scale
        self.preview_scale_info_label.setText(f"缩放: {value}%")

        # 同步到多页面预览的缩放
        if hasattr(self, 'multi_page_preview'):
            # 注意：这里不需要同步，因为预览缩放是独立的
            pass

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

    def _calculate_preview_hash(self):
        """计算当前预览状态的哈希值，用于判断是否需要重新生成预览"""
        import hashlib

        # 收集影响预览的所有参数
        hash_data = []

        # 布局参数
        hash_data.append(f"layout:{self.layout_mode}")
        hash_data.append(f"spacing:{self.spacing_value}")
        hash_data.append(f"margin:{self.margin_value}")
        hash_data.append(f"preview_scale:{self.preview_scale_value}")

        # 徽章尺寸参数（重要：影响圆形大小和布局）
        hash_data.append(f"badge_size:{app_config.badge_size_mm}")
        hash_data.append(f"bleed_size:{app_config.bleed_size_mm}")
        hash_data.append(f"badge_diameter:{app_config.badge_diameter_mm}")

        # 图片参数
        for item in self.image_items:
            hash_data.append(f"img:{item.file_path}:{item.quantity}:{item.scale}:{item.offset_x}:{item.offset_y}")

        # 计算哈希
        hash_string = "|".join(hash_data)
        return hashlib.md5(hash_string.encode()).hexdigest()

    def update_layout_preview(self):
        """更新A4排版预览（支持多页面）"""
        try:
            # 计算当前状态哈希
            current_hash = self._calculate_preview_hash()

            # 检查是否需要重新生成预览
            if self._preview_cache_valid and current_hash == self._last_preview_hash:
                # 缓存有效，无需重新生成
                return

            # 获取当前设置
            layout_type = self.layout_mode
            spacing_mm = self.spacing_value
            margin_mm = self.margin_value

            # 获取展开后的图片列表
            expanded_images = self.get_expanded_image_list()

            # 计算多页面布局
            multi_layout = self.layout_engine.calculate_multi_page_layout(
                len(expanded_images), layout_type, spacing_mm, margin_mm
            )

            # 创建多页面预览
            page_previews = self.layout_engine.create_multi_page_preview(
                expanded_images, layout_type, spacing_mm, margin_mm,
                preview_scale=self.preview_scale_value
            )

            # 同时生成高分辨率打印版本（用于打印）
            self._cached_print_pages = self._generate_high_res_print_pages(
                expanded_images, layout_type, spacing_mm, margin_mm
            )

            # 更新多页面预览显示
            self.multi_page_preview.set_page_pixmaps(page_previews)

            # 更新布局信息
            total_images = len(expanded_images)
            unique_images = len(self.image_items)
            total_pages = multi_layout['total_pages']
            max_per_page = multi_layout['max_per_page']

            if not self.image_items:
                # 没有图片时显示布局容量信息
                info_text = f"每页可放置: {max_per_page}个 | 当前: 0个 | 导入图片开始使用"
                self.status_bar.showMessage(f"排版预览 - {layout_type}模式，每页可放置{max_per_page}个圆形")
            else:
                # 有图片时显示详细信息
                if total_pages == 1:
                    info_text = f"可放置: {max_per_page}个 | 总数: {total_images}个 | 种类: {unique_images}个"
                else:
                    info_text = f"共{total_pages}页 | 每页{max_per_page}个 | 总数: {total_images}个 | 种类: {unique_images}个"
                self.status_bar.showMessage(f"排版预览已更新 - {layout_type}模式，共{total_pages}页，{total_images}个图片")

            self.layout_info_label.setText(info_text)

            # 更新缓存状态
            self._last_preview_hash = current_hash
            self._preview_cache_valid = True

        except Exception as e:
            print(f"更新排版预览失败: {e}")
            self.show_layout_hint()
            self._preview_cache_valid = False
            self._cached_print_pages = []  # 清空打印缓存

    def _generate_high_res_print_pages(self, expanded_images, layout_type, spacing_mm, margin_mm):
        """
        生成高分辨率打印页面（用于实际打印）
        使用与预览相同的布局引擎，确保一致性
        """
        try:
            if not expanded_images:
                return []

            print("生成高分辨率打印页面...")

            # 使用layout_engine的多页面预览功能，但设置为1.0比例（全分辨率）
            # 这确保了与预览使用完全相同的布局逻辑和图像处理流程
            print_pages = self.layout_engine.create_multi_page_preview(
                expanded_images, layout_type, spacing_mm, margin_mm,
                preview_scale=1.0  # 使用全分辨率，确保与预览逻辑一致
            )

            print(f"高分辨率打印页面生成完成，共{len(print_pages)}页")
            return print_pages

        except Exception as e:
            print(f"生成高分辨率打印页面失败: {e}")
            traceback.print_exc()
            return []

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

            # 使用专门的数量变化延迟更新布局预览（重量级操作）
            self.layout_preview_timer.stop()
            self.layout_preview_timer.start(self.quantity_debounce_delay)

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
            # 用户主动点击适应窗口按钮时，强制适应并重置手动缩放标志
            self.multi_page_preview.user_has_manually_scaled = False
            self.multi_page_preview.fit_to_window(force=True)
            self.status_bar.showMessage("预览已适应窗口大小")
        except Exception as e:
            print(f"适应窗口失败: {e}")

    def reset_preview_view(self):
        """重置预览视图到1:1比例"""
        try:
            self.multi_page_preview.set_scale(1.0)  # 重置为1:1比例（100%）
            self.multi_page_preview.canvas_offset = QPoint(0, 0)  # 重置画布偏移，确保居中
            self.multi_page_preview.user_has_manually_scaled = False  # 重置手动缩放标志
            self.multi_page_preview.update()  # 刷新显示
            self.status_bar.showMessage("预览视图已重置为1:1比例")
        except Exception as e:
            print(f"重置视图失败: {e}")

    def on_badge_size_change(self, value):
        """徽章尺寸改变事件"""
        app_config.badge_size_mm = value
        self.update_total_diameter_label()
        self.status_bar.showMessage(f"徽章尺寸已设置为: {value}mm")

        # 更新交互式编辑器的遮罩半径
        if hasattr(self, 'interactive_editor') and self.interactive_editor:
            self.interactive_editor.update_mask_radius()

        # 触发排版预览更新
        self.update_layout_preview()

    def on_bleed_size_change(self, value):
        """出血半径改变事件"""
        app_config.bleed_size_mm = value
        self.update_total_diameter_label()
        self.status_bar.showMessage(f"出血半径已设置为: {value}mm")

        # 更新交互式编辑器的遮罩半径
        if hasattr(self, 'interactive_editor') and self.interactive_editor:
            self.interactive_editor.update_mask_radius()

        # 触发排版预览更新
        self.update_layout_preview()



    def set_badge_preset(self, badge_size, bleed_size):
        """设置徽章预设"""
        self.badge_size_spinbox.setValue(badge_size)
        self.bleed_size_spinbox.setValue(bleed_size)
        app_config.badge_size_mm = badge_size
        app_config.bleed_size_mm = bleed_size
        self.update_total_diameter_label()
        self.status_bar.showMessage(f"预设: 徽章{badge_size}mm + 出血半径{bleed_size}mm")

        # 更新交互式编辑器的遮罩半径
        if hasattr(self, 'interactive_editor') and self.interactive_editor:
            self.interactive_editor.update_mask_radius()

        # 触发排版预览更新
        self.update_layout_preview()

    def update_total_diameter_label(self):
        """更新总直径标签"""
        total = app_config.badge_diameter_mm
        self.total_diameter_label.setText(f"总直径: {total}mm")

    def on_outside_opacity_change(self, value):
        """外部区域透明度改变事件"""
        app_config.outside_opacity = value
        self.outside_opacity_label.setText(f"{value}%")
        # 更新单图编辑器
        if hasattr(self, 'interactive_editor') and self.interactive_editor:
            self.interactive_editor.repaint()
        self.status_bar.showMessage(f"外部区域透明度: {value}%")

    def on_bleed_opacity_change(self, value):
        """出血区透明度改变事件"""
        app_config.bleed_opacity = value
        self.bleed_opacity_label.setText(f"{value}%")
        # 更新单图编辑器
        if hasattr(self, 'interactive_editor') and self.interactive_editor:
            self.interactive_editor.repaint()
        self.status_bar.showMessage(f"出血区透明度: {value}%")

    # 保持向后兼容
    def on_diameter_change(self, value):
        """圆形直径改变事件（向后兼容）"""
        app_config.badge_diameter_mm = value
        self.status_bar.showMessage(f"圆形直径已设置为: {value}mm")

    def set_diameter(self, diameter):
        """设置圆形直径（向后兼容）"""
        app_config.badge_diameter_mm = diameter
        self.status_bar.showMessage(f"圆形直径已设置为: {diameter}mm")

    def on_config_changed(self, key, old_value, new_value):
        """配置变化事件"""
        # 避免未使用参数警告
        _ = old_value, new_value

        if key == 'badge_diameter_mm':
            # 清理所有缓存以释放内存
            self.clear_all_caches()

            # 重新创建所有编辑器和预览
            self.current_editor = None

            # 如果有选中的图片，重新加载编辑器
            if self.current_selection:
                self.load_image_editor()

            # 延迟更新布局预览
            self.layout_preview_timer.stop()
            self.layout_preview_timer.start(self.layout_debounce_delay)

    def clear_all_caches(self):
        """清理所有缓存，释放内存"""
        try:
            # 清理图片处理器缓存
            if hasattr(self, 'image_processor'):
                self.image_processor.clear_cache()

            # 清理布局引擎缓存
            if hasattr(self, 'layout_engine') and hasattr(self.layout_engine, 'clear_cache'):
                self.layout_engine.clear_cache()

            # 清理交互式编辑器缓存
            if hasattr(self, 'interactive_editor'):
                self.interactive_editor._invalidate_cache()

            # 清理A4预览缓存
            self._last_preview_hash = None
            self._preview_cache_valid = False
            self._cached_print_pages.clear()

            logger.info("所有缓存已清理")

        except Exception as e:
            logger.error(f"清理缓存失败: {e}", exc_info=True)

    def print_layout(self):
        """打印当前A4排版 - 使用自定义打印对话框"""
        try:
            # 获取图片列表
            expanded_images = self.get_expanded_image_list()
            if not expanded_images:
                QMessageBox.warning(self, "打印失败", "没有图片可以打印，请先导入图片。")
                return

            # 生成预览图片
            preview_pixmap = self._generate_print_preview_image(expanded_images)

            # 导入自定义打印对话框
            from ui.custom_print_dialog import CustomPrintDialog

            # 创建自定义打印对话框
            print_dialog = CustomPrintDialog(preview_pixmap, self)
            print_dialog.print_requested.connect(lambda settings: self._execute_custom_print(settings, expanded_images))

            # 显示对话框
            print_dialog.exec()

        except ImportError as e:
            QMessageBox.critical(
                self,
                "打印功能不可用",
                f"打印功能需要相关模块，请确保已正确安装：{str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(self, "打印错误", f"打印时发生错误：{str(e)}")
            traceback.print_exc()

    def _generate_print_preview_image(self, expanded_images):
        """生成打印预览图片"""
        try:
            # 使用现有的布局引擎生成预览
            preview_pixmap = self.layout_engine.create_layout_preview(
                expanded_images,
                self.layout_mode,
                self.spacing_value,
                self.margin_value,
                preview_scale=1.0  # 使用全尺寸预览
            )

            return preview_pixmap

        except Exception as e:
            print(f"生成打印预览失败: {e}")
            return None

    def _execute_custom_print(self, settings, expanded_images):
        """执行简化的打印"""
        try:
            # 获取选中的打印机
            printer_info = settings['printer']
            if not printer_info:
                QMessageBox.warning(self, "打印失败", "未选择打印机")
                return

            # 创建打印机对象
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setPrinterName(printer_info.printerName())

            # 设置打印参数
            printer.setCopyCount(settings['copies'])

            # 设置彩色模式
            if settings.get('color_mode') == 'grayscale':
                printer.setColorMode(QPrinter.ColorMode.GrayScale)
            else:
                printer.setColorMode(QPrinter.ColorMode.Color)

            # 配置打印机为一致性设置（零页边距、全页模式）
            self._configure_printer_for_consistency(printer)

            # 执行打印
            self.status_bar.showMessage("正在打印...")

            # 使用简单打印方法
            self._simple_print_to_printer(printer, expanded_images)

            self.status_bar.showMessage("打印完成")
            QMessageBox.information(self, "打印成功", "A4排版已发送到打印机！")

        except Exception as e:
            self.status_bar.showMessage("打印失败")
            QMessageBox.warning(self, "打印失败", f"打印过程中发生错误：{str(e)}")
            traceback.print_exc()





    def _configure_printer_for_consistency(self, printer):
        """配置打印机设置，确保与排版预览一致"""
        try:


            print("配置打印机设置...")

            # 设置零页边距，确保与预览一致
            printer.setPageMargins(QMarginsF(0, 0, 0, 0), QPageLayout.Unit.Millimeter)

            # 启用全页模式，使用整个纸张区域
            printer.setFullPage(True)

            # 设置高分辨率
            printer.setResolution(300)

            print("打印机配置完成：零页边距、全页模式、300DPI")

        except Exception as e:
            print(f"配置打印机失败: {e}")
            # 配置失败不影响打印，继续使用默认设置

    def _simple_print_to_printer(self, printer, expanded_images):
        """简单的打印实现 - 使用与导出功能完全相同的逻辑"""
        try:
            print("开始打印，使用与导出相同的逻辑...")

            # 创建QPainter
            painter = QPainter()
            if not painter.begin(printer):
                raise Exception("无法初始化打印机")

            try:
                # 计算多页面布局（与导出功能完全相同）
                multi_layout = self.layout_engine.calculate_multi_page_layout(
                    len(expanded_images), self.layout_mode, self.spacing_value, self.margin_value
                )

                print(f"打印{multi_layout['total_pages']}页内容...")
                image_index = 0

                # 为每个页面打印
                for page_info in multi_layout['pages']:
                    print(f"打印第{page_info['page_index'] + 1}页...")

                    # 获取当前页面的图片
                    page_images = expanded_images[image_index:image_index + page_info['images_on_page']]

                    # 使用与导出功能完全相同的方法生成页面图片
                    page_pixmap = self._generate_print_page_like_export(page_images, page_info)

                    if page_pixmap and not page_pixmap.isNull():
                        # 获取打印区域
                        page_rect_f = printer.pageRect(QPrinter.Unit.DevicePixel)

                        # 使用坐标和尺寸的方式绘制，避免类型问题
                        painter.drawPixmap(
                            int(page_rect_f.x()),
                            int(page_rect_f.y()),
                            int(page_rect_f.width()),
                            int(page_rect_f.height()),
                            page_pixmap
                        )
                        print(f"第{page_info['page_index'] + 1}页已发送到打印机")
                    else:
                        print(f"第{page_info['page_index'] + 1}页生成失败，跳过")

                    # 更新图片索引
                    image_index += page_info['images_on_page']

                    # 如果不是最后一页，添加新页面
                    if page_info['page_index'] < multi_layout['total_pages'] - 1:
                        if not printer.newPage():
                            raise Exception("无法创建新页面")

                print(f"打印完成，共{multi_layout['total_pages']}页")

            finally:
                painter.end()

        except Exception as e:
            print(f"打印失败: {e}")
            raise

    def _generate_print_page_like_export(self, page_images, page_info):
        """使用与导出功能完全相同的逻辑生成页面图片"""
        try:
            from core.image_processor import ImageProcessor

            # 创建图片处理器
            image_processor = ImageProcessor()

            # 创建A4画布（与导出功能完全相同）
            canvas_img = Image.new('RGB',
                                 (self.layout_engine.a4_width_px, self.layout_engine.a4_height_px),
                                 (255, 255, 255))

            # 处理当前页面的每个图片（与导出功能完全相同）
            positions = page_info['positions']
            for i, image_item in enumerate(page_images):
                if i >= len(positions):
                    break

                try:
                    # 获取圆形图片（与导出功能完全相同）
                    circle_img = image_processor.create_circular_crop(
                        image_item.file_path,
                        image_item.scale,
                        image_item.offset_x,
                        image_item.offset_y,
                        image_item.rotation
                    )

                    # 计算粘贴位置（与导出功能完全相同）
                    center_x, center_y = positions[i]
                    paste_x = center_x - self.layout_engine.badge_radius_px
                    paste_y = center_y - self.layout_engine.badge_radius_px

                    # 粘贴到画布（与导出功能完全相同）
                    if circle_img.mode == 'RGBA':
                        canvas_img.paste(circle_img, (paste_x, paste_y), circle_img)
                    else:
                        canvas_img.paste(circle_img, (paste_x, paste_y))

                except Exception as e:
                    print(f"处理图片失败 {image_item.filename}: {e}")
                    continue

            # 转换PIL图像为QPixmap
            return self._pil_to_qpixmap(canvas_img)

        except Exception as e:
            print(f"生成打印页面失败: {e}")
            return None

    def print_preview(self):
        """打印预览 - 使用系统默认的预览对话框"""
        try:
            # 获取图片列表
            expanded_images = self.get_expanded_image_list()
            if not expanded_images:
                QMessageBox.warning(self, "预览失败", "没有图片可以预览，请先导入图片。")
                return

            # 导入打印预览相关模块
            from PySide6.QtPrintSupport import QPrintPreviewDialog, QPrinter

            # 创建打印机对象并配置
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            self._configure_printer_for_consistency(printer)

            # 创建打印预览对话框
            preview_dialog = QPrintPreviewDialog(printer, self)
            preview_dialog.setWindowTitle("打印预览 - A4排版")

            # 保存图片列表到实例变量，供槽函数使用
            self._current_print_images = expanded_images

            # 连接预览信号，使用简单的绘制函数
            preview_dialog.paintRequested.connect(self._simple_paint_for_preview)

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
            traceback.print_exc()

    def _simple_paint_for_preview(self, printer):
        """简单的预览绘制函数 - 与打印使用相同的逻辑"""
        try:
            expanded_images = getattr(self, '_current_print_images', [])
            print(f"开始预览绘制，图片数量: {len(expanded_images)}")

            # 直接使用简单打印函数的逻辑
            self._simple_print_to_printer(printer, expanded_images)

        except Exception as e:
            print(f"预览绘制失败: {e}")
            traceback.print_exc()



    def _pil_to_qpixmap(self, pil_image):
        """将PIL图片转换为QPixmap"""
        try:
            # 将PIL图片保存到字节流
            buffer = BytesIO()
            try:
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
            finally:
                # 确保释放内存
                buffer.close()

        except Exception as e:
            print(f"PIL到QPixmap转换失败: {e}")
            # 返回空白pixmap
            blank_pixmap = QPixmap(100, 100)
            blank_pixmap.fill()
            return blank_pixmap






    def render_to_printer(self, printer, expanded_images):
        """将A4排版渲染到打印机（兼容旧接口）"""
        # 使用简单打印函数
        self._simple_print_to_printer(printer, expanded_images)

    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于",
            f"{APP_TITLE} v{APP_VERSION}\n\n"
            "专业的徽章图案制作工具\n"
            "支持图片裁剪和A4排版\n\n"
            "开发者: 喵喵mya\n"
            "邮箱: 231750570@qq.com\n"
            "GitHub: https://github.com/fenglyu1314/BadgePatternTool\n\n"
            "基于PySide6开发\n"
            "版权所有 © 2025 喵喵mya"
        )
