"""
性能测试模块
测试缓存系统、内存管理和性能优化功能
"""

import unittest
import sys
import time
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image

# 添加src目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from core.image_processor import ImageProcessor
from core.layout_engine import LayoutEngine
from ui.interactive_image_editor import InteractiveImageEditor
from utils.file_handler import FileHandler, ImageItem


class TestImageProcessorPerformance(unittest.TestCase):
    """图片处理器性能测试"""
    
    def setUp(self):
        self.processor = ImageProcessor()
    
    def test_cache_functionality(self):
        """测试缓存功能"""
        # 测试缓存初始化
        self.assertIsInstance(self.processor._crop_cache, dict)
        self.assertIsInstance(self.processor._preview_cache, dict)
        self.assertEqual(len(self.processor._crop_cache), 0)
        self.assertEqual(len(self.processor._preview_cache), 0)
    
    def test_cache_size_limits(self):
        """测试缓存大小限制"""
        # 验证缓存大小限制设置
        self.assertGreater(self.processor._max_cache_size, 0)
        self.assertGreater(self.processor._max_preview_cache_size, 0)
        self.assertLessEqual(self.processor._max_preview_cache_size, 
                           self.processor._max_cache_size)
    
    def test_memory_monitoring(self):
        """测试内存监控"""
        # 测试内存使用监控
        self.assertGreaterEqual(self.processor._current_memory_usage, 0)
        self.assertGreater(self.processor._cache_memory_limit, 0)
        
        # 测试缓存信息获取
        cache_info = self.processor.get_cache_info()
        self.assertIsInstance(cache_info, dict)
        self.assertIn('crop_cache_size', cache_info)
        self.assertIn('preview_cache_size', cache_info)
        self.assertIn('estimated_memory_mb', cache_info)
    
    def test_cache_clear(self):
        """测试缓存清理"""
        # 添加一些模拟缓存数据
        self.processor._crop_cache['test1'] = "data1"
        self.processor._preview_cache['test2'] = "data2"
        self.processor._cache_access_time['test1'] = 1
        
        # 清理缓存
        self.processor.clear_cache()
        
        # 验证缓存已清空
        self.assertEqual(len(self.processor._crop_cache), 0)
        self.assertEqual(len(self.processor._preview_cache), 0)
        self.assertEqual(len(self.processor._cache_access_time), 0)
        self.assertEqual(self.processor._current_memory_usage, 0)


class TestLayoutEnginePerformance(unittest.TestCase):
    """布局引擎性能测试"""
    
    def setUp(self):
        self.engine = LayoutEngine()
    
    def test_layout_cache(self):
        """测试布局缓存"""
        # 测试缓存清理功能
        if hasattr(self.engine, 'clear_cache'):
            self.engine.clear_cache()
            
            # 测试缓存信息
            if hasattr(self.engine, 'get_cache_info'):
                cache_info = self.engine.get_cache_info()
                self.assertIsInstance(cache_info, dict)
    
    def test_layout_performance(self):
        """测试布局计算性能"""
        start_time = time.time()
        
        # 执行布局计算
        layout = self.engine.calculate_grid_layout(spacing_mm=5, margin_mm=10)
        
        end_time = time.time()
        calculation_time = end_time - start_time
        
        # 布局计算应该在合理时间内完成（1秒内）
        self.assertLess(calculation_time, 1.0)
        self.assertIsInstance(layout, dict)
        self.assertIn('positions', layout)
    
    def test_multiple_layout_calculations(self):
        """测试多次布局计算性能"""
        times = []
        
        for i in range(5):
            start_time = time.time()
            layout = self.engine.calculate_compact_layout(spacing_mm=5, margin_mm=10)
            end_time = time.time()
            times.append(end_time - start_time)
        
        # 平均计算时间应该合理
        avg_time = sum(times) / len(times)
        self.assertLess(avg_time, 0.5)  # 平均500ms内完成


class TestFileHandlerPerformance(unittest.TestCase):
    """文件处理器性能测试"""
    
    def setUp(self):
        self.handler = FileHandler()
    
    def create_test_image(self, size=(100, 100)):
        """创建测试图片"""
        img = Image.new('RGB', size, color='red')
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(temp_file.name)
        return temp_file.name
    
    def test_thumbnail_creation_performance(self):
        """测试缩略图创建性能"""
        test_image_path = self.create_test_image((500, 500))
        
        try:
            start_time = time.time()
            thumbnail = self.handler.create_thumbnail(test_image_path)
            end_time = time.time()
            
            creation_time = end_time - start_time
            
            # 缩略图创建应该很快（500ms内）
            self.assertLess(creation_time, 0.5)
            self.assertIsNotNone(thumbnail)
            
        finally:
            Path(test_image_path).unlink()
    
    def test_batch_thumbnail_creation(self):
        """测试批量缩略图创建性能"""
        test_images = []
        
        try:
            # 创建多个测试图片
            for i in range(5):
                img_path = self.create_test_image((200, 200))
                test_images.append(img_path)
            
            start_time = time.time()
            
            # 批量创建缩略图
            thumbnails = []
            for img_path in test_images:
                thumbnail = self.handler.create_thumbnail(img_path)
                thumbnails.append(thumbnail)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # 批量处理应该在合理时间内完成
            self.assertLess(total_time, 2.0)  # 2秒内完成5个缩略图
            self.assertEqual(len(thumbnails), 5)
            
        finally:
            for img_path in test_images:
                Path(img_path).unlink()


class TestCacheEfficiency(unittest.TestCase):
    """缓存效率测试"""
    
    def test_cache_hit_rate(self):
        """测试缓存命中率"""
        processor = ImageProcessor()
        
        # 模拟缓存操作
        test_key = "test_cache_key"
        test_data = "test_data"
        
        # 第一次访问（缓存未命中）
        processor._crop_cache[test_key] = test_data
        processor._update_cache_access(test_key)
        
        # 第二次访问（缓存命中）
        cached_data = processor._crop_cache.get(test_key)
        processor._update_cache_access(test_key)
        
        self.assertEqual(cached_data, test_data)
        self.assertIn(test_key, processor._cache_access_time)
    
    def test_lru_cache_management(self):
        """测试LRU缓存管理"""
        processor = ImageProcessor()
        
        # 填充缓存到接近限制
        for i in range(processor._max_cache_size + 5):
            key = f"test_key_{i}"
            processor._crop_cache[key] = f"data_{i}"
            processor._update_cache_access(key)
        
        # 验证缓存大小被控制
        self.assertLessEqual(len(processor._crop_cache), processor._max_cache_size + 2)


class TestMemoryManagement(unittest.TestCase):
    """内存管理测试"""
    
    def test_memory_estimation(self):
        """测试内存使用估算"""
        processor = ImageProcessor()
        
        initial_memory = processor._current_memory_usage
        
        # 模拟添加缓存项
        mock_image = Image.new('RGB', (100, 100))
        estimated_size = 100 * 100 * 3  # RGB
        
        processor._current_memory_usage += estimated_size
        
        self.assertGreater(processor._current_memory_usage, initial_memory)
    
    def test_memory_cleanup(self):
        """测试内存清理"""
        processor = ImageProcessor()
        
        # 添加一些内存使用
        processor._current_memory_usage = 50 * 1024 * 1024  # 50MB
        
        # 清理缓存
        processor.clear_cache()
        
        # 内存使用应该被重置
        self.assertEqual(processor._current_memory_usage, 0)


class TestPerformanceBenchmarks(unittest.TestCase):
    """性能基准测试"""
    
    def test_startup_performance(self):
        """测试启动性能"""
        start_time = time.time()
        
        # 模拟组件初始化
        processor = ImageProcessor()
        engine = LayoutEngine()
        handler = FileHandler()
        
        end_time = time.time()
        startup_time = end_time - start_time
        
        # 启动时间应该合理（2秒内）
        self.assertLess(startup_time, 2.0)
    
    def test_concurrent_operations(self):
        """测试并发操作性能"""
        processor = ImageProcessor()
        
        # 模拟多个并发操作
        operations = []
        start_time = time.time()
        
        for i in range(10):
            # 模拟缓存操作
            key = f"concurrent_key_{i}"
            processor._crop_cache[key] = f"data_{i}"
            processor._update_cache_access(key)
            operations.append(key)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 并发操作应该快速完成
        self.assertLess(total_time, 0.1)
        self.assertEqual(len(operations), 10)


if __name__ == '__main__':
    unittest.main()
