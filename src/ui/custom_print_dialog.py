"""
自定义打印对话框
提供简洁直观的打印界面，类似系统打印对话框的设计
"""

import sys
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSpinBox, QPushButton, QGroupBox, QRadioButton,
    QWidget, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtPrintSupport import QPrinter, QPrinterInfo

from common.error_handler import logger

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PrintPreviewWidget(QLabel):
    """打印预览组件"""

    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 300)
        # 只设置背景和边框，让文字颜色跟随系统主题
        self.setStyleSheet("""
            QLabel {
                background-color: #808080;
                border: 1px solid #666;
            }
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setObjectName("preview_label")  # 设置对象名称以便样式应用
        # 设置内容边距，在预览图片周围留出空间
        self.setContentsMargins(20, 20, 20, 20)
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
        """完全使用系统默认样式"""
        # 清除所有样式，让Qt使用系统默认样式
        self.setStyleSheet("")
        
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("打印")
        self.setModal(True)
        # 调整窗口大小，让左侧预览区域更接近A4比例
        # A4比例约1:1.41，考虑右侧控制面板，总宽度设为750
        self.resize(750, 600)

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

        # 右侧控制区域（包含参数和按钮）
        self.setup_control_area(content_layout)

        main_layout.addLayout(content_layout)

        # 设置焦点策略，防止回车键意外触发按钮
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def keyPressEvent(self, event):
        """处理键盘事件，防止回车键意外触发按钮"""
        # 如果按下回车键，不做任何处理（忽略）
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            event.ignore()
            return
        # 其他键盘事件正常处理
        super().keyPressEvent(event)
        
    def setup_preview_area(self, parent_layout):
        """设置预览区域"""
        # 预览组件
        self.preview_widget = PrintPreviewWidget()
        if self.preview_pixmap:
            self.preview_widget.set_preview_pixmap(self.preview_pixmap)

        parent_layout.addWidget(self.preview_widget, 3)  # 占3/4空间，更接近A4比例
        
    def setup_control_area(self, parent_layout):
        """设置控制区域（包含参数和按钮）"""
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        control_layout.setSpacing(15)
        control_layout.setContentsMargins(0, 0, 0, 0)

        # 打印机选择
        self.setup_printer_selection(control_layout)

        # 打印设置
        self.setup_print_settings(control_layout)

        # 添加弹性空间
        control_layout.addStretch()

        # 底部按钮区域
        self.setup_control_buttons(control_layout)

        parent_layout.addWidget(control_widget, 1)  # 占1/4空间
        
    def setup_printer_selection(self, parent_layout):
        """设置打印机选择"""
        # 打印机选择标签 - 使用系统默认样式
        printer_label = QLabel("选择打印机")
        parent_layout.addWidget(printer_label)

        # 打印机选择和属性按钮的水平布局
        printer_layout = QHBoxLayout()
        printer_layout.setSpacing(8)  # 设置间距

        # 打印机下拉框
        self.printer_combo = QComboBox()
        printer_layout.addWidget(self.printer_combo, 1)  # 占用剩余空间

        # 属性按钮
        self.properties_btn = QPushButton("属性")
        self.properties_btn.setMaximumWidth(60)   # 稍微缩小宽度
        self.properties_btn.setAutoDefault(False)  # 禁用默认按钮行为
        self.properties_btn.setDefault(False)      # 禁用默认按钮行为
        self.properties_btn.clicked.connect(self.show_printer_properties)
        printer_layout.addWidget(self.properties_btn, 0)  # 固定宽度

        parent_layout.addLayout(printer_layout)
        
    def setup_print_settings(self, parent_layout):
        """设置打印设置"""
        # 份数设置
        copies_layout = QHBoxLayout()
        copies_layout.addWidget(QLabel("份数:"))

        self.copies_spinbox = QSpinBox()
        self.copies_spinbox.setRange(1, 999)
        self.copies_spinbox.setValue(1)
        self.copies_spinbox.setMinimumHeight(30)  # 适中的高度
        self.copies_spinbox.setMinimumWidth(80)   # 适中的宽度
        copies_layout.addWidget(self.copies_spinbox)
        copies_layout.addStretch()

        parent_layout.addLayout(copies_layout)

        # 打印模式设置
        color_group = QGroupBox("打印模式")
        color_layout = QVBoxLayout(color_group)

        self.color_radio = QRadioButton("彩色打印")
        self.color_radio.setChecked(True)  # 默认彩色
        color_layout.addWidget(self.color_radio)

        self.grayscale_radio = QRadioButton("单色打印")
        color_layout.addWidget(self.grayscale_radio)

        parent_layout.addWidget(color_group)

    def setup_control_buttons(self, parent_layout):
        """设置控制按钮（在右侧面板）"""
        # 打印按钮（填满宽度）
        print_btn = QPushButton("打印")
        print_btn.setObjectName("print_button")
        print_btn.setMinimumHeight(40)  # 稍微大一些突出主要操作
        print_btn.setAutoDefault(False)
        print_btn.setDefault(False)

        # 直接为打印按钮设置绿色样式
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #107c10;
                color: white;
                font-weight: bold;
                border: none;
                padding: 8px 16px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #0e6b0e;
            }
            QPushButton:pressed {
                background-color: #0c5a0c;
            }
        """)

        print_btn.clicked.connect(self.start_print)

        # 添加一些上边距
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 15, 0, 0)
        button_layout.addWidget(print_btn)

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
            'color_mode': 'color' if self.color_radio.isChecked() else 'grayscale',
        }
        

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
