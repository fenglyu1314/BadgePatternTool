"""
路径工具模块
统一管理项目路径和导入路径设置
"""

import sys
import os
from pathlib import Path


def setup_project_paths():
    """
    设置项目路径，确保可以正确导入项目模块
    这个函数替代了各个模块中重复的路径设置代码
    """
    # 获取项目根目录
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent  # src/common -> src
    
    # 添加src目录到Python路径（如果还没有添加）
    src_path = str(project_root)
    if src_path not in sys.path:
        sys.path.insert(0, src_path)


def get_project_root():
    """获取项目根目录路径"""
    current_file = Path(__file__).resolve()
    return current_file.parent.parent  # src/common -> src


def get_assets_dir():
    """获取资源文件目录路径"""
    return get_project_root() / "assets"


def get_icon_path(icon_name="icon.ico"):
    """获取图标文件路径"""
    assets_dir = get_assets_dir()
    icon_path = assets_dir / icon_name
    
    # 如果ico文件不存在，尝试png文件
    if not icon_path.exists() and icon_name.endswith('.ico'):
        png_path = assets_dir / icon_name.replace('.ico', '.png')
        if png_path.exists():
            return png_path
    
    return icon_path


# 自动设置路径（导入时执行）
setup_project_paths()
