"""
核心功能测试模块
测试图片处理、排版引擎、导出管理等核心功能
"""

import unittest
import sys
import os
from pathlib import Path

# 添加src目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from core.image_processor import ImageProcessor
from core.layout_engine import LayoutEngine
from core.export_manager import ExportManager
from utils.config import app_config


class TestImageProcessor(unittest.TestCase):
    """图片处理器测试"""
    
    def setUp(self):
        self.processor = ImageProcessor()
    
    def test_processor_initialization(self):
        """测试处理器初始化"""
        self.assertIsNotNone(self.processor)
        self.assertGreater(self.processor.badge_diameter_px, 0)
        self.assertGreater(self.processor.badge_radius_px, 0)
    
    def test_optimal_scale_calculation(self):
        """测试最佳缩放比例计算"""
        # 这里需要一个测试图片，暂时跳过
        pass


class TestLayoutEngine(unittest.TestCase):
    """排版引擎测试"""
    
    def setUp(self):
        self.engine = LayoutEngine()
    
    def test_engine_initialization(self):
        """测试引擎初始化"""
        self.assertIsNotNone(self.engine)
        self.assertGreater(self.engine.a4_width_px, 0)
        self.assertGreater(self.engine.a4_height_px, 0)
    
    def test_grid_layout_calculation(self):
        """测试网格布局计算"""
        layout = self.engine.calculate_grid_layout(spacing_mm=5, margin_mm=10)
        
        self.assertEqual(layout['type'], 'grid')
        self.assertIn('positions', layout)
        self.assertIn('max_count', layout)
        self.assertGreater(layout['max_count'], 0)
        self.assertIsInstance(layout['positions'], list)
    
    def test_compact_layout_calculation(self):
        """测试紧密布局计算"""
        layout = self.engine.calculate_compact_layout(spacing_mm=5, margin_mm=10)
        
        self.assertEqual(layout['type'], 'compact')
        self.assertIn('positions', layout)
        self.assertIn('max_count', layout)
        self.assertGreater(layout['max_count'], 0)
        self.assertIsInstance(layout['positions'], list)
    
    def test_layout_info(self):
        """测试布局信息获取"""
        info = self.engine.get_layout_info('grid', 5, 10)
        
        self.assertEqual(info['type'], 'grid')
        self.assertEqual(info['spacing_mm'], 5)
        self.assertEqual(info['margin_mm'], 10)
        self.assertGreater(info['max_count'], 0)


class TestExportManager(unittest.TestCase):
    """导出管理器测试"""
    
    def setUp(self):
        self.manager = ExportManager()
    
    def test_manager_initialization(self):
        """测试管理器初始化"""
        self.assertIsNotNone(self.manager)
        self.assertIsNotNone(self.manager.layout_engine)
        self.assertIsNotNone(self.manager.image_processor)
    
    def test_suggested_filename(self):
        """测试建议文件名生成"""
        filename = self.manager.get_suggested_filename('PDF', 'grid')
        
        self.assertIsInstance(filename, str)
        self.assertTrue(filename.endswith('.pdf'))
        self.assertIn('网格', filename)
    
    def test_export_validation(self):
        """测试导出设置验证"""
        # 测试空图片列表
        valid, error = self.manager.validate_export_settings([], "test.pdf")
        self.assertFalse(valid)
        self.assertIn("没有可导出的图片", error)
        
        # 测试空输出路径
        valid, error = self.manager.validate_export_settings([1], "")
        self.assertFalse(valid)
        self.assertIn("请指定输出文件路径", error)


class TestConfig(unittest.TestCase):
    """配置管理测试"""
    
    def test_config_initialization(self):
        """测试配置初始化"""
        self.assertIsNotNone(app_config)
        self.assertGreater(app_config.badge_diameter_mm, 0)
        self.assertGreater(app_config.badge_diameter_px, 0)
    
    def test_config_update(self):
        """测试配置更新"""
        original_diameter = app_config.badge_diameter_mm
        
        # 更新配置
        app_config.badge_diameter_mm = 50
        self.assertEqual(app_config.badge_diameter_mm, 50)
        
        # 恢复原始值
        app_config.badge_diameter_mm = original_diameter


if __name__ == '__main__':
    unittest.main()
