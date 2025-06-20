"""
导入工具模块
统一管理可选依赖的导入和检查
"""

import sys
from typing import Optional, Any


class OptionalImport:
    """可选导入类，用于处理可能不存在的依赖"""
    
    def __init__(self, module_name: str, package: Optional[str] = None):
        self.module_name = module_name
        self.package = package
        self.module = None
        self.available = False
        self._import_error = None
        
        self._try_import()
    
    def _try_import(self):
        """尝试导入模块"""
        try:
            if self.package:
                self.module = __import__(self.package, fromlist=[self.module_name])
                self.module = getattr(self.module, self.module_name)
            else:
                self.module = __import__(self.module_name)
            self.available = True
        except ImportError as e:
            self._import_error = e
            self.available = False
    
    def __getattr__(self, name: str) -> Any:
        """获取模块属性"""
        if not self.available:
            raise ImportError(f"Module '{self.module_name}' is not available: {self._import_error}")
        return getattr(self.module, name)
    
    def __bool__(self) -> bool:
        """检查模块是否可用"""
        return self.available


# 常用的可选导入
PYSIDE6_AVAILABLE = False
PIL_AVAILABLE = False
REPORTLAB_AVAILABLE = False

try:
    # QtWidgets
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QListWidget, QListWidgetItem,
        QSlider, QRadioButton, QComboBox, QButtonGroup, QSpinBox,
        QMessageBox, QStatusBar, QSplitter, QGroupBox,
        QSpacerItem, QSizePolicy
    )
    # QtCore
    from PySide6.QtCore import Qt, QTimer, QSize, QPoint
    # QtGui
    from PySide6.QtGui import QPixmap, QIcon, QAction, QPainter
    # QtPrintSupport
    from PySide6.QtPrintSupport import QPrinter
    PYSIDE6_AVAILABLE = True
except ImportError:
    # 如果导入失败，设置为None
    QApplication = QMainWindow = QWidget = QVBoxLayout = QHBoxLayout = None
    QLabel = QPushButton = QListWidget = QListWidgetItem = None
    QSlider = QRadioButton = QComboBox = QButtonGroup = QSpinBox = None
    QMessageBox = QStatusBar = QSplitter = QGroupBox = None
    QSpacerItem = QSizePolicy = Qt = QTimer = QSize = QPoint = None
    QPixmap = QIcon = QAction = QPainter = QPrinter = None
    PYSIDE6_AVAILABLE = False

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    Image = ImageDraw = None

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    REPORTLAB_AVAILABLE = True
except ImportError:
    canvas = A4 = None


def check_required_dependencies():
    """检查必需的依赖是否可用"""
    missing_deps = []
    
    if not PYSIDE6_AVAILABLE:
        missing_deps.append("PySide6")
    if not PIL_AVAILABLE:
        missing_deps.append("Pillow")
    if not REPORTLAB_AVAILABLE:
        missing_deps.append("reportlab")
    
    if missing_deps:
        raise ImportError(f"Missing required dependencies: {', '.join(missing_deps)}")
    
    return True


def get_dependency_info():
    """获取依赖信息"""
    return {
        'PySide6': PYSIDE6_AVAILABLE,
        'PIL': PIL_AVAILABLE,
        'ReportLab': REPORTLAB_AVAILABLE
    }
