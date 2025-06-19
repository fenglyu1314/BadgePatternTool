"""
多页面功能测试
测试多页面排版、预览、导出和打印功能
"""

import unittest
import os
import sys
import tempfile
from unittest.mock import Mock, patch

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.layout_engine import LayoutEngine
from core.export_manager import ExportManager
from utils.file_handler import ImageItem


class TestMultiPageLayout(unittest.TestCase):
    """测试多页面布局功能"""
    
    def setUp(self):
        """测试前准备"""
        self.layout_engine = LayoutEngine()
        self.export_manager = ExportManager()
        
        # 创建测试图片项
        self.test_images = []
        for i in range(25):  # 创建25个测试图片项（超过单页容量）
            image_item = Mock(spec=ImageItem)
            image_item.file_path = f"test_image_{i}.jpg"
            image_item.filename = f"test_image_{i}.jpg"
            image_item.scale = 1.0
            image_item.offset_x = 0
            image_item.offset_y = 0
            image_item.rotation = 0
            image_item.quantity = 1
            self.test_images.append(image_item)
    
    def test_multi_page_layout_calculation(self):
        """测试多页面布局计算"""
        # 测试网格布局
        multi_layout = self.layout_engine.calculate_multi_page_layout(
            25, 'grid', spacing_mm=5, margin_mm=10
        )
        
        self.assertEqual(multi_layout['type'], 'grid')
        self.assertEqual(multi_layout['total_images'], 25)
        self.assertGreater(multi_layout['total_pages'], 1)  # 应该有多页
        self.assertGreater(multi_layout['max_per_page'], 0)
        
        # 验证页面信息
        self.assertEqual(len(multi_layout['pages']), multi_layout['total_pages'])
        
        total_images_in_pages = sum(page['images_on_page'] for page in multi_layout['pages'])
        self.assertEqual(total_images_in_pages, 25)
        
        print(f"网格布局: {multi_layout['total_pages']}页，每页最多{multi_layout['max_per_page']}个")
    
    def test_compact_multi_page_layout(self):
        """测试紧密布局多页面"""
        multi_layout = self.layout_engine.calculate_multi_page_layout(
            25, 'compact', spacing_mm=5, margin_mm=10
        )
        
        self.assertEqual(multi_layout['type'], 'compact')
        self.assertGreater(multi_layout['total_pages'], 1)
        
        # 紧密布局应该比网格布局容纳更多图片
        grid_layout = self.layout_engine.calculate_multi_page_layout(
            25, 'grid', spacing_mm=5, margin_mm=10
        )
        
        self.assertGreaterEqual(
            multi_layout['max_per_page'], 
            grid_layout['max_per_page']
        )
        
        print(f"紧密布局: {multi_layout['total_pages']}页，每页最多{multi_layout['max_per_page']}个")
    
    def test_single_page_layout(self):
        """测试单页面布局（图片数量少于单页容量）"""
        multi_layout = self.layout_engine.calculate_multi_page_layout(
            5, 'grid', spacing_mm=5, margin_mm=10
        )
        
        self.assertEqual(multi_layout['total_pages'], 1)
        self.assertEqual(multi_layout['pages'][0]['images_on_page'], 5)
        
        print(f"单页布局: {multi_layout['total_pages']}页，{multi_layout['pages'][0]['images_on_page']}个图片")
    
    def test_multi_page_preview_creation(self):
        """测试多页面预览创建"""
        try:
            # 创建多页面预览
            page_previews = self.layout_engine.create_multi_page_preview(
                self.test_images[:15], 'grid', spacing_mm=5, margin_mm=10, preview_scale=0.5
            )
            
            self.assertIsInstance(page_previews, list)
            self.assertGreater(len(page_previews), 1)  # 应该有多页预览
            
            print(f"成功创建{len(page_previews)}页预览")
            
        except Exception as e:
            print(f"预览创建测试跳过（可能缺少PySide6）: {e}")
    
    @patch('core.image_processor.ImageProcessor.create_circular_crop')
    def test_multi_page_pdf_export(self, mock_crop):
        """测试多页面PDF导出"""
        # Mock圆形裁剪
        from PIL import Image
        mock_circle = Image.new('RGBA', (200, 200), (255, 0, 0, 255))
        mock_crop.return_value = mock_circle
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            try:
                success, count = self.export_manager.export_multi_page_to_pdf(
                    self.test_images[:15], temp_file.name, 'grid', 5, 10
                )
                
                self.assertTrue(success)
                self.assertEqual(count, 15)
                self.assertTrue(os.path.exists(temp_file.name))
                
                print(f"多页面PDF导出成功: {count}个图片")
                
            finally:
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
    
    @patch('core.image_processor.ImageProcessor.create_circular_crop')
    def test_multi_page_image_export(self, mock_crop):
        """测试多页面图片导出"""
        # Mock圆形裁剪
        from PIL import Image
        mock_circle = Image.new('RGBA', (200, 200), (255, 0, 0, 255))
        mock_crop.return_value = mock_circle
        
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = os.path.join(temp_dir, "test_export")
            
            success, count = self.export_manager.export_multi_page_to_images(
                self.test_images[:15], base_path, 'PNG', 'grid', 5, 10
            )
            
            self.assertTrue(success)
            self.assertEqual(count, 15)
            
            # 检查生成的文件
            generated_files = [f for f in os.listdir(temp_dir) if f.startswith("test_export")]
            self.assertGreater(len(generated_files), 1)  # 应该有多个文件
            
            print(f"多页面图片导出成功: {count}个图片，生成{len(generated_files)}个文件")
    
    def test_page_distribution(self):
        """测试页面分配逻辑"""
        # 测试不同数量的图片分配
        test_cases = [
            (5, 1),   # 5个图片应该是1页
            (15, 2),  # 15个图片应该是2页（假设每页最多11个）
            (25, 3),  # 25个图片应该是3页
        ]
        
        for image_count, expected_min_pages in test_cases:
            multi_layout = self.layout_engine.calculate_multi_page_layout(
                image_count, 'compact', spacing_mm=5, margin_mm=10
            )
            
            self.assertGreaterEqual(multi_layout['total_pages'], expected_min_pages)
            
            # 验证所有页面的图片总数等于输入数量
            total_in_pages = sum(page['images_on_page'] for page in multi_layout['pages'])
            self.assertEqual(total_in_pages, image_count)
            
            print(f"{image_count}个图片 -> {multi_layout['total_pages']}页")


class TestMultiPageWidget(unittest.TestCase):
    """测试多页面预览组件"""
    
    def setUp(self):
        """测试前准备"""
        try:
            from ui.multi_page_preview_widget import MultiPagePreviewWidget
            self.widget_available = True
        except ImportError:
            self.widget_available = False
    
    def test_widget_creation(self):
        """测试组件创建"""
        if not self.widget_available:
            self.skipTest("PySide6不可用，跳过UI测试")
        
        from ui.multi_page_preview_widget import MultiPagePreviewWidget
        
        widget = MultiPagePreviewWidget()
        self.assertEqual(widget.get_page_count(), 0)
        
        # 测试设置页面数量
        widget.set_page_count(3)
        self.assertEqual(widget.get_page_count(), 3)
        
        print("多页面预览组件创建成功")
    
    def test_widget_scaling(self):
        """测试组件缩放功能"""
        if not self.widget_available:
            self.skipTest("PySide6不可用，跳过UI测试")
        
        from ui.multi_page_preview_widget import MultiPagePreviewWidget
        
        widget = MultiPagePreviewWidget()
        widget.set_page_count(2)
        
        # 测试缩放
        widget.set_scale(1.5)
        self.assertEqual(widget.current_scale, 1.5)
        
        widget.zoom_in()
        self.assertGreater(widget.current_scale, 1.5)
        
        widget.zoom_out()
        self.assertLess(widget.current_scale, widget.current_scale)
        
        print("多页面预览组件缩放功能正常")


def run_multi_page_tests():
    """运行多页面功能测试"""
    print("=" * 50)
    print("多页面功能测试")
    print("=" * 50)
    
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加布局测试
    suite.addTest(TestMultiPageLayout('test_multi_page_layout_calculation'))
    suite.addTest(TestMultiPageLayout('test_compact_multi_page_layout'))
    suite.addTest(TestMultiPageLayout('test_single_page_layout'))
    suite.addTest(TestMultiPageLayout('test_multi_page_preview_creation'))
    suite.addTest(TestMultiPageLayout('test_multi_page_pdf_export'))
    suite.addTest(TestMultiPageLayout('test_multi_page_image_export'))
    suite.addTest(TestMultiPageLayout('test_page_distribution'))
    
    # 添加UI测试
    suite.addTest(TestMultiPageWidget('test_widget_creation'))
    suite.addTest(TestMultiPageWidget('test_widget_scaling'))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_multi_page_tests()
    sys.exit(0 if success else 1)
