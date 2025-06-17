"""
主窗口界面模块 - PySide6版本
实现BadgePatternTool的主界面布局
"""

import sys
import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QListWidget, QTabWidget, QFrame,
    QSlider, QRadioButton, QComboBox, QButtonGroup,
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
        list_frame.setFixedWidth(250)
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
        layout = QVBoxLayout(self.edit_tab)
        
        # 临时标签
        label = QLabel("单图编辑功能开发中...")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
    def create_layout_area(self):
        """创建A4排版预览区域"""
        layout = QVBoxLayout(self.layout_tab)
        
        # 临时标签
        label = QLabel("A4排版预览功能开发中...")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
    # 事件处理方法
    def import_images(self):
        """导入图片"""
        QMessageBox.information(self, "提示", "导入图片功能开发中...")
        
    def export_pdf(self):
        """导出PDF"""
        QMessageBox.information(self, "提示", "导出PDF功能开发中...")
        
    def export_png(self):
        """导出PNG"""
        QMessageBox.information(self, "提示", "导出PNG功能开发中...")
        
    def export_file(self):
        """导出文件"""
        format_type = self.format_combo.currentText()
        QMessageBox.information(self, "提示", f"导出{format_type.upper()}功能开发中...")
        
    def select_all(self):
        """全选"""
        QMessageBox.information(self, "提示", "全选功能开发中...")
        
    def clear_all(self):
        """清空列表"""
        if self.image_items:
            reply = QMessageBox.question(self, "确认", "确定要清空所有图片吗？")
            if reply == QMessageBox.Yes:
                self.image_items.clear()
                self.image_listbox.clear()
                self.current_selection = None
                self.status_bar.showMessage("已清空图片列表")
        
    def delete_selected(self):
        """删除选中项"""
        current_row = self.image_listbox.currentRow()
        if current_row >= 0:
            self.image_listbox.takeItem(current_row)
            if current_row < len(self.image_items):
                deleted_item = self.image_items.pop(current_row)
                self.status_bar.showMessage(f"已删除: {deleted_item.get_display_name()}")
        
    def refresh_preview(self):
        """刷新预览"""
        QMessageBox.information(self, "提示", "刷新预览功能开发中...")
        
    def on_image_select(self):
        """图片选择事件"""
        current_row = self.image_listbox.currentRow()
        if current_row >= 0 and current_row < len(self.image_items):
            self.current_selection = self.image_items[current_row]
            self.status_bar.showMessage(f"已选择: {self.current_selection.get_display_name()}")
        else:
            self.current_selection = None
            
    def set_layout_mode(self, mode):
        """设置布局模式"""
        self.layout_mode = mode
        self.status_bar.showMessage(f"布局模式: {'网格排列' if mode == 'grid' else '紧密排列'}")
        
    def on_spacing_change(self, value):
        """间距改变事件"""
        self.spacing_value = value
        self.status_bar.showMessage(f"间距设置: {value}mm")
        
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于",
            f"{APP_TITLE} v{APP_VERSION}\n\n"
            "徽章图案制作工具\n"
            "支持图片裁剪和A4排版\n\n"
            "开发中..."
        )
