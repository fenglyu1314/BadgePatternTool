"""
BadgePatternTool 主程序入口
徽章图案工具 - 用于制作徽章的图片处理和排版工具
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# 添加src目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config import APP_NAME, APP_VERSION, APP_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT
from ui.main_window import MainWindow

def main():
    """主程序入口"""
    try:
        # 创建主窗口
        root = tk.Tk()

        # 创建主界面
        app = MainWindow(root)

        # 启动主循环
        root.mainloop()

    except Exception as e:
        messagebox.showerror("错误", f"程序启动失败：{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
