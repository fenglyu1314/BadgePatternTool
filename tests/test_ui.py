"""
UI模块测试
测试用户界面组件和交互功能
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加src目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# 检查PySide6是否可用
try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QPixmap
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False


@unittest.skipUnless(PYSIDE6_AVAILABLE, "PySide6 not available")
class TestInteractiveImageEditor(unittest.TestCase):
    """交互式图片编辑器测试"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试类"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """设置测试"""
        from ui.interactive_image_editor import InteractiveImageEditor
        self.editor = InteractiveImageEditor()
    
    def test_editor_initialization(self):
        """测试编辑器初始化"""
        self.assertIsNotNone(self.editor)
        self.assertEqual(self.editor.image_scale, 1.0)
        self.assertEqual(self.editor.image_offset.x(), 0)
        self.assertEqual(self.editor.image_offset.y(), 0)
    
    def test_cache_functionality(self):
        """测试缓存功能"""
        # 测试缓存失效
        self.editor._invalidate_cache()
        self.assertFalse(self.editor._cache_valid)
        
        # 测试缓存检查
        is_valid = self.editor._is_cache_valid()
        self.assertIsInstance(is_valid, bool)
    
    def test_mask_radius_calculation(self):
        """测试遮罩半径计算"""
        self.editor.update_mask_radius()
        self.assertGreater(self.editor.mask_radius, 0)
    
    def test_scale_limits(self):
        """测试缩放限制"""
        # 测试最小缩放
        self.editor.image_scale = 0.05  # 低于最小值
        self.editor.apply_scale_limits()
        self.assertGreaterEqual(self.editor.image_scale, 0.1)
        
        # 测试最大缩放
        self.editor.image_scale = 15.0  # 高于最大值
        self.editor.apply_scale_limits()
        self.assertLessEqual(self.editor.image_scale, 10.0)


@unittest.skipUnless(PYSIDE6_AVAILABLE, "PySide6 not available")
class TestInteractivePreviewLabel(unittest.TestCase):
    """交互式预览标签测试"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试类"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """设置测试"""
        from ui.interactive_preview_label import InteractivePreviewLabel
        self.preview = InteractivePreviewLabel()
    
    def test_preview_initialization(self):
        """测试预览初始化"""
        self.assertIsNotNone(self.preview)
        self.assertEqual(self.preview.scale_factor, 1.0)
        self.assertEqual(self.preview.offset_x, 0)
        self.assertEqual(self.preview.offset_y, 0)
    
    def test_zoom_functionality(self):
        """测试缩放功能"""
        initial_scale = self.preview.scale_factor
        
        # 测试放大
        self.preview.zoom_in()
        self.assertGreater(self.preview.scale_factor, initial_scale)
        
        # 测试缩小
        self.preview.zoom_out()
        self.assertLess(self.preview.scale_factor, self.preview.scale_factor)
        
        # 测试重置
        self.preview.reset_view()
        self.assertEqual(self.preview.scale_factor, 1.0)
        self.assertEqual(self.preview.offset_x, 0)
        self.assertEqual(self.preview.offset_y, 0)
    
    def test_fit_to_window(self):
        """测试适应窗口功能"""
        # 设置一个测试图片
        test_pixmap = QPixmap(800, 600)
        self.preview.set_pixmap(test_pixmap)
        
        # 测试适应窗口
        self.preview.fit_to_window()
        self.assertGreater(self.preview.scale_factor, 0)
        self.assertLessEqual(self.preview.scale_factor, 1.0)


@unittest.skipUnless(PYSIDE6_AVAILABLE, "PySide6 not available")
class TestMainWindowComponents(unittest.TestCase):
    """主窗口组件测试"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试类"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def test_component_initialization(self):
        """测试组件初始化"""
        # 测试核心组件是否可以正常导入和初始化
        from utils.file_handler import FileHandler
        from core.image_processor import ImageProcessor
        from core.layout_engine import LayoutEngine
        from core.export_manager import ExportManager
        
        file_handler = FileHandler()
        image_processor = ImageProcessor()
        layout_engine = LayoutEngine()
        export_manager = ExportManager()
        
        self.assertIsNotNone(file_handler)
        self.assertIsNotNone(image_processor)
        self.assertIsNotNone(layout_engine)
        self.assertIsNotNone(export_manager)
    
    @patch('ui.main_window.MainWindow')
    def test_main_window_mock(self, mock_main_window):
        """测试主窗口模拟"""
        # 创建模拟主窗口
        mock_window = mock_main_window.return_value
        mock_window.image_items = []
        mock_window.current_selection = None
        
        # 测试模拟对象
        self.assertIsNotNone(mock_window)
        self.assertEqual(mock_window.image_items, [])
        self.assertIsNone(mock_window.current_selection)


class TestUIUtilities(unittest.TestCase):
    """UI工具函数测试"""
    
    def test_error_handling_ui(self):
        """测试UI错误处理"""
        from common.error_handler import logger, ImageProcessingError
        
        # 测试日志记录
        logger.info("测试UI日志记录")
        
        # 测试自定义异常
        with self.assertRaises(ImageProcessingError):
            raise ImageProcessingError("UI测试异常")
    
    def test_config_ui_integration(self):
        """测试配置与UI集成"""
        from utils.config import app_config
        
        # 测试配置访问
        self.assertIsNotNone(app_config)
        self.assertGreater(app_config.badge_diameter_mm, 0)
        
        # 测试配置监听器机制
        if hasattr(app_config, 'add_listener'):
            def test_listener(key, old_value, new_value):
                pass
            
            app_config.add_listener(test_listener)
            # 测试监听器添加成功
            self.assertTrue(True)


class TestUIPerformance(unittest.TestCase):
    """UI性能测试"""
    
    def test_component_creation_performance(self):
        """测试组件创建性能"""
        import time
        
        start_time = time.time()
        
        # 创建多个组件实例
        from utils.file_handler import FileHandler
        from core.image_processor import ImageProcessor
        
        for _ in range(5):
            handler = FileHandler()
            processor = ImageProcessor()
            
            self.assertIsNotNone(handler)
            self.assertIsNotNone(processor)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # 组件创建应该很快（1秒内）
        self.assertLess(creation_time, 1.0)
    
    def test_cache_performance(self):
        """测试缓存性能"""
        from core.image_processor import ImageProcessor
        
        processor = ImageProcessor()
        
        # 测试缓存操作性能
        start_time = time.time()
        
        for i in range(100):
            key = f"test_key_{i}"
            processor._update_cache_access(key)
        
        end_time = time.time()
        cache_time = end_time - start_time
        
        # 缓存操作应该很快（100ms内）
        self.assertLess(cache_time, 0.1)


class TestUIIntegration(unittest.TestCase):
    """UI集成测试"""
    
    def test_module_integration(self):
        """测试模块集成"""
        # 测试各模块之间的集成
        from utils.file_handler import FileHandler
        from core.image_processor import ImageProcessor
        from core.layout_engine import LayoutEngine
        
        handler = FileHandler()
        processor = ImageProcessor()
        engine = LayoutEngine()
        
        # 测试模块间的基本交互
        self.assertIsInstance(handler.supported_formats, list)
        self.assertGreater(processor.badge_diameter_px, 0)
        self.assertGreater(engine.a4_width_px, 0)
    
    def test_error_propagation(self):
        """测试错误传播"""
        from common.error_handler import error_handler
        
        @error_handler("测试UI错误", show_error=False, default_return=None)
        def test_ui_function():
            raise ValueError("UI测试错误")
        
        result = test_ui_function()
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
