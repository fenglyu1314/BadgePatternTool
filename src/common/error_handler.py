"""
错误处理模块
提供统一的错误处理、日志记录和用户友好的错误提示
"""

import sys
import traceback
import logging
from typing import Optional, Callable, Any
from contextlib import contextmanager
from functools import wraps

# 尝试导入PySide6，如果不可用则使用None
try:
    from PySide6.QtWidgets import QMessageBox
    PYSIDE6_AVAILABLE = True
except ImportError:
    QMessageBox = None
    PYSIDE6_AVAILABLE = False


class BadgeToolError(Exception):
    """BadgePatternTool基础异常类"""
    pass


class ImageProcessingError(BadgeToolError):
    """图片处理相关错误"""
    pass


class LayoutError(BadgeToolError):
    """排版相关错误"""
    pass


class ExportError(BadgeToolError):
    """导出相关错误"""
    pass


class ConfigError(BadgeToolError):
    """配置相关错误"""
    pass


def setup_logging(log_level=logging.INFO):
    """设置日志记录"""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger('BadgePatternTool')


logger = setup_logging()


def show_error_message(title: str, message: str, parent=None):
    """显示错误消息框"""
    if PYSIDE6_AVAILABLE and QMessageBox:
        QMessageBox.critical(parent, title, message)
    else:
        print(f"ERROR - {title}: {message}")


def show_warning_message(title: str, message: str, parent=None):
    """显示警告消息框"""
    if PYSIDE6_AVAILABLE and QMessageBox:
        QMessageBox.warning(parent, title, message)
    else:
        print(f"WARNING - {title}: {message}")


def show_info_message(title: str, message: str, parent=None):
    """显示信息消息框"""
    if PYSIDE6_AVAILABLE and QMessageBox:
        QMessageBox.information(parent, title, message)
    else:
        print(f"INFO - {title}: {message}")


def handle_exception(exc_type, exc_value, exc_traceback, show_dialog=True):
    """全局异常处理器"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    error_msg = f"未处理的异常: {exc_type.__name__}: {exc_value}"
    logger.error(error_msg, exc_info=(exc_type, exc_value, exc_traceback))
    
    if show_dialog:
        detailed_msg = f"{error_msg}\n\n详细信息:\n{''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))}"
        show_error_message("程序错误", detailed_msg)


def safe_execute(func: Callable, error_message: str = "操作失败", 
                show_error: bool = True, default_return: Any = None):
    """安全执行函数，捕获异常并显示友好错误信息"""
    try:
        return func()
    except Exception as e:
        logger.error(f"{error_message}: {e}", exc_info=True)
        if show_error:
            show_error_message("错误", f"{error_message}: {str(e)}")
        return default_return


def error_handler(error_message: str = "操作失败", show_error: bool = True, 
                 default_return: Any = None):
    """错误处理装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"{error_message} in {func.__name__}: {e}", exc_info=True)
                if show_error:
                    show_error_message("错误", f"{error_message}: {str(e)}")
                return default_return
        return wrapper
    return decorator


@contextmanager
def resource_manager(resource, cleanup_func: Optional[Callable] = None):
    """资源管理上下文管理器"""
    try:
        yield resource
    finally:
        try:
            if cleanup_func:
                cleanup_func(resource)
            elif hasattr(resource, 'close'):
                resource.close()
            elif hasattr(resource, '__exit__'):
                resource.__exit__(None, None, None)
        except Exception as e:
            logger.warning(f"资源清理失败: {e}")


# 设置全局异常处理器
sys.excepthook = handle_exception


def cleanup_resources():
    """清理资源的函数"""
    try:
        # 清理日志处理器
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
        logger.info("资源清理完成")
    except Exception as e:
        print(f"资源清理失败: {e}")


# 注册程序退出时的清理函数
import atexit
atexit.register(cleanup_resources)
