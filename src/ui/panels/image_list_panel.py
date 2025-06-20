"""
图片列表面板
负责图片的导入、显示和基本操作
"""

from PySide6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, 
    QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon

from common.error_handler import logger, show_error_message
from common.constants import MAX_IMAGE_COUNT


class ImageListPanel(QGroupBox):
    """图片列表面板类"""
    
    # 信号定义
    image_selected = Signal(object)  # 图片选择信号
    images_imported = Signal(list)   # 图片导入信号
    image_copied = Signal(object)    # 图片复制信号
    image_deleted = Signal(object)   # 图片删除信号
    images_cleared = Signal()        # 清空信号
    
    def __init__(self, parent=None):
        super().__init__("图片列表", parent)
        self.image_items = []  # 存储ImageItem对象列表
        self.current_selection = None
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        
        # 导入按钮
        self.import_btn = QPushButton("导入图片")
        layout.addWidget(self.import_btn)
        
        # 图片列表
        self.image_listbox = QListWidget()
        self.image_listbox.setViewMode(QListWidget.ViewMode.ListMode)
        self.image_listbox.setIconSize(QSize(48, 48))
        self.image_listbox.setSpacing(2)
        self.image_listbox.setUniformItemSizes(True)
        
        # 启用拖拽功能
        self.image_listbox.setAcceptDrops(True)
        self.image_listbox.setDragDropMode(QListWidget.DragDropMode.DropOnly)
        
        layout.addWidget(self.image_listbox)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        self.copy_btn = QPushButton("复制")
        btn_layout.addWidget(self.copy_btn)
        
        self.delete_btn = QPushButton("删除")
        btn_layout.addWidget(self.delete_btn)
        
        self.clear_btn = QPushButton("清空")
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
        from PySide6.QtWidgets import QFileDialog
        from common.constants import SUPPORTED_IMAGE_FORMATS
        
        try:
            file_paths, _ = QFileDialog.getOpenFileNames(
                self, "选择图片文件", "", 
                ";;".join([f"{name} ({pattern})" for name, pattern in SUPPORTED_IMAGE_FORMATS])
            )
            
            if file_paths:
                # 检查数量限制
                total_count = len(self.image_items) + len(file_paths)
                if total_count > MAX_IMAGE_COUNT:
                    show_error_message(
                        "导入失败", 
                        f"图片总数不能超过{MAX_IMAGE_COUNT}个，当前已有{len(self.image_items)}个"
                    )
                    return
                
                self.images_imported.emit(file_paths)
                logger.info(f"导入了{len(file_paths)}个图片文件")
                
        except Exception as e:
            logger.error(f"导入图片失败: {e}", exc_info=True)
            show_error_message("导入失败", f"导入图片时发生错误: {str(e)}")
    
    def copy_selected(self):
        """复制选中的图片"""
        if self.current_selection:
            self.image_copied.emit(self.current_selection)
            logger.info("复制了选中的图片")
    
    def delete_selected(self):
        """删除选中的图片"""
        if self.current_selection:
            self.image_deleted.emit(self.current_selection)
            logger.info("删除了选中的图片")
    
    def clear_all(self):
        """清空所有图片"""
        if self.image_items:
            self.images_cleared.emit()
            logger.info("清空了所有图片")
    
    def on_selection_changed(self):
        """选择变化事件"""
        current_item = self.image_listbox.currentItem()
        if current_item:
            # 获取对应的ImageItem对象
            row = self.image_listbox.row(current_item)
            if 0 <= row < len(self.image_items):
                self.current_selection = self.image_items[row]
                self.image_selected.emit(self.current_selection)
        else:
            self.current_selection = None
            self.image_selected.emit(None)
    
    def add_image_item(self, image_item):
        """添加图片项"""
        self.image_items.append(image_item)
        self.refresh_list()
    
    def remove_image_item(self, image_item):
        """移除图片项"""
        if image_item in self.image_items:
            self.image_items.remove(image_item)
            self.refresh_list()
    
    def clear_items(self):
        """清空所有项"""
        self.image_items.clear()
        self.current_selection = None
        self.refresh_list()
    
    def refresh_list(self):
        """刷新列表显示"""
        self.image_listbox.clear()
        
        for i, item in enumerate(self.image_items):
            list_item = QListWidgetItem()
            
            # 设置显示文本
            filename = item.filename if hasattr(item, 'filename') else f"图片{i+1}"
            quantity_text = f" (x{item.quantity})" if hasattr(item, 'quantity') and item.quantity > 1 else ""
            list_item.setText(f"{filename}{quantity_text}")
            
            # 设置缩略图图标
            if hasattr(item, 'thumbnail') and item.thumbnail:
                list_item.setIcon(QIcon(item.thumbnail))
            
            self.image_listbox.addItem(list_item)
    
    def get_selected_item(self):
        """获取当前选中的图片项"""
        return self.current_selection
    
    def get_all_items(self):
        """获取所有图片项"""
        return self.image_items.copy()
    
    def set_items(self, items):
        """设置图片项列表"""
        self.image_items = items.copy()
        self.refresh_list()
