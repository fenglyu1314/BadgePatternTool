"""
图片列表面板模块
负责图片列表的显示和管理
"""

import os
from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, 
    QListWidget, QListWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt, QSize, pyqtSignal
from PySide6.QtGui import QPixmap

from utils.file_handler import FileHandler, ImageItem


class ImageListPanel(QGroupBox):
    """图片列表面板类"""
    
    # 信号定义
    image_selected = pyqtSignal(object)  # 图片选择信号
    images_changed = pyqtSignal()  # 图片列表变化信号
    
    def __init__(self, parent=None):
        super().__init__("图片列表", parent)
        
        # 初始化组件
        self.file_handler = FileHandler()
        self.image_items = []
        self.current_selection = None
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 导入按钮
        self.import_btn = QPushButton("导入图片")
        layout.addWidget(self.import_btn)
        
        # 图片列表
        self.image_listbox = QListWidget()
        self.setup_listbox()
        layout.addWidget(self.image_listbox)
        
        # 操作按钮
        self.create_action_buttons(layout)
    
    def setup_listbox(self):
        """设置列表框"""
        # 设置列表显示模式和样式
        self.image_listbox.setViewMode(QListWidget.ListMode)
        self.image_listbox.setIconSize(QSize(48, 48))
        self.image_listbox.setSpacing(2)
        self.image_listbox.setUniformItemSizes(True)
        
        # 启用拖拽功能
        self.image_listbox.setAcceptDrops(True)
        self.image_listbox.setDragDropMode(QListWidget.DropOnly)
    
    def create_action_buttons(self, layout):
        """创建操作按钮"""
        btn_layout = QHBoxLayout()
        
        self.copy_btn = QPushButton("复制")
        self.delete_btn = QPushButton("删除")
        self.clear_btn = QPushButton("清空")
        
        btn_layout.addWidget(self.copy_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.clear_btn)
        
        layout.addLayout(btn_layout)
    
    def setup_connections(self):
        """设置信号连接"""
        self.import_btn.clicked.connect(self.import_images)
        self.copy_btn.clicked.connect(self.copy_selected)
        self.delete_btn.clicked.connect(self.delete_selected)
        self.clear_btn.clicked.connect(self.clear_all)
        self.image_listbox.itemSelectionChanged.connect(self.on_selection_changed)
    
    def import_images(self):
        """导入图片"""
        try:
            new_items = self.file_handler.import_images_dialog()
            if new_items:
                self.image_items.extend(new_items)
                self.update_image_list()
                self.images_changed.emit()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入图片失败: {e}")
    
    def copy_selected(self):
        """复制选中的图片"""
        if self.current_selection:
            # 创建副本
            new_item = ImageItem(
                self.current_selection.file_path,
                self.current_selection.filename
            )
            new_item.scale = self.current_selection.scale
            new_item.offset_x = self.current_selection.offset_x
            new_item.offset_y = self.current_selection.offset_y
            new_item.rotation = self.current_selection.rotation
            new_item.quantity = self.current_selection.quantity
            
            self.image_items.append(new_item)
            self.update_image_list()
            self.images_changed.emit()
    
    def delete_selected(self):
        """删除选中的图片"""
        if self.current_selection and self.current_selection in self.image_items:
            self.image_items.remove(self.current_selection)
            self.current_selection = None
            self.update_image_list()
            self.images_changed.emit()
    
    def clear_all(self):
        """清空所有图片"""
        if self.image_items:
            reply = QMessageBox.question(
                self, "确认", "确定要清空所有图片吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.image_items.clear()
                self.current_selection = None
                self.update_image_list()
                self.images_changed.emit()
    
    def on_selection_changed(self):
        """处理选择变化"""
        current_item = self.image_listbox.currentItem()
        if current_item:
            index = self.image_listbox.row(current_item)
            if 0 <= index < len(self.image_items):
                self.current_selection = self.image_items[index]
                self.image_selected.emit(self.current_selection)
        else:
            self.current_selection = None
            self.image_selected.emit(None)
    
    def update_image_list(self):
        """更新图片列表显示"""
        self.image_listbox.clear()
        
        for i, item in enumerate(self.image_items):
            # 创建列表项
            list_item = QListWidgetItem()
            
            # 设置显示文本
            display_text = f"{item.filename}"
            if item.quantity > 1:
                display_text += f" (x{item.quantity})"
            list_item.setText(display_text)
            
            # 设置缩略图
            try:
                thumbnail = self.file_handler.create_thumbnail(item.file_path, (48, 48))
                if thumbnail:
                    list_item.setIcon(thumbnail)
            except Exception as e:
                print(f"创建缩略图失败: {e}")
            
            self.image_listbox.addItem(list_item)
    
    def get_image_items(self):
        """获取图片项目列表"""
        return self.image_items
    
    def set_image_items(self, items):
        """设置图片项目列表"""
        self.image_items = items
        self.update_image_list()
    
    def get_current_selection(self):
        """获取当前选择的图片"""
        return self.current_selection
