"""
控制面板模块
负责排版控制和导出设置
"""

from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, 
    QRadioButton, QButtonGroup, QSlider, QLabel, QComboBox,
    QSpinBox, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, pyqtSignal

from utils.config import (
    DEFAULT_LAYOUT, DEFAULT_SPACING, DEFAULT_MARGIN, 
    DEFAULT_EXPORT_FORMAT, app_config
)


class ControlPanel(QGroupBox):
    """控制面板类"""
    
    # 信号定义
    layout_mode_changed = pyqtSignal(str)  # 布局模式变化
    spacing_changed = pyqtSignal(float)  # 间距变化
    margin_changed = pyqtSignal(float)  # 页边距变化
    diameter_changed = pyqtSignal(int)  # 直径变化
    export_requested = pyqtSignal()  # 导出请求
    print_requested = pyqtSignal()  # 打印请求
    auto_layout_requested = pyqtSignal()  # 自动排版请求
    
    def __init__(self, parent=None):
        super().__init__("排版控制", parent)
        
        # 初始化状态
        self.layout_mode = DEFAULT_LAYOUT
        self.spacing_value = DEFAULT_SPACING
        self.margin_value = DEFAULT_MARGIN
        self.export_format = DEFAULT_EXPORT_FORMAT.lower()
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 布局模式
        self.create_layout_mode_group(layout)
        
        # 间距控制
        self.create_spacing_group(layout)
        
        # 页边距控制
        self.create_margin_group(layout)
        
        # 圆形尺寸设置
        self.create_size_group(layout)
        
        # 导出设置
        self.create_export_group(layout)
        
        # 添加弹性空间
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
    
    def create_layout_mode_group(self, parent_layout):
        """创建布局模式组"""
        layout_mode_group = QGroupBox("排列模式")
        parent_layout.addWidget(layout_mode_group)
        
        layout = QVBoxLayout(layout_mode_group)
        
        self.layout_button_group = QButtonGroup()
        
        self.grid_radio = QRadioButton("网格排列")
        self.grid_radio.setChecked(DEFAULT_LAYOUT == "grid")
        self.layout_button_group.addButton(self.grid_radio)
        layout.addWidget(self.grid_radio)
        
        self.compact_radio = QRadioButton("紧密排列")
        self.compact_radio.setChecked(DEFAULT_LAYOUT == "compact")
        self.layout_button_group.addButton(self.compact_radio)
        layout.addWidget(self.compact_radio)
    
    def create_spacing_group(self, parent_layout):
        """创建间距控制组"""
        spacing_group = QGroupBox("间距设置")
        parent_layout.addWidget(spacing_group)
        
        layout = QVBoxLayout(spacing_group)
        
        self.spacing_label = QLabel(f"间距: {self.spacing_value}mm")
        layout.addWidget(self.spacing_label)
        
        self.spacing_slider = QSlider(Qt.Horizontal)
        self.spacing_slider.setRange(0, 20)
        self.spacing_slider.setValue(int(self.spacing_value))
        layout.addWidget(self.spacing_slider)
    
    def create_margin_group(self, parent_layout):
        """创建页边距控制组"""
        margin_group = QGroupBox("页边距")
        parent_layout.addWidget(margin_group)
        
        layout = QVBoxLayout(margin_group)
        
        self.margin_label = QLabel(f"边距: {self.margin_value}mm")
        layout.addWidget(self.margin_label)
        
        self.margin_slider = QSlider(Qt.Horizontal)
        self.margin_slider.setRange(0, 30)
        self.margin_slider.setValue(int(self.margin_value))
        layout.addWidget(self.margin_slider)
    
    def create_size_group(self, parent_layout):
        """创建尺寸设置组"""
        size_group = QGroupBox("圆形尺寸")
        parent_layout.addWidget(size_group)
        
        layout = QVBoxLayout(size_group)
        
        # 直径设置
        diameter_layout = QHBoxLayout()
        diameter_layout.addWidget(QLabel("直径:"))
        
        self.diameter_spinbox = QSpinBox()
        self.diameter_spinbox.setRange(10, 100)
        self.diameter_spinbox.setValue(int(app_config.badge_diameter_mm))
        self.diameter_spinbox.setSuffix("mm")
        diameter_layout.addWidget(self.diameter_spinbox)
        
        layout.addLayout(diameter_layout)
        
        # 预设按钮
        self.create_preset_buttons(layout)
    
    def create_preset_buttons(self, parent_layout):
        """创建预设按钮"""
        preset_layout = QHBoxLayout()
        
        self.btn_25 = QPushButton("25mm")
        self.btn_32 = QPushButton("32mm")
        self.btn_58 = QPushButton("58mm")
        self.btn_68 = QPushButton("68mm")
        
        preset_layout.addWidget(self.btn_25)
        preset_layout.addWidget(self.btn_32)
        preset_layout.addWidget(self.btn_58)
        preset_layout.addWidget(self.btn_68)
        
        parent_layout.addLayout(preset_layout)
    
    def create_export_group(self, parent_layout):
        """创建导出设置组"""
        export_group = QGroupBox("导出设置")
        parent_layout.addWidget(export_group)
        
        layout = QVBoxLayout(export_group)
        
        # 导出格式
        layout.addWidget(QLabel("输出格式:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["pdf", "png", "jpg"])
        
        # 设置默认选择
        default_index = self.format_combo.findText(DEFAULT_EXPORT_FORMAT.lower())
        if default_index >= 0:
            self.format_combo.setCurrentIndex(default_index)
        layout.addWidget(self.format_combo)
        
        # 功能按钮
        self.auto_layout_btn = QPushButton("自动排版")
        layout.addWidget(self.auto_layout_btn)
        
        self.export_btn = QPushButton("导出文件")
        layout.addWidget(self.export_btn)
        
        self.print_btn = QPushButton("打印")
        self.print_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        layout.addWidget(self.print_btn)
    
    def setup_connections(self):
        """设置信号连接"""
        # 布局模式
        self.grid_radio.toggled.connect(lambda checked: self.on_layout_mode_changed("grid") if checked else None)
        self.compact_radio.toggled.connect(lambda checked: self.on_layout_mode_changed("compact") if checked else None)
        
        # 滑块
        self.spacing_slider.valueChanged.connect(self.on_spacing_changed)
        self.margin_slider.valueChanged.connect(self.on_margin_changed)
        
        # 直径设置
        self.diameter_spinbox.valueChanged.connect(self.on_diameter_changed)
        
        # 预设按钮
        self.btn_25.clicked.connect(lambda: self.set_diameter(25))
        self.btn_32.clicked.connect(lambda: self.set_diameter(32))
        self.btn_58.clicked.connect(lambda: self.set_diameter(58))
        self.btn_68.clicked.connect(lambda: self.set_diameter(68))
        
        # 功能按钮
        self.auto_layout_btn.clicked.connect(self.auto_layout_requested.emit)
        self.export_btn.clicked.connect(self.export_requested.emit)
        self.print_btn.clicked.connect(self.print_requested.emit)
    
    def on_layout_mode_changed(self, mode):
        """处理布局模式变化"""
        self.layout_mode = mode
        self.layout_mode_changed.emit(mode)
    
    def on_spacing_changed(self, value):
        """处理间距变化"""
        self.spacing_value = float(value)
        self.spacing_label.setText(f"间距: {self.spacing_value}mm")
        self.spacing_changed.emit(self.spacing_value)
    
    def on_margin_changed(self, value):
        """处理页边距变化"""
        self.margin_value = float(value)
        self.margin_label.setText(f"边距: {self.margin_value}mm")
        self.margin_changed.emit(self.margin_value)
    
    def on_diameter_changed(self, value):
        """处理直径变化"""
        self.diameter_changed.emit(value)
    
    def set_diameter(self, diameter):
        """设置直径"""
        self.diameter_spinbox.setValue(diameter)
    
    def get_export_format(self):
        """获取导出格式"""
        return self.format_combo.currentText()
    
    def get_layout_mode(self):
        """获取布局模式"""
        return self.layout_mode
    
    def get_spacing(self):
        """获取间距"""
        return self.spacing_value
    
    def get_margin(self):
        """获取页边距"""
        return self.margin_value
