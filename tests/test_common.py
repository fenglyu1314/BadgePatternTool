"""
公共模块测试
测试common目录下的公共功能模块
"""

import unittest
import sys
import os
import tempfile
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加src目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from common.imports import check_required_dependencies, get_dependency_info
from common.constants import *
from common.path_utils import get_project_root, get_assets_dir
from common.error_handler import logger, error_handler, resource_manager, ImageProcessingError


class TestImports(unittest.TestCase):
    """导入管理测试"""
    
    def test_dependency_check(self):
        """测试依赖检查"""
        # 测试必需依赖检查
        try:
            result = check_required_dependencies()
            self.assertTrue(result)
        except ImportError:
            # 如果缺少依赖，应该抛出ImportError
            pass
    
    def test_dependency_info(self):
        """测试依赖信息获取"""
        info = get_dependency_info()
        self.assertIsInstance(info, dict)
        self.assertIn('PySide6', info)
        self.assertIn('PIL', info)
        self.assertIn('ReportLab', info)


class TestConstants(unittest.TestCase):
    """常量定义测试"""
    
    def test_version_constants(self):
        """测试版本常量"""
        self.assertIsInstance(APP_VERSION, str)
        self.assertTrue(len(APP_VERSION) > 0)
        self.assertRegex(APP_VERSION, r'^\d+\.\d+\.\d+$')  # 版本号格式检查
    
    def test_size_constants(self):
        """测试尺寸常量"""
        self.assertGreater(A4_WIDTH_PX, 0)
        self.assertGreater(A4_HEIGHT_PX, 0)
        self.assertGreater(PRINT_DPI, 0)
        self.assertGreater(DEFAULT_BADGE_SIZE_MM, 0)
    
    def test_format_constants(self):
        """测试格式常量"""
        self.assertIsInstance(SUPPORTED_IMAGE_FORMATS, list)
        self.assertGreater(len(SUPPORTED_IMAGE_FORMATS), 0)
        self.assertIn(('.jpg', 'JPEG'), SUPPORTED_IMAGE_FORMATS)
        self.assertIn(('.png', 'PNG'), SUPPORTED_IMAGE_FORMATS)


class TestPathUtils(unittest.TestCase):
    """路径工具测试"""
    
    def test_project_root(self):
        """测试项目根目录获取"""
        root = get_project_root()
        self.assertIsInstance(root, Path)
        self.assertTrue(root.exists())
        self.assertTrue((root / "src").exists())
    
    def test_src_path(self):
        """测试源码目录获取"""
        src = get_project_root()
        self.assertIsInstance(src, Path)
        self.assertTrue(src.exists())
        self.assertTrue((src / "main.py").exists())
    
    def test_assets_path(self):
        """测试资源目录获取"""
        assets = get_assets_path()
        self.assertIsInstance(assets, Path)
        # 资源目录可能不存在，但路径应该正确
        self.assertEqual(assets.name, "assets")


class TestErrorHandler(unittest.TestCase):
    """错误处理测试"""
    
    def test_logger_initialization(self):
        """测试日志器初始化"""
        self.assertIsNotNone(logger)
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "BadgePatternTool")
    
    def test_error_decorator(self):
        """测试错误处理装饰器"""
        @error_handler("测试错误", show_error=False, default_return="default")
        def test_function():
            raise ValueError("测试异常")
        
        result = test_function()
        self.assertEqual(result, "default")
    
    def test_error_decorator_success(self):
        """测试错误处理装饰器成功情况"""
        @error_handler("测试错误", show_error=False, default_return="default")
        def test_function():
            return "success"
        
        result = test_function()
        self.assertEqual(result, "success")
    
    def test_resource_manager(self):
        """测试资源管理器"""
        # 测试None资源
        with resource_manager(None) as resource:
            self.assertIsNone(resource)
        
        # 测试文件资源
        with tempfile.NamedTemporaryFile() as temp_file:
            with resource_manager(temp_file) as resource:
                self.assertEqual(resource, temp_file)
    
    def test_custom_exception(self):
        """测试自定义异常"""
        with self.assertRaises(ImageProcessingError):
            raise ImageProcessingError("测试图片处理错误")


class TestErrorHandlerIntegration(unittest.TestCase):
    """错误处理集成测试"""
    
    def test_logging_levels(self):
        """测试日志级别"""
        with patch('common.error_handler.logger') as mock_logger:
            logger.debug("调试信息")
            logger.info("信息")
            logger.warning("警告")
            logger.error("错误")
            
            # 验证日志方法被调用
            mock_logger.debug.assert_called_with("调试信息")
            mock_logger.info.assert_called_with("信息")
            mock_logger.warning.assert_called_with("警告")
            mock_logger.error.assert_called_with("错误")
    
    @patch('common.error_handler.show_error_message')
    def test_error_message_display(self, mock_show_error):
        """测试错误消息显示"""
        @error_handler("测试错误", show_error=True, default_return=None)
        def failing_function():
            raise RuntimeError("测试运行时错误")
        
        result = failing_function()
        self.assertIsNone(result)
        mock_show_error.assert_called_once()


class TestPerformanceMonitoring(unittest.TestCase):
    """性能监控测试"""
    
    def test_resource_cleanup(self):
        """测试资源清理"""
        # 创建临时资源
        temp_resources = []
        
        class MockResource:
            def __init__(self, name):
                self.name = name
                self.closed = False
                temp_resources.append(self)
            
            def close(self):
                self.closed = True
        
        # 测试资源管理器的清理功能
        resource = MockResource("test")
        with resource_manager(resource):
            self.assertFalse(resource.closed)
        
        # 资源应该被自动关闭
        self.assertTrue(resource.closed)


if __name__ == '__main__':
    unittest.main()
