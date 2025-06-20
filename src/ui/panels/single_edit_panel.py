"""
单图编辑面板
负责单个图片的交互式编辑
"""

from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, 
    QSlider, QPushButton
)
from PySide6.QtCore import Qt, Signal

from common.error_handler import logger
from utils.config import app_config


class SingleEditPanel(QGroupBox):
    """单图编辑面板类"""
    
    # 信号定义
    parameters_changed = Signal(object)  # 编辑参数变化信号
    opacity_changed = Signal(str, int)   # 透明度变化信号
    
    def __init__(self, parent=None):
        super().__init__("单图编辑区", parent)
        self.current_editor = None
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        
        # 交互式图片编辑器
        from ui.interactive_image_editor import InteractiveImageEditor
        self.interactive_editor = InteractiveImageEditor()
        self.interactive_editor.setFixedSize(320, 320)
        layout.addWidget(self.interactive_editor)
        
        # 更新遮罩半径以匹配配置
        self.interactive_editor.update_mask_radius()
        
        # 编辑控制区域
        self.create_edit_controls(layout)
    
    def create_edit_controls(self, parent_layout):
        """创建编辑控制区域"""
        # 遮罩透明度设置
        mask_group = QGroupBox("遮罩设置")
        parent_layout.addWidget(mask_group)
        
        mask_layout = QVBoxLayout(mask_group)
        
        # 外部区域透明度
        outside_layout = QHBoxLayout()
        outside_layout.addWidget(QLabel("外部区域:"))
        
        self.outside_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.outside_opacity_slider.setRange(0, 100)
        self.outside_opacity_slider.setValue(app_config.outside_opacity)
        outside_layout.addWidget(self.outside_opacity_slider)
        
        self.outside_opacity_label = QLabel(f"{app_config.outside_opacity}%")
        self.outside_opacity_label.setMinimumWidth(35)
        outside_layout.addWidget(self.outside_opacity_label)
        
        mask_layout.addLayout(outside_layout)
        
        # 出血区透明度
        bleed_opacity_layout = QHBoxLayout()
        bleed_opacity_layout.addWidget(QLabel("出血区:"))
        
        self.bleed_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.bleed_opacity_slider.setRange(0, 100)
        self.bleed_opacity_slider.setValue(app_config.bleed_opacity)
        bleed_opacity_layout.addWidget(self.bleed_opacity_slider)
        
        self.bleed_opacity_label = QLabel(f"{app_config.bleed_opacity}%")
        self.bleed_opacity_label.setMinimumWidth(35)
        bleed_opacity_layout.addWidget(self.bleed_opacity_label)
        
        mask_layout.addLayout(bleed_opacity_layout)
        
        # 缩放控制
        self.scale_label = QLabel("缩放: 1.00x")
        self.scale_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        parent_layout.addWidget(self.scale_label)
        
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(10, 1000)  # 0.1 到 10.0
        self.scale_slider.setValue(100)  # 1.0
        parent_layout.addWidget(self.scale_slider)
        
        # X轴偏移控制
        self.offset_x_label = QLabel("水平偏移: 0px")
        self.offset_x_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        parent_layout.addWidget(self.offset_x_label)
        
        self.offset_x_slider = QSlider(Qt.Orientation.Horizontal)
        self.offset_x_slider.setRange(-100, 100)
        self.offset_x_slider.setValue(0)
        parent_layout.addWidget(self.offset_x_slider)
        
        # Y轴偏移控制
        self.offset_y_label = QLabel("垂直偏移: 0px")
        self.offset_y_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        parent_layout.addWidget(self.offset_y_label)
        
        self.offset_y_slider = QSlider(Qt.Orientation.Horizontal)
        self.offset_y_slider.setRange(-100, 100)
        self.offset_y_slider.setValue(0)
        parent_layout.addWidget(self.offset_y_slider)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        self.fit_btn = QPushButton("适应大小")
        btn_layout.addWidget(self.fit_btn)
        
        self.reset_btn = QPushButton("重置")
        btn_layout.addWidget(self.reset_btn)
        
        parent_layout.addLayout(btn_layout)
    
    def setup_connections(self):
        """设置信号连接"""
        # 交互式编辑器信号
        self.interactive_editor.parameters_changed.connect(self.on_editor_parameters_changed)
        
        # 透明度滑块信号
        self.outside_opacity_slider.valueChanged.connect(self.on_outside_opacity_change)
        self.bleed_opacity_slider.valueChanged.connect(self.on_bleed_opacity_change)
        
        # 编辑控制信号
        self.scale_slider.valueChanged.connect(self.on_scale_change)
        self.offset_x_slider.valueChanged.connect(self.on_position_change)
        self.offset_y_slider.valueChanged.connect(self.on_position_change)
        
        # 按钮信号
        self.fit_btn.clicked.connect(self.fit_to_circle)
        self.reset_btn.clicked.connect(self.reset_parameters)
    
    def on_editor_parameters_changed(self, editor):
        """编辑器参数变化事件"""
        self.current_editor = editor
        if editor:
            # 更新滑块值（不触发信号）
            self.scale_slider.blockSignals(True)
            self.offset_x_slider.blockSignals(True)
            self.offset_y_slider.blockSignals(True)
            
            self.scale_slider.setValue(int(editor.scale * 100))
            self.offset_x_slider.setValue(editor.offset_x)
            self.offset_y_slider.setValue(editor.offset_y)
            
            self.scale_slider.blockSignals(False)
            self.offset_x_slider.blockSignals(False)
            self.offset_y_slider.blockSignals(False)
            
            # 更新标签
            self.update_labels()
        
        self.parameters_changed.emit(editor)
    
    def on_outside_opacity_change(self, value):
        """外部区域透明度变化"""
        app_config.outside_opacity = value
        self.outside_opacity_label.setText(f"{value}%")
        self.opacity_changed.emit("outside", value)
        logger.debug(f"外部区域透明度设置为: {value}%")
    
    def on_bleed_opacity_change(self, value):
        """出血区透明度变化"""
        app_config.bleed_opacity = value
        self.bleed_opacity_label.setText(f"{value}%")
        self.opacity_changed.emit("bleed", value)
        logger.debug(f"出血区透明度设置为: {value}%")
    
    def on_scale_change(self, value):
        """缩放变化事件"""
        if self.current_editor:
            scale = value / 100.0
            self.current_editor.set_scale(scale)
            self.update_labels()
            self.interactive_editor.update_preview()
    
    def on_position_change(self):
        """位置变化事件"""
        if self.current_editor:
            offset_x = self.offset_x_slider.value()
            offset_y = self.offset_y_slider.value()
            self.current_editor.set_offset(offset_x, offset_y)
            self.update_labels()
            self.interactive_editor.update_preview()
    
    def fit_to_circle(self):
        """适应圆形大小"""
        if self.current_editor:
            self.current_editor.reset_to_optimal()
            self.update_sliders()
            self.interactive_editor.update_preview()
    
    def reset_parameters(self):
        """重置参数"""
        if self.current_editor:
            self.current_editor.scale = 1.0
            self.current_editor.offset_x = 0
            self.current_editor.offset_y = 0
            self.update_sliders()
            self.interactive_editor.update_preview()
    
    def update_sliders(self):
        """更新滑块值"""
        if self.current_editor:
            self.scale_slider.blockSignals(True)
            self.offset_x_slider.blockSignals(True)
            self.offset_y_slider.blockSignals(True)
            
            self.scale_slider.setValue(int(self.current_editor.scale * 100))
            self.offset_x_slider.setValue(self.current_editor.offset_x)
            self.offset_y_slider.setValue(self.current_editor.offset_y)
            
            self.scale_slider.blockSignals(False)
            self.offset_x_slider.blockSignals(False)
            self.offset_y_slider.blockSignals(False)
            
            self.update_labels()
    
    def update_labels(self):
        """更新标签显示"""
        if self.current_editor:
            self.scale_label.setText(f"缩放: {self.current_editor.scale:.2f}x")
            self.offset_x_label.setText(f"水平偏移: {self.current_editor.offset_x}px")
            self.offset_y_label.setText(f"垂直偏移: {self.current_editor.offset_y}px")
    
    def set_image(self, image_path):
        """设置要编辑的图片"""
        self.interactive_editor.set_image(image_path)
    
    def clear_image(self):
        """清空图片"""
        self.interactive_editor.clear_image()
        self.current_editor = None
