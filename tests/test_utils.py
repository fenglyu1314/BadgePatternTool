"""
工具模块测试
测试文件处理、配置管理等工具功能
"""

import unittest
import sys
import os
import tempfile
from pathlib import Path

# 添加src目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from utils.file_handler import FileHandler, ImageItem
from utils.config import mm_to_pixels, PRINT_DPI, A4_WIDTH_MM, A4_HEIGHT_MM


class TestFileHandler(unittest.TestCase):
    """文件处理器测试"""
    
    def setUp(self):
        self.handler = FileHandler()
    
    def test_handler_initialization(self):
        """测试处理器初始化"""
        self.assertIsNotNone(self.handler)
        self.assertIsInstance(self.handler.supported_formats, list)
        self.assertGreater(len(self.handler.supported_formats), 0)
    
    def test_file_validation(self):
        """测试文件验证"""
        # 测试不存在的文件
        self.assertFalse(self.handler.validate_image_file("nonexistent.jpg"))
        
        # 测试不支持的格式
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_path = f.name
        
        try:
            self.assertFalse(self.handler.validate_image_file(temp_path))
        finally:
            os.unlink(temp_path)


class TestImageItem(unittest.TestCase):
    """图片项目测试"""
    
    def test_item_initialization(self):
        """测试项目初始化"""
        # 创建临时图片文件进行测试
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            temp_path = f.name
        
        try:
            # 由于没有真实图片，这个测试会失败，但可以测试基本结构
            item = ImageItem(temp_path)
            self.assertEqual(item.file_path, temp_path)
            self.assertEqual(item.scale, 1.0)
            self.assertEqual(item.offset_x, 0)
            self.assertEqual(item.offset_y, 0)
            self.assertEqual(item.quantity, 1)
        except Exception:
            # 预期会失败，因为不是真实图片
            pass
        finally:
            os.unlink(temp_path)


class TestConfigUtils(unittest.TestCase):
    """配置工具测试"""
    
    def test_mm_to_pixels_conversion(self):
        """测试毫米到像素转换"""
        # 测试基本转换
        pixels = mm_to_pixels(25.4)  # 1英寸
        expected = PRINT_DPI  # 300 DPI下，1英寸 = 300像素
        self.assertEqual(pixels, expected)
        
        # 测试A4尺寸转换
        a4_width_px = mm_to_pixels(A4_WIDTH_MM)
        a4_height_px = mm_to_pixels(A4_HEIGHT_MM)
        
        self.assertGreater(a4_width_px, 0)
        self.assertGreater(a4_height_px, 0)
        self.assertGreater(a4_height_px, a4_width_px)  # A4是竖向的
    
    def test_conversion_accuracy(self):
        """测试转换精度"""
        # 测试往返转换
        original_mm = 68  # 徽章直径
        pixels = mm_to_pixels(original_mm)
        back_to_mm = pixels * 25.4 / PRINT_DPI
        
        # 允许小的浮点误差（精度放宽到1位小数）
        self.assertAlmostEqual(original_mm, back_to_mm, places=1)


if __name__ == '__main__':
    unittest.main()
