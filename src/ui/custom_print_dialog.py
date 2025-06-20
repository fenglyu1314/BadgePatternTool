"""
自定义打印对话框
提供简洁直观的打印界面，类似系统打印对话框的设计
"""

import sys
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSpinBox, QPushButton, QGroupBox, QCheckBox, QRadioButton,
    QWidget, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter, QFont, QPen, QColor
from PySide6.QtPrintSupport import QPrinter, QPrinterInfo

# 导入主界面的颜色配置
from utils.config import COLORS
from common.error_handler import logger

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PrintPreviewWidget(QLabel):
    """打印预览组件"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 300)
        self.setStyleSheet("""
            QLabel {
                background-color: #808080;
                border: 1px solid #666;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setObjectName("preview_label")  # 设置对象名称以便样式应用
        self.preview_pixmap = None
        
    def set_preview_pixmap(self, pixmap):
        """设置预览图片"""
        self.preview_pixmap = pixmap
        self.update_preview()
        
    def update_preview(self):
        """更新预览显示"""
        if self.preview_pixmap:
            # 缩放图片以适应预览区域
            margins = self.contentsMargins()
            available_width = self.width() - margins.left() - margins.right()
            available_height = self.height() - margins.top() - margins.bottom()

            scaled_pixmap = self.preview_pixmap.scaled(
                available_width, available_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
        else:
            self.setText("预览加载中...")
            
    def resizeEvent(self, event):
        """窗口大小改变时更新预览"""
        super().resizeEvent(event)
        if self.preview_pixmap:
            self.update_preview()


class CustomPrintDialog(QDialog):
    """自定义打印对话框"""
    
    # 信号
    print_requested = Signal(dict)  # 发送打印参数
    
    def __init__(self, preview_pixmap=None, parent=None):
        super().__init__(parent)
        self.preview_pixmap = preview_pixmap
        self.printer_list = []
        self.setup_ui()
        self.load_printers()

    def apply_main_window_style(self):
        """应用与主界面一致的样式"""
        style = f"""
            QDialog {{
                background-color: {COLORS['bg_primary']};
                color: {COLORS['text']};
                font-family: "Microsoft YaHei", "SimHei", sans-serif;
            }}
            QLabel {{
                color: {COLORS['text']};
                font-size: 12px;
                background-color: transparent;
            }}
            QGroupBox {{
                font-weight: bold;
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: {COLORS['bg_secondary']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {COLORS['text']};
                background-color: {COLORS['bg_primary']};
            }}
            QComboBox {{
                color: {COLORS['text']};
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 3px;
                padding: 5px;
                min-height: 20px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666;
                margin-right: 5px;
            }}
            QSpinBox {{
                color: {COLORS['text']};
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 3px;
                padding: 3px;
                min-height: 20px;
            }}
            QCheckBox {{
                color: {COLORS['text']};
                spacing: 5px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {COLORS['border']};
                border-radius: 3px;
                background-color: {COLORS['bg_secondary']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['accent']};
                border-color: {COLORS['accent']};
            }}
            QRadioButton {{
                color: {COLORS['text']};
                spacing: 5px;
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                background-color: {COLORS['bg_secondary']};
            }}
            QRadioButton::indicator:checked {{
                background-color: {COLORS['accent']};
                border-color: {COLORS['accent']};
            }}
            QPushButton {{
                color: {COLORS['text']};
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 3px;
                padding: 8px 16px;
                min-height: 24px;
                font-weight: normal;
            }}
            QPushButton:hover {{
                background-color: #f8f9fa;
                border-color: {COLORS['accent']};
            }}
            QPushButton:pressed {{
                background-color: #e9ecef;
            }}
            /* 打印按钮特殊样式 */
            QPushButton#print_button {{
                background-color: {COLORS['success']};
                color: white;
                font-weight: bold;
                border: none;
            }}
            QPushButton#print_button:hover {{
                background-color: #0e6b0e;
            }}
            QPushButton#print_button:pressed {{
                background-color: #0c5a0c;
            }}
            /* 预览区域样式 */
            QLabel#preview_label {{
                color: #666666;
                background-color: #f5f5f5;
                border: 1px solid {COLORS['border']};
            }}
        """
        self.setStyleSheet(style)
        
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("打印")
        self.setModal(True)
        self.resize(900, 650)

        # 应用与主界面一致的样式
        self.apply_main_window_style()

        # 主布局 - 垂直布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 内容区域 - 水平布局
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        # 左侧预览区域
        self.setup_preview_area(content_layout)

        # 右侧控制区域
        self.setup_control_area(content_layout)

        main_layout.addLayout(content_layout)

        # 底部按钮区域
        self.setup_bottom_buttons(main_layout)
        
    def setup_preview_area(self, parent_layout):
        """设置预览区域"""
        # 预览组件
        self.preview_widget = PrintPreviewWidget()
        if self.preview_pixmap:
            self.preview_widget.set_preview_pixmap(self.preview_pixmap)
        
        parent_layout.addWidget(self.preview_widget, 2)  # 占2/3空间
        
    def setup_control_area(self, parent_layout):
        """设置控制区域"""
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        control_layout.setSpacing(15)
        control_layout.setContentsMargins(0, 0, 0, 0)
        
        # 打印机选择
        self.setup_printer_selection(control_layout)
        
        # 打印设置
        self.setup_print_settings(control_layout)
        
        # 页面设置
        self.setup_page_settings(control_layout)
        
        # 添加弹性空间
        control_layout.addStretch()
        
        parent_layout.addWidget(control_widget, 1)  # 占1/3空间
        
    def setup_printer_selection(self, parent_layout):
        """设置打印机选择"""
        # 打印机选择标签
        printer_label = QLabel("选择打印机")
        printer_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        parent_layout.addWidget(printer_label)
        
        # 打印机下拉框
        self.printer_combo = QComboBox()
        self.printer_combo.setMinimumHeight(30)
        parent_layout.addWidget(self.printer_combo)
        
        # 属性按钮
        properties_btn = QPushButton("属性")
        properties_btn.setMaximumWidth(80)
        properties_btn.clicked.connect(self.show_printer_properties)
        parent_layout.addWidget(properties_btn)
        
    def setup_print_settings(self, parent_layout):
        """设置打印设置"""
        # 份数设置
        copies_layout = QHBoxLayout()
        copies_layout.addWidget(QLabel("份数:"))
        
        self.copies_spinbox = QSpinBox()
        self.copies_spinbox.setRange(1, 999)
        self.copies_spinbox.setValue(1)
        self.copies_spinbox.setMaximumWidth(80)
        copies_layout.addWidget(self.copies_spinbox)
        copies_layout.addStretch()
        
        parent_layout.addLayout(copies_layout)
        
        # 页边距设置组
        margins_group = QGroupBox()
        margins_layout = QVBoxLayout(margins_group)
        margins_layout.setSpacing(8)
        
        # 页边距输入框
        margin_inputs = [
            ("左边距:", "left"),
            ("上边距:", "top"), 
            ("右边距:", "right"),
            ("下边距:", "bottom")
        ]
        
        self.margin_spinboxes = {}
        for label_text, key in margin_inputs:
            margin_layout = QHBoxLayout()
            margin_layout.addWidget(QLabel(label_text))

            spinbox = QSpinBox()
            spinbox.setRange(5, 50)  # 最小5mm（打印机硬件限制）
            spinbox.setValue(6)      # 默认6mm（5mm限制+1mm安全余量）
            spinbox.setSuffix("mm")
            spinbox.setMaximumWidth(80)
            # 连接信号以实时更新预览
            spinbox.valueChanged.connect(self.update_preview_with_settings)
            self.margin_spinboxes[key] = spinbox

            margin_layout.addWidget(spinbox)
            margin_layout.addStretch()
            margins_layout.addLayout(margin_layout)
            
        parent_layout.addWidget(margins_group)
        
    def setup_page_settings(self, parent_layout):
        """设置页面设置"""
        # 缩放比例
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("缩放比例:"))
        
        self.scale_spinbox = QSpinBox()
        self.scale_spinbox.setRange(10, 500)
        self.scale_spinbox.setValue(100)
        self.scale_spinbox.setSuffix("%")
        self.scale_spinbox.setMaximumWidth(80)
        # 连接信号以实时更新预览
        self.scale_spinbox.valueChanged.connect(self.update_preview_with_settings)
        scale_layout.addWidget(self.scale_spinbox)
        scale_layout.addStretch()

        parent_layout.addLayout(scale_layout)

        # 选项复选框
        self.rotate_checkbox = QCheckBox("旋转 90°")
        self.rotate_checkbox.toggled.connect(self.update_preview_with_settings)
        parent_layout.addWidget(self.rotate_checkbox)

        self.fit_to_page_checkbox = QCheckBox("缩放以适合纸张")
        self.fit_to_page_checkbox.toggled.connect(self.update_preview_with_settings)
        parent_layout.addWidget(self.fit_to_page_checkbox)

        # 彩色/单色打印选项
        color_group = QGroupBox("打印模式")
        color_layout = QVBoxLayout(color_group)

        self.color_radio = QRadioButton("彩色打印")
        self.color_radio.setChecked(True)  # 默认彩色
        color_layout.addWidget(self.color_radio)

        self.grayscale_radio = QRadioButton("单色打印")
        color_layout.addWidget(self.grayscale_radio)

        parent_layout.addWidget(color_group)

        # 连接信号
        self.fit_to_page_checkbox.toggled.connect(self.on_fit_to_page_changed)

    def update_preview_with_settings(self):
        """根据当前设置更新预览"""
        try:
            if not self.preview_pixmap:
                return

            # 获取当前设置
            settings = self.get_print_settings()

            # 创建新的预览图片，应用当前设置
            updated_preview = self.apply_settings_to_preview(self.preview_pixmap, settings)

            # 更新预览显示
            if hasattr(self, 'preview_widget') and updated_preview:
                self.preview_widget.set_preview_pixmap(updated_preview)

        except Exception as e:
            print(f"更新预览失败: {e}")

    def apply_settings_to_preview(self, original_pixmap, settings):
        """将设置应用到预览图片"""
        try:
            if not original_pixmap:
                return None

            # 创建新的图片副本
            result_pixmap = QPixmap(original_pixmap.size())
            result_pixmap.fill(Qt.GlobalColor.white)

            painter = QPainter(result_pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # 计算变换
            scale_factor = settings['scale'] / 100.0

            # 应用旋转
            if settings['rotate']:
                painter.translate(result_pixmap.width() / 2, result_pixmap.height() / 2)
                painter.rotate(90)
                painter.translate(-result_pixmap.height() / 2, -result_pixmap.width() / 2)

            # 应用缩放
            if settings['fit_to_page']:
                # 适合纸张模式
                scaled_pixmap = original_pixmap.scaled(
                    result_pixmap.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            else:
                # 自定义缩放
                new_size = original_pixmap.size() * scale_factor
                scaled_pixmap = original_pixmap.scaled(
                    new_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

            # 计算居中位置
            x = (result_pixmap.width() - scaled_pixmap.width()) // 2
            y = (result_pixmap.height() - scaled_pixmap.height()) // 2

            # 绘制图片
            painter.drawPixmap(x, y, scaled_pixmap)

            # 绘制页边距线
            self.draw_margin_lines(painter, result_pixmap.size(), settings['margins'])

            painter.end()
            return result_pixmap

        except Exception as e:

            logger.error(f"应用设置到预览失败: {e}", exc_info=True)
            return original_pixmap

    def draw_margin_lines(self, painter, pixmap_size, margins):
        """绘制页边距线"""
        try:


            # 设置页边距线样式
            painter.setPen(QPen(QColor(200, 100, 100), 2, Qt.PenStyle.DashLine))

            # 计算页边距像素值（假设96 DPI）
            dpi = 96
            left_px = int(margins['left'] * dpi / 25.4)
            top_px = int(margins['top'] * dpi / 25.4)
            right_px = int(margins['right'] * dpi / 25.4)
            bottom_px = int(margins['bottom'] * dpi / 25.4)

            # 绘制页边距矩形
            margin_rect_x = left_px
            margin_rect_y = top_px
            margin_rect_width = pixmap_size.width() - left_px - right_px
            margin_rect_height = pixmap_size.height() - top_px - bottom_px

            if margin_rect_width > 0 and margin_rect_height > 0:
                painter.drawRect(margin_rect_x, margin_rect_y, margin_rect_width, margin_rect_height)

        except Exception as e:
            print(f"绘制页边距线失败: {e}")


        
    def setup_bottom_buttons(self, parent_layout):
        """设置底部按钮"""
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)

        # 重置按钮
        reset_btn = QPushButton("重置")
        reset_btn.setMinimumHeight(35)
        reset_btn.clicked.connect(self.reset_settings)
        button_layout.addWidget(reset_btn)

        button_layout.addStretch()

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setMinimumHeight(35)
        close_btn.setMinimumWidth(80)
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)

        # 打印按钮
        print_btn = QPushButton("打印")
        print_btn.setObjectName("print_button")  # 设置对象名以应用特殊样式
        print_btn.setMinimumHeight(35)
        print_btn.setMinimumWidth(80)
        print_btn.clicked.connect(self.start_print)
        button_layout.addWidget(print_btn)

        # 将按钮布局添加到父布局
        parent_layout.addLayout(button_layout)



    def load_printers(self):
        """加载可用打印机"""
        try:
            # 获取所有可用打印机
            printers = QPrinterInfo.availablePrinters()
            self.printer_list = printers
            
            # 清空下拉框
            self.printer_combo.clear()
            
            # 添加打印机到下拉框
            for printer in printers:
                self.printer_combo.addItem(printer.printerName())
                
            # 设置默认打印机
            default_printer = QPrinterInfo.defaultPrinter()
            if default_printer.isNull():
                return
                
            default_name = default_printer.printerName()
            index = self.printer_combo.findText(default_name)
            if index >= 0:
                self.printer_combo.setCurrentIndex(index)
                
        except Exception as e:
            print(f"加载打印机失败: {e}")
            
    def get_selected_printer(self):
        """获取选中的打印机"""
        current_index = self.printer_combo.currentIndex()
        if 0 <= current_index < len(self.printer_list):
            return self.printer_list[current_index]
        return None
        
    def get_print_settings(self):
        """获取打印设置"""
        return {
            'printer': self.get_selected_printer(),
            'copies': self.copies_spinbox.value(),
            'margins': {
                'left': self.margin_spinboxes['left'].value(),
                'top': self.margin_spinboxes['top'].value(),
                'right': self.margin_spinboxes['right'].value(),
                'bottom': self.margin_spinboxes['bottom'].value(),
            },
            'scale': self.scale_spinbox.value(),
            'rotate': self.rotate_checkbox.isChecked(),
            'fit_to_page': self.fit_to_page_checkbox.isChecked(),
            'color_mode': 'color' if self.color_radio.isChecked() else 'grayscale',
        }
        
    def on_fit_to_page_changed(self, checked):
        """适合纸张选项改变"""
        # 如果选择适合纸张，禁用缩放比例输入
        self.scale_spinbox.setEnabled(not checked)
        if checked:
            self.scale_spinbox.setValue(100)
            
    def reset_settings(self):
        """重置设置"""
        self.copies_spinbox.setValue(1)
        for spinbox in self.margin_spinboxes.values():
            spinbox.setValue(0)
        self.scale_spinbox.setValue(100)
        self.rotate_checkbox.setChecked(False)
        self.fit_to_page_checkbox.setChecked(False)
        self.color_radio.setChecked(True)  # 默认彩色打印
        
    def show_printer_properties(self):
        """显示打印机属性设置"""
        try:
            # 获取当前选中的打印机
            current_index = self.printer_combo.currentIndex()
            if current_index < 0 or current_index >= len(self.printer_list):

                QMessageBox.warning(self, "错误", "请先选择一个打印机")
                return

            # 获取选中的打印机信息
            printer_info = self.printer_list[current_index]
            printer_name = printer_info.printerName()

            # 尝试使用Windows API打开打印机属性对话框
            try:
                import subprocess
                import platform

                if platform.system() == "Windows":
                    # 使用Windows的rundll32调用打印机属性对话框
                    # /e 参数打开打印机属性对话框，而不是管理界面
                    subprocess.run([
                        "rundll32.exe",
                        "printui.dll,PrintUIEntry",
                        "/e",
                        f"/n{printer_name}"
                    ], check=False)
                else:
                    # 非Windows系统，尝试使用Qt的打印机属性对话框
                    self._show_qt_printer_properties(printer_info)

            except Exception as subprocess_error:
                logger.warning(f"Windows API调用失败: {subprocess_error}")
                # 如果Windows API失败，尝试使用Qt的打印机属性对话框
                self._show_qt_printer_properties(printer_info)

        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开打印机属性：{str(e)}")

    def _show_qt_printer_properties(self, printer_info):
        """使用Qt显示打印机属性对话框"""
        try:
            from PySide6.QtPrintSupport import QPageSetupDialog

            # 创建打印机对象
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setPrinterName(printer_info.printerName())

            # 创建页面设置对话框（包含打印机属性）
            page_setup_dialog = QPageSetupDialog(printer, self)
            page_setup_dialog.setWindowTitle(f"打印机属性 - {printer_info.printerName()}")

            # 显示对话框
            result = page_setup_dialog.exec()

            if result == page_setup_dialog.DialogCode.Accepted:
                print(f"打印机属性设置已更新: {printer_info.printerName()}")

        except Exception as e:
            logger.error(f"Qt打印机属性对话框失败: {e}", exc_info=True)
            # 最后的备选方案：显示手动指导
            QMessageBox.information(
                self,
                "打印机属性",
                f"请手动打开打印机 '{printer_info.printerName()}' 的属性设置：\n\n"
                "Windows系统：\n"
                "1. 打开控制面板\n"
                "2. 选择'设备和打印机'\n"
                "3. 右键点击打印机\n"
                "4. 选择'打印机属性'\n\n"
                "或者在设置中搜索'打印机'进行配置。"
            )
        
    def start_print(self):
        """开始打印"""
        settings = self.get_print_settings()
        if settings['printer'] is None:
            QMessageBox.warning(self, "错误", "请选择一个打印机")
            return

        # 发送打印请求信号
        self.print_requested.emit(settings)
        self.accept()
