#!/usr/bin/env python3
"""
测试圆形裁切导出功能
"""

def test_circle_export():
    """测试圆形裁切导出"""
    try:
        from PIL import Image, ImageDraw
        from src.core.export_manager import ExportManager
        from src.utils.file_handler import ImageItem
        from src.utils.config import app_config
        import os
        
        # 设置68mm配置
        app_config.badge_diameter_mm = 68
        
        # 创建一个测试图片（彩色方块）
        test_img_path = "test_square.png"
        img_size = 400
        test_img = Image.new('RGB', (img_size, img_size), (255, 255, 255))
        draw = ImageDraw.Draw(test_img)
        
        # 绘制彩色方块
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        block_size = img_size // 2
        for i, color in enumerate(colors):
            x = (i % 2) * block_size
            y = (i // 2) * block_size
            draw.rectangle([x, y, x + block_size, y + block_size], fill=color)
        
        test_img.save(test_img_path)
        print(f"创建测试图片: {test_img_path}")
        
        # 创建图片项目
        image_item = ImageItem(test_img_path)
        image_item.scale = 1.0
        image_item.offset_x = 0
        image_item.offset_y = 0
        image_item.rotation = 0
        image_item.quantity = 1
        image_item.is_processed = True
        
        # 创建导出管理器
        export_manager = ExportManager()
        
        # 测试PNG导出
        output_path = "test_circle_output.png"
        success, count = export_manager.export_to_image(
            [image_item], output_path, "PNG", "grid", 5, 10
        )
        
        if success:
            print(f"✅ 圆形导出成功，处理了 {count} 张图片")
            
            # 检查输出图片
            if os.path.exists(output_path):
                with Image.open(output_path) as result_img:
                    print(f"   输出图片尺寸: {result_img.size}")
                    print(f"   输出图片模式: {result_img.mode}")
                    
                    # 检查圆形区域
                    # 获取圆心位置（应该在第一个位置）
                    layout = export_manager.layout_engine.calculate_grid_layout(5, 10)
                    if layout['positions']:
                        center_x, center_y = layout['positions'][0]
                        radius = export_manager.layout_engine.badge_radius_px
                        
                        print(f"   圆心位置: ({center_x}, {center_y})")
                        print(f"   圆形半径: {radius}px")
                        
                        # 检查圆形边缘的像素（应该是白色背景）
                        edge_x = center_x + radius - 1
                        edge_y = center_y
                        
                        if edge_x < result_img.width and edge_y < result_img.height:
                            edge_pixel = result_img.getpixel((edge_x, edge_y))
                            print(f"   圆形边缘像素: {edge_pixel}")
                            
                            # 检查圆形外部的像素（应该是白色背景）
                            outside_x = center_x + radius + 10
                            outside_y = center_y
                            
                            if outside_x < result_img.width:
                                outside_pixel = result_img.getpixel((outside_x, outside_y))
                                print(f"   圆形外部像素: {outside_pixel}")
                                
                                # 判断是否正确裁切
                                if outside_pixel == (255, 255, 255):
                                    print("✅ 圆形裁切正确：圆形外部为白色背景")
                                else:
                                    print("⚠️ 圆形裁切可能有问题：圆形外部不是白色背景")
                            
                        # 检查圆心的像素（应该是彩色）
                        center_pixel = result_img.getpixel((center_x, center_y))
                        print(f"   圆心像素: {center_pixel}")
                        
                        if center_pixel != (255, 255, 255):
                            print("✅ 圆形内容正确：圆心有彩色内容")
                        else:
                            print("⚠️ 圆形内容可能有问题：圆心是白色")
                
                print(f"   输出文件已保存: {output_path}")
            else:
                print("❌ 输出文件未生成")
        else:
            print("❌ 圆形导出失败")
        
        # 清理测试文件
        if os.path.exists(test_img_path):
            os.remove(test_img_path)
            print(f"清理测试文件: {test_img_path}")
        
        return success
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_circle_export()
