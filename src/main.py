"""
BadgePatternTool 主程序入口
徽章图案工具 - 用于制作徽章的图片处理和排版工具
"""

import sys

# 导入公共模块（自动设置路径）
from common.path_utils import get_icon_path
from common.imports import QApplication, QMessageBox, QIcon, check_required_dependencies
from common.error_handler import show_error_message, logger

from utils.config import APP_NAME, APP_VERSION
from ui.main_window import MainWindow

def main():
    """主程序入口"""
    try:
        # 检查必需的依赖
        check_required_dependencies()

        # 创建应用程序
        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion(APP_VERSION)

        # 设置应用程序图标（用于任务栏和窗口）
        try:
            icon_path = get_icon_path("icon.ico")
            if icon_path.exists():
                icon = QIcon(str(icon_path))
                if not icon.isNull():
                    app.setWindowIcon(icon)
                    logger.info(f"应用程序图标加载成功: {icon_path.name}")
                else:
                    logger.warning("图标文件无效")
            else:
                logger.warning("未找到应用程序图标文件")
        except Exception as e:
            logger.error(f"设置应用程序图标失败: {e}")

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

        show_error_message("启动错误", f"程序启动失败：{str(e)}")
        logger.error(f"程序启动失败: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
