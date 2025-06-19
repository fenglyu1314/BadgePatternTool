"""
主窗口管理器
协调各个UI组件之间的交互
"""

from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QObject, pyqtSignal

from core.image_processor import ImageProcessor, ImageProcessParams
from core.layout_engine import LayoutEngine
from core.export_manager import ExportManager, ExportConfig
from utils.config import app_config


class MainWindowManager(QObject):
    """主窗口管理器类"""
    
    # 信号定义
    preview_update_requested = pyqtSignal()  # 预览更新请求
    layout_info_updated = pyqtSignal(str)  # 布局信息更新
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化业务逻辑组件
        self.image_processor = ImageProcessor()
        self.layout_engine = LayoutEngine()
        self.export_manager = ExportManager()
        
        # 当前状态
        self.current_image_items = []
        self.current_selection = None
        
        # UI组件引用（由主窗口设置）
        self.image_list_panel = None
        self.control_panel = None
        self.edit_controls_panel = None
        self.interactive_editor = None
        self.preview_widget = None
    
    def set_ui_components(self, **components):
        """设置UI组件引用"""
        for name, component in components.items():
            setattr(self, name, component)
        
        # 设置信号连接
        self.setup_connections()
    
    def setup_connections(self):
        """设置组件间的信号连接"""
        if self.image_list_panel:
            self.image_list_panel.image_selected.connect(self.on_image_selected)
            self.image_list_panel.images_changed.connect(self.on_images_changed)
        
        if self.control_panel:
            self.control_panel.layout_mode_changed.connect(self.on_layout_mode_changed)
            self.control_panel.spacing_changed.connect(self.on_spacing_changed)
            self.control_panel.margin_changed.connect(self.on_margin_changed)
            self.control_panel.diameter_changed.connect(self.on_diameter_changed)
            self.control_panel.export_requested.connect(self.on_export_requested)
            self.control_panel.print_requested.connect(self.on_print_requested)
            self.control_panel.auto_layout_requested.connect(self.on_auto_layout_requested)
        
        if self.edit_controls_panel:
            self.edit_controls_panel.scale_changed.connect(self.on_scale_changed)
            self.edit_controls_panel.offset_changed.connect(self.on_offset_changed)
            self.edit_controls_panel.rotation_changed.connect(self.on_rotation_changed)
            self.edit_controls_panel.quantity_changed.connect(self.on_quantity_changed)
            self.edit_controls_panel.reset_requested.connect(self.on_reset_requested)
        
        if self.interactive_editor:
            self.interactive_editor.parameters_changed.connect(self.on_editor_parameters_changed)
    
    def on_image_selected(self, image_item):
        """处理图片选择"""
        self.current_selection = image_item
        
        if image_item:
            # 更新编辑控制面板
            if self.edit_controls_panel:
                self.edit_controls_panel.update_from_image_item(image_item)
            
            # 更新交互式编辑器
            if self.interactive_editor:
                self.interactive_editor.load_image(image_item.file_path)
                self.interactive_editor.set_parameters(
                    image_item.scale,
                    image_item.offset_x,
                    image_item.offset_y,
                    image_item.rotation
                )
        else:
            # 清空编辑器
            if self.interactive_editor:
                self.interactive_editor.clear_image()
    
    def on_images_changed(self):
        """处理图片列表变化"""
        if self.image_list_panel:
            self.current_image_items = self.image_list_panel.get_image_items()
        
        # 更新预览
        self.preview_update_requested.emit()
        
        # 更新布局信息
        self.update_layout_info()
    
    def on_layout_mode_changed(self, mode):
        """处理布局模式变化"""
        self.preview_update_requested.emit()
        self.update_layout_info()
    
    def on_spacing_changed(self, spacing):
        """处理间距变化"""
        self.preview_update_requested.emit()
        self.update_layout_info()
    
    def on_margin_changed(self, margin):
        """处理页边距变化"""
        self.preview_update_requested.emit()
        self.update_layout_info()
    
    def on_diameter_changed(self, diameter):
        """处理直径变化"""
        app_config.set_badge_diameter(diameter)
        
        # 更新交互式编辑器的遮罩
        if self.interactive_editor:
            self.interactive_editor.update_mask_radius()
        
        self.preview_update_requested.emit()
        self.update_layout_info()
    
    def on_scale_changed(self, scale):
        """处理缩放变化"""
        if self.current_selection:
            self.current_selection.scale = scale
            self.update_editor_and_preview()
    
    def on_offset_changed(self, offset_x, offset_y):
        """处理偏移变化"""
        if self.current_selection:
            self.current_selection.offset_x = offset_x
            self.current_selection.offset_y = offset_y
            self.update_editor_and_preview()
    
    def on_rotation_changed(self, rotation):
        """处理旋转变化"""
        if self.current_selection:
            self.current_selection.rotation = rotation
            self.update_editor_and_preview()
    
    def on_quantity_changed(self, quantity):
        """处理数量变化"""
        if self.current_selection:
            self.current_selection.quantity = quantity
            
            # 更新图片列表显示
            if self.image_list_panel:
                self.image_list_panel.update_image_list()
            
            self.preview_update_requested.emit()
    
    def on_reset_requested(self):
        """处理重置请求"""
        if self.current_selection:
            self.current_selection.scale = 1.0
            self.current_selection.offset_x = 0
            self.current_selection.offset_y = 0
            self.current_selection.rotation = 0
            self.current_selection.quantity = 1
            
            # 更新UI
            if self.edit_controls_panel:
                self.edit_controls_panel.update_from_image_item(self.current_selection)
            
            self.update_editor_and_preview()
    
    def on_editor_parameters_changed(self, scale, offset_x, offset_y):
        """处理编辑器参数变化"""
        if self.current_selection:
            self.current_selection.scale = scale
            self.current_selection.offset_x = offset_x
            self.current_selection.offset_y = offset_y
            
            # 更新编辑控制面板
            if self.edit_controls_panel:
                self.edit_controls_panel.update_from_image_item(self.current_selection)
            
            self.preview_update_requested.emit()
    
    def on_export_requested(self):
        """处理导出请求"""
        if not self.current_image_items:
            QMessageBox.warning(None, "警告", "请先导入图片")
            return
        
        try:
            # 获取导出配置
            config = ExportConfig(
                layout_type=self.control_panel.get_layout_mode(),
                spacing_mm=self.control_panel.get_spacing(),
                margin_mm=self.control_panel.get_margin(),
                format_type=self.control_panel.get_export_format()
            )
            
            # 展开图片列表（考虑数量）
            expanded_items = self.expand_image_items()
            
            # 执行导出
            success, count = self.export_manager.export_with_dialog(expanded_items, config=config)
            
            if success:
                QMessageBox.information(None, "成功", f"成功导出 {count} 个图片")
            
        except Exception as e:
            QMessageBox.critical(None, "错误", f"导出失败: {e}")
    
    def on_print_requested(self):
        """处理打印请求"""
        if not self.current_image_items:
            QMessageBox.warning(None, "警告", "请先导入图片")
            return
        
        # 实现打印逻辑
        print("打印功能待实现")
    
    def on_auto_layout_requested(self):
        """处理自动排版请求"""
        # 实现自动排版逻辑
        self.preview_update_requested.emit()
    
    def update_editor_and_preview(self):
        """更新编辑器和预览"""
        if self.current_selection and self.interactive_editor:
            self.interactive_editor.set_parameters(
                self.current_selection.scale,
                self.current_selection.offset_x,
                self.current_selection.offset_y,
                self.current_selection.rotation
            )
        
        self.preview_update_requested.emit()
    
    def update_layout_info(self):
        """更新布局信息"""
        if not self.control_panel:
            return
        
        try:
            # 计算布局
            if self.control_panel.get_layout_mode() == 'grid':
                layout = self.layout_engine.calculate_grid_layout(
                    self.control_panel.get_spacing(),
                    self.control_panel.get_margin()
                )
            else:
                layout = self.layout_engine.calculate_compact_layout(
                    self.control_panel.get_spacing(),
                    self.control_panel.get_margin()
                )
            
            # 计算实际图片数量
            total_images = sum(item.quantity for item in self.current_image_items)
            max_count = layout['max_count']
            
            info_text = f"可放置: {max_count} | 已有: {total_images}"
            self.layout_info_updated.emit(info_text)
            
        except Exception as e:
            self.layout_info_updated.emit(f"布局计算错误: {e}")
    
    def expand_image_items(self):
        """展开图片项目列表（考虑数量）"""
        expanded_items = []
        for item in self.current_image_items:
            for _ in range(item.quantity):
                expanded_items.append(item)
        return expanded_items
    
    def get_current_image_items(self):
        """获取当前图片项目列表"""
        return self.current_image_items
    
    def get_current_selection(self):
        """获取当前选择"""
        return self.current_selection
