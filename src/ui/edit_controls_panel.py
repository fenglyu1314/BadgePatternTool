"""
编辑控制面板模块
负责单图编辑的控制界面
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QSlider, QLabel, QSpinBox, QGroupBox
)
from PySide6.QtCore import Qt, pyqtSignal


class EditControlsPanel(QWidget):
    """编辑控制面板类"""
    
    # 信号定义
    scale_changed = pyqtSignal(float)  # 缩放变化
    offset_changed = pyqtSignal(int, int)  # 偏移变化
    rotation_changed = pyqtSignal(int)  # 旋转变化
    quantity_changed = pyqtSignal(int)  # 数量变化
    reset_requested = pyqtSignal()  # 重置请求
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化状态
        self.scale_value = 1.0
        self.offset_x_value = 0
        self.offset_y_value = 0
        self.rotation_value = 0
        self.quantity_value = 1
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 缩放控制
        self.create_scale_controls(layout)
        
        # 位置控制
        self.create_position_controls(layout)
        
        # 旋转控制
        self.create_rotation_controls(layout)
        
        # 数量控制
        self.create_quantity_controls(layout)
        
        # 操作按钮
        self.create_action_buttons(layout)
    
    def create_scale_controls(self, parent_layout):
        """创建缩放控制"""
        self.scale_label = QLabel("图片缩放: 1.0")
        self.scale_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        parent_layout.addWidget(self.scale_label)
        
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(10, 500)  # 0.1x 到 5.0x
        self.scale_slider.setValue(100)  # 1.0x
        parent_layout.addWidget(self.scale_slider)
    
    def create_position_controls(self, parent_layout):
        """创建位置控制"""
        position_group = QGroupBox("位置调整")
        parent_layout.addWidget(position_group)
        
        layout = QVBoxLayout(position_group)
        
        # X轴偏移
        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel("X偏移:"))
        
        self.offset_x_label = QLabel("0px")
        self.offset_x_label.setMinimumWidth(40)
        x_layout.addWidget(self.offset_x_label)
        
        self.offset_x_slider = QSlider(Qt.Horizontal)
        self.offset_x_slider.setRange(-200, 200)
        self.offset_x_slider.setValue(0)
        x_layout.addWidget(self.offset_x_slider)
        
        layout.addLayout(x_layout)
        
        # Y轴偏移
        y_layout = QHBoxLayout()
        y_layout.addWidget(QLabel("Y偏移:"))
        
        self.offset_y_label = QLabel("0px")
        self.offset_y_label.setMinimumWidth(40)
        y_layout.addWidget(self.offset_y_label)
        
        self.offset_y_slider = QSlider(Qt.Horizontal)
        self.offset_y_slider.setRange(-200, 200)
        self.offset_y_slider.setValue(0)
        y_layout.addWidget(self.offset_y_slider)
        
        layout.addLayout(y_layout)
    
    def create_rotation_controls(self, parent_layout):
        """创建旋转控制"""
        rotation_layout = QHBoxLayout()
        rotation_layout.addWidget(QLabel("旋转:"))
        
        self.rotation_label = QLabel("0°")
        self.rotation_label.setMinimumWidth(30)
        rotation_layout.addWidget(self.rotation_label)
        
        self.rotation_slider = QSlider(Qt.Horizontal)
        self.rotation_slider.setRange(-180, 180)
        self.rotation_slider.setValue(0)
        rotation_layout.addWidget(self.rotation_slider)
        
        parent_layout.addLayout(rotation_layout)
    
    def create_quantity_controls(self, parent_layout):
        """创建数量控制"""
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("数量:"))
        
        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setRange(1, 50)
        self.quantity_spinbox.setValue(1)
        quantity_layout.addWidget(self.quantity_spinbox)
        
        parent_layout.addLayout(quantity_layout)
    
    def create_action_buttons(self, parent_layout):
        """创建操作按钮"""
        button_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("重置")
        self.apply_btn = QPushButton("应用")
        
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.apply_btn)
        
        parent_layout.addLayout(button_layout)
    
    def setup_connections(self):
        """设置信号连接"""
        # 滑块连接
        self.scale_slider.valueChanged.connect(self.on_scale_changed)
        self.offset_x_slider.valueChanged.connect(self.on_offset_x_changed)
        self.offset_y_slider.valueChanged.connect(self.on_offset_y_changed)
        self.rotation_slider.valueChanged.connect(self.on_rotation_changed)
        
        # 数量控制
        self.quantity_spinbox.valueChanged.connect(self.on_quantity_changed)
        
        # 按钮连接
        self.reset_btn.clicked.connect(self.reset_controls)
        self.apply_btn.clicked.connect(self.apply_changes)
    
    def on_scale_changed(self, value):
        """处理缩放变化"""
        self.scale_value = value / 100.0
        self.scale_label.setText(f"图片缩放: {self.scale_value:.1f}")
        self.scale_changed.emit(self.scale_value)
    
    def on_offset_x_changed(self, value):
        """处理X偏移变化"""
        self.offset_x_value = value
        self.offset_x_label.setText(f"{value}px")
        self.offset_changed.emit(self.offset_x_value, self.offset_y_value)
    
    def on_offset_y_changed(self, value):
        """处理Y偏移变化"""
        self.offset_y_value = value
        self.offset_y_label.setText(f"{value}px")
        self.offset_changed.emit(self.offset_x_value, self.offset_y_value)
    
    def on_rotation_changed(self, value):
        """处理旋转变化"""
        self.rotation_value = value
        self.rotation_label.setText(f"{value}°")
        self.rotation_changed.emit(value)
    
    def on_quantity_changed(self, value):
        """处理数量变化"""
        self.quantity_value = value
        self.quantity_changed.emit(value)
    
    def reset_controls(self):
        """重置所有控制"""
        self.scale_slider.setValue(100)
        self.offset_x_slider.setValue(0)
        self.offset_y_slider.setValue(0)
        self.rotation_slider.setValue(0)
        self.quantity_spinbox.setValue(1)
        self.reset_requested.emit()
    
    def apply_changes(self):
        """应用所有变化"""
        # 发送所有当前值的信号
        self.scale_changed.emit(self.scale_value)
        self.offset_changed.emit(self.offset_x_value, self.offset_y_value)
        self.rotation_changed.emit(self.rotation_value)
        self.quantity_changed.emit(self.quantity_value)
    
    def update_from_image_item(self, image_item):
        """从图片项更新控制值"""
        if image_item:
            # 更新滑块值（不触发信号）
            self.scale_slider.blockSignals(True)
            self.offset_x_slider.blockSignals(True)
            self.offset_y_slider.blockSignals(True)
            self.rotation_slider.blockSignals(True)
            self.quantity_spinbox.blockSignals(True)
            
            self.scale_slider.setValue(int(image_item.scale * 100))
            self.offset_x_slider.setValue(image_item.offset_x)
            self.offset_y_slider.setValue(image_item.offset_y)
            self.rotation_slider.setValue(image_item.rotation)
            self.quantity_spinbox.setValue(image_item.quantity)
            
            # 重新启用信号
            self.scale_slider.blockSignals(False)
            self.offset_x_slider.blockSignals(False)
            self.offset_y_slider.blockSignals(False)
            self.rotation_slider.blockSignals(False)
            self.quantity_spinbox.blockSignals(False)
            
            # 更新显示标签
            self.scale_value = image_item.scale
            self.offset_x_value = image_item.offset_x
            self.offset_y_value = image_item.offset_y
            self.rotation_value = image_item.rotation
            self.quantity_value = image_item.quantity
            
            self.scale_label.setText(f"图片缩放: {self.scale_value:.1f}")
            self.offset_x_label.setText(f"{self.offset_x_value}px")
            self.offset_y_label.setText(f"{self.offset_y_value}px")
            self.rotation_label.setText(f"{self.rotation_value}°")
    
    def get_current_values(self):
        """获取当前所有值"""
        return {
            'scale': self.scale_value,
            'offset_x': self.offset_x_value,
            'offset_y': self.offset_y_value,
            'rotation': self.rotation_value,
            'quantity': self.quantity_value
        }
