"""
BadgePatternTool 主程序入口
徽章图案工具 - 用于制作徽章的图片处理和排版工具
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config import APP_NAME, APP_VERSION
from ui.main_window import MainWindow

def main():
    """主程序入口"""
    try:
        # 创建应用程序
        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion(APP_VERSION)

        # 设置应用程序属性（PySide6中这些属性已默认启用）
        # app.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # 已弃用
        # app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)     # 已弃用

        # 创建主窗口
        main_window = MainWindow()
        main_window.show()

        # 启动事件循环
        sys.exit(app.exec())

    except Exception as e:
        # 如果QApplication还没创建，先创建一个临时的
        if not QApplication.instance():
            QApplication(sys.argv)

        QMessageBox.critical(None, "错误", f"程序启动失败：{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
