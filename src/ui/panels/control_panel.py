"""
控制面板
负责排版控制和导出设置
"""

from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, 
    QSlider, QPushButton, QRadioButton, QButtonGroup,
    QSpinBox, QComboBox, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from common.constants import (
    DEFAULT_LAYOUT, DEFAULT_EXPORT_FORMAT, 
    DEFAULT_SPACING_MM, DEFAULT_MARGIN_MM
)
from common.error_handler import logger
from utils.config import app_config


class ControlPanel(QGroupBox):
    """控制面板类"""
    
    # 信号定义
    layout_mode_changed = Signal(str)      # 布局模式变化
    spacing_changed = Signal(int)          # 间距变化
    margin_changed = Signal(int)           # 页边距变化
    badge_size_changed = Signal(int)       # 徽章尺寸变化
    bleed_size_changed = Signal(int)       # 出血尺寸变化
    export_requested = Signal(str)         # 导出请求
    print_requested = Signal()             # 打印请求
    auto_layout_requested = Signal()       # 自动排版请求
    
    def __init__(self, parent=None):
        super().__init__("排版控制", parent)
        
        # 初始化状态
        self.layout_mode = DEFAULT_LAYOUT
        self.spacing_value = DEFAULT_SPACING_MM
        self.margin_value = DEFAULT_MARGIN_MM
        self.export_format = DEFAULT_EXPORT_FORMAT.lower()
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        
        # 布局模式
        self.create_layout_mode_group(layout)
        
        # 间距控制
        self.create_spacing_group(layout)
        
        # 页边距控制
        self.create_margin_group(layout)
        
        # 徽章尺寸设置
        self.create_badge_size_group(layout)
        
        # 导出设置
        self.create_export_group(layout)
        
        # 添加弹性空间
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
    
    def create_layout_mode_group(self, parent_layout):
        """创建布局模式组"""
        layout_mode_group = QGroupBox("排列模式")
        parent_layout.addWidget(layout_mode_group)
        
        layout_mode_layout = QVBoxLayout(layout_mode_group)
        
        self.layout_button_group = QButtonGroup()
        
        self.grid_radio = QRadioButton("网格排列")
        self.grid_radio.setChecked(DEFAULT_LAYOUT == "grid")
        self.layout_button_group.addButton(self.grid_radio)
        layout_mode_layout.addWidget(self.grid_radio)
        
        self.compact_radio = QRadioButton("紧密排列")
        self.compact_radio.setChecked(DEFAULT_LAYOUT == "compact")
        self.layout_button_group.addButton(self.compact_radio)
        layout_mode_layout.addWidget(self.compact_radio)
    
    def create_spacing_group(self, parent_layout):
        """创建间距控制组"""
        spacing_group = QGroupBox("间距设置")
        parent_layout.addWidget(spacing_group)
        
        spacing_layout = QVBoxLayout(spacing_group)
        
        self.spacing_label = QLabel(f"间距: {self.spacing_value}mm")
        spacing_layout.addWidget(self.spacing_label)
        
        self.spacing_slider = QSlider(Qt.Orientation.Horizontal)
        self.spacing_slider.setRange(0, 20)
        self.spacing_slider.setValue(int(self.spacing_value))
        spacing_layout.addWidget(self.spacing_slider)
    
    def create_margin_group(self, parent_layout):
        """创建页边距控制组"""
        margin_group = QGroupBox("页边距")
        parent_layout.addWidget(margin_group)
        
        margin_layout = QVBoxLayout(margin_group)
        
        self.margin_label = QLabel(f"边距: {self.margin_value}mm")
        margin_layout.addWidget(self.margin_label)
        
        self.margin_slider = QSlider(Qt.Orientation.Horizontal)
        self.margin_slider.setRange(5, 30)  # 最小5mm（打印机限制），最大30mm
        self.margin_slider.setValue(int(self.margin_value))
        margin_layout.addWidget(self.margin_slider)
    
    def create_badge_size_group(self, parent_layout):
        """创建徽章尺寸设置组"""
        size_group = QGroupBox("徽章尺寸")
        parent_layout.addWidget(size_group)
        
        size_layout = QVBoxLayout(size_group)
        
        # 徽章尺寸设置
        badge_layout = QHBoxLayout()
        badge_layout.addWidget(QLabel("徽章:"))
        
        self.badge_size_spinbox = QSpinBox()
        self.badge_size_spinbox.setRange(10, 100)  # 10-100mm，支持75mm
        self.badge_size_spinbox.setValue(int(app_config.badge_size_mm))
        self.badge_size_spinbox.setSuffix("mm")
        badge_layout.addWidget(self.badge_size_spinbox)
        
        size_layout.addLayout(badge_layout)
        
        # 出血半径设置
        bleed_layout = QHBoxLayout()
        bleed_layout.addWidget(QLabel("出血半径:"))
        
        self.bleed_size_spinbox = QSpinBox()
        self.bleed_size_spinbox.setRange(0, 10)  # 0-10mm（半径）
        self.bleed_size_spinbox.setValue(int(app_config.bleed_size_mm))
        self.bleed_size_spinbox.setSuffix("mm")
        bleed_layout.addWidget(self.bleed_size_spinbox)
        
        size_layout.addLayout(bleed_layout)
        
        # 总直径显示
        self.total_diameter_label = QLabel(f"总直径: {app_config.badge_diameter_mm}mm")
        self.total_diameter_label.setStyleSheet("font-weight: bold; color: #666;")
        size_layout.addWidget(self.total_diameter_label)
        
        # 预设按钮
        preset_layout = QHBoxLayout()
        
        self.btn_32 = QPushButton("32+5")
        preset_layout.addWidget(self.btn_32)
        
        self.btn_58 = QPushButton("58+5")
        preset_layout.addWidget(self.btn_58)
        
        self.btn_75 = QPushButton("75+5")
        preset_layout.addWidget(self.btn_75)
        
        size_layout.addLayout(preset_layout)
    
    def create_export_group(self, parent_layout):
        """创建导出设置组"""
        export_group = QGroupBox("导出设置")
        parent_layout.addWidget(export_group)
        
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
        self.auto_layout_btn = QPushButton("自动排版")
        export_layout.addWidget(self.auto_layout_btn)
        
        # 导出按钮
        self.export_btn = QPushButton("导出文件")
        export_layout.addWidget(self.export_btn)
        
        # 打印按钮
        self.print_btn = QPushButton("打印")
        export_layout.addWidget(self.print_btn)
    
    def setup_connections(self):
        """设置信号连接"""
        # 布局模式
        self.grid_radio.toggled.connect(lambda checked: self.set_layout_mode("grid") if checked else None)
        self.compact_radio.toggled.connect(lambda checked: self.set_layout_mode("compact") if checked else None)
        
        # 间距和边距
        self.spacing_slider.valueChanged.connect(self.on_spacing_change)
        self.margin_slider.valueChanged.connect(self.on_margin_change)
        
        # 徽章尺寸
        self.badge_size_spinbox.valueChanged.connect(self.on_badge_size_change)
        self.bleed_size_spinbox.valueChanged.connect(self.on_bleed_size_change)
        
        # 预设按钮
        self.btn_32.clicked.connect(lambda: self.set_badge_preset(32, 5))
        self.btn_58.clicked.connect(lambda: self.set_badge_preset(58, 5))
        self.btn_75.clicked.connect(lambda: self.set_badge_preset(75, 5))
        
        # 导出和打印
        self.auto_layout_btn.clicked.connect(self.auto_layout_requested.emit)
        self.export_btn.clicked.connect(self.export_file)
        self.print_btn.clicked.connect(self.print_requested.emit)
    
    def set_layout_mode(self, mode):
        """设置布局模式"""
        if mode != self.layout_mode:
            self.layout_mode = mode
            self.layout_mode_changed.emit(mode)
            logger.info(f"布局模式切换为: {mode}")
    
    def on_spacing_change(self, value):
        """间距变化事件"""
        self.spacing_value = value
        self.spacing_label.setText(f"间距: {value}mm")
        self.spacing_changed.emit(value)
    
    def on_margin_change(self, value):
        """页边距变化事件"""
        self.margin_value = value
        self.margin_label.setText(f"边距: {value}mm")
        self.margin_changed.emit(value)
    
    def on_badge_size_change(self, value):
        """徽章尺寸变化事件"""
        app_config.badge_size_mm = value
        self.update_total_diameter()
        self.badge_size_changed.emit(value)
    
    def on_bleed_size_change(self, value):
        """出血尺寸变化事件"""
        app_config.bleed_size_mm = value
        self.update_total_diameter()
        self.bleed_size_changed.emit(value)
    
    def set_badge_preset(self, badge_size, bleed_size):
        """设置徽章预设"""
        self.badge_size_spinbox.setValue(badge_size)
        self.bleed_size_spinbox.setValue(bleed_size)
        logger.info(f"设置徽章预设: {badge_size}+{bleed_size}mm")
    
    def update_total_diameter(self):
        """更新总直径显示"""
        total = app_config.badge_diameter_mm
        self.total_diameter_label.setText(f"总直径: {total}mm")
    
    def export_file(self):
        """导出文件"""
        format_name = self.format_combo.currentText()
        self.export_format = format_name
        self.export_requested.emit(format_name)
    
    def get_current_settings(self):
        """获取当前设置"""
        return {
            'layout_mode': self.layout_mode,
            'spacing': self.spacing_value,
            'margin': self.margin_value,
            'export_format': self.export_format
        }
