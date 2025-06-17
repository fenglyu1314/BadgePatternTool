#!/usr/bin/env python3
"""
交互式图片编辑器测试
测试新的交互式编辑功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPixmap
from src.ui.interactive_image_editor import InteractiveImageEditor
from PIL import Image, ImageDraw


def create_test_image():
    """创建测试图片"""
    # 创建一个测试图片
    img = Image.new('RGB', (400, 300), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # 绘制一些图案
    draw.rectangle([50, 50, 150, 150], fill='red', outline='darkred', width=3)
    draw.ellipse([200, 100, 350, 250], fill='green', outline='darkgreen', width=3)
    draw.text((160, 20), "Test Image", fill='black')
    draw.text((160, 260), "Interactive Editor", fill='black')
    
    # 保存测试图片
    test_image_path = project_root / "test_interactive_editor.png"
    img.save(test_image_path)
    return str(test_image_path)


class TestWindow(QMainWindow):
    """测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("交互式图片编辑器测试")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 添加说明标签
        info_label = QLabel("""
交互式图片编辑器测试

功能测试：
1. 点击"加载测试图片"按钮
2. 使用鼠标拖拽移动图片
3. 使用滚轮缩放图片
4. 观察圆形遮罩效果
5. 查看参数变化

预期效果：
- 显示完整的测试图片
- 圆形遮罩居中显示
- 圆形外部区域变暗
- 白色虚线边框
- 中心十字线
        """)
        info_label.setStyleSheet("color: #666; font-size: 12px; padding: 10px;")
        layout.addWidget(info_label)
        
        # 创建交互式编辑器
        self.editor = InteractiveImageEditor()
        self.editor.setFixedSize(400, 300)
        layout.addWidget(self.editor)
        
        # 连接信号
        self.editor.parameters_changed.connect(self.on_parameters_changed)
        
        # 参数显示标签
        self.params_label = QLabel("参数: 未加载图片")
        self.params_label.setStyleSheet("font-family: monospace; background: #f0f0f0; padding: 5px;")
        layout.addWidget(self.params_label)
        
        # 控制按钮
        button_layout = QVBoxLayout()
        
        load_btn = QPushButton("加载测试图片")
        load_btn.clicked.connect(self.load_test_image)
        button_layout.addWidget(load_btn)
        
        reset_btn = QPushButton("重置视图")
        reset_btn.clicked.connect(self.reset_view)
        button_layout.addWidget(reset_btn)
        
        test_params_btn = QPushButton("测试参数设置")
        test_params_btn.clicked.connect(self.test_parameters)
        button_layout.addWidget(test_params_btn)
        
        layout.addLayout(button_layout)
        
        # 创建测试图片
        self.test_image_path = create_test_image()
        print(f"测试图片已创建: {self.test_image_path}")
    
    def load_test_image(self):
        """加载测试图片"""
        success = self.editor.load_image(self.test_image_path)
        if success:
            print("✅ 测试图片加载成功")
            self.params_label.setText("图片已加载，可以开始测试交互功能")
        else:
            print("❌ 测试图片加载失败")
            self.params_label.setText("图片加载失败")
    
    def reset_view(self):
        """重置视图"""
        self.editor.reset_view()
        print("🔄 视图已重置")
    
    def test_parameters(self):
        """测试参数设置"""
        if self.editor.original_image:
            # 测试不同的参数组合
            test_cases = [
                (1.5, 50, 30),   # 放大 + 右下偏移
                (0.8, -40, -20), # 缩小 + 左上偏移
                (2.0, 0, 0),     # 大幅放大 + 居中
                (0.5, 0, 50),    # 缩小 + 下偏移
            ]
            
            import time
            for i, (scale, offset_x, offset_y) in enumerate(test_cases):
                print(f"🧪 测试参数组合 {i+1}: scale={scale}, offset=({offset_x}, {offset_y})")
                self.editor.set_parameters(scale, offset_x, offset_y)
                QApplication.processEvents()  # 更新界面
                time.sleep(1)  # 暂停1秒观察效果
            
            print("✅ 参数测试完成")
        else:
            print("⚠️ 请先加载图片")
    
    def on_parameters_changed(self, scale, offset_x, offset_y):
        """参数改变事件"""
        params_text = f"缩放: {scale:.2f} | X偏移: {offset_x} | Y偏移: {offset_y}"
        self.params_label.setText(params_text)
        print(f"📊 参数更新: {params_text}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 清理测试图片
        try:
            if os.path.exists(self.test_image_path):
                os.remove(self.test_image_path)
                print(f"🗑️ 测试图片已清理: {self.test_image_path}")
        except Exception as e:
            print(f"清理测试图片失败: {e}")
        
        event.accept()


def test_editor_functionality():
    """测试编辑器功能"""
    print("🧪 开始交互式图片编辑器功能测试")
    
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = TestWindow()
    window.show()
    
    print("""
🎯 测试指南:

1. 基本功能测试:
   - 点击"加载测试图片"
   - 观察图片是否正确显示
   - 检查圆形遮罩是否居中
   - 验证暗化效果是否正确

2. 交互功能测试:
   - 在图片上拖拽鼠标移动图片
   - 使用滚轮缩放图片
   - 观察光标变化
   - 检查参数实时更新

3. 边界测试:
   - 测试最大/最小缩放
   - 测试极限偏移位置
   - 验证参数范围限制

4. 性能测试:
   - 快速拖拽和缩放
   - 观察响应速度
   - 检查内存使用

按 Ctrl+C 或关闭窗口结束测试
    """)
    
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
        sys.exit(0)


if __name__ == "__main__":
    test_editor_functionality()
