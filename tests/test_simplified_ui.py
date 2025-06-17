#!/usr/bin/env python3
"""
简化界面测试
验证去除分组框后的界面效果
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow


def test_simplified_ui():
    """测试简化后的界面"""
    print("🧪 开始简化界面测试")
    
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    print("""
🎯 界面简化验证清单:

✅ 单图编辑区域检查:
   - 交互式编辑器直接显示（无"交互式编辑"框框）
   - 编辑器尺寸增加到320x320
   - 控件直接排列（无"编辑控制"框框）

✅ 控件布局检查:
   - 缩放标签和滑块直接显示
   - X偏移标签和滑块直接显示  
   - Y偏移标签和滑块直接显示
   - 数量控制在一行显示
   - 操作按钮在一行显示

✅ 样式效果检查:
   - 标签使用加粗字体
   - 适当的间距分隔功能区域
   - 快速设置按钮紧凑排列
   - 整体界面简洁清爽

✅ 功能完整性检查:
   - 导入图片功能正常
   - 交互式编辑器功能正常
   - 滑块控制功能正常
   - 双向同步功能正常
   - 数量设置功能正常
   - 重置和应用功能正常

🎨 界面对比:
   修改前: 7个分组框，4层嵌套，界面繁琐
   修改后: 1个分组框，扁平布局，界面简洁

📋 测试步骤:
1. 观察单图编辑区域的整体布局
2. 检查是否还有多余的分组框
3. 验证交互式编辑器是否正常显示
4. 测试所有编辑功能是否正常工作
5. 确认界面是否更加简洁清爽

按 Ctrl+C 或关闭窗口结束测试
    """)
    
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
        sys.exit(0)


if __name__ == "__main__":
    test_simplified_ui()
