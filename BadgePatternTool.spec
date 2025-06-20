# -*- mode: python ; coding: utf-8 -*-
"""
BadgePatternTool PyInstaller 配置文件
优化版本 - 减小文件大小，提高性能

项目负责人: 喵喵mya (231750570@qq.com)
版本: v1.5.6
"""

import sys
import os
from pathlib import Path

# 项目路径 - 使用当前工作目录而不是__file__
project_root = Path(os.getcwd())
src_path = project_root / "src"

# 分析主脚本
a = Analysis(
    [str(src_path / "main.py")],
    pathex=[str(project_root), str(src_path)],
    binaries=[],
    datas=[
        # 只包含必需的资源文件
        (str(src_path / "assets" / "icon.ico"), "assets"),
        (str(src_path / "assets" / "icon.png"), "assets"),
    ],
    hiddenimports=[
        # PySide6 核心模块
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'PySide6.QtPrintSupport',
        
        # PIL 核心模块
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageTk',
        'PIL._tkinter_finder',
        
        # ReportLab 核心模块
        'reportlab.pdfgen.canvas',
        'reportlab.lib.pagesizes',
        
        # 项目模块
        'common.imports',
        'common.constants',
        'common.path_utils',
        'common.error_handler',
        'utils.config',
        'utils.file_handler',
        'core.image_processor',
        'core.layout_engine', 
        'core.export_manager',
        'ui.main_window',
        'ui.interactive_preview_label',
        'ui.interactive_image_editor',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不必要的模块以减小文件大小
        'tkinter',
        'matplotlib',
        'scipy',
        'pandas',
        'numpy.testing',
        'jupyter',
        'IPython',
        'test',
        'unittest',
        'doctest',
        'pydoc',
        # 注意：不能排除以下模块，因为reportlab需要它们
        # 'xml',
        # 'xmlrpc',
        # 'email',
        # 'http',
        # 'urllib3',
        # 'ssl',
        # 'socket',
        'requests',
        'sqlite3',
        'asyncio',
        'multiprocessing',
        'concurrent',
        'distutils',
        'setuptools',
        'pkg_resources',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 移除不必要的文件
def remove_unnecessary_files(a):
    """移除不必要的文件以减小大小"""
    excludes = [
        'api-ms-win-',
        'ucrtbase.dll',
        'msvcp140.dll',
        'vcruntime140.dll',
        'Qt6Network',
        'Qt6Sql',
        'Qt6Test',
        'Qt6Quick',
        'Qt6Qml',
        'Qt6WebEngine',
        'Qt6Multimedia',
        'Qt6OpenGL',
        'Qt63D',
        'Qt6Charts',
        'Qt6DataVisualization',
        'Qt6Designer',
        'Qt6Help',
        'Qt6Location',
        'Qt6Positioning',
        'Qt6Sensors',
        'Qt6SerialPort',
        'Qt6WebChannel',
        'Qt6WebSockets',
        'Qt6Xml',
        'Qt6XmlPatterns',
        'opengl32sw.dll',
        'libEGL.dll',
        'libGLESv2.dll',
        'd3dcompiler_47.dll',
    ]
    
    # 过滤二进制文件
    a.binaries = [x for x in a.binaries if not any(exclude in x[0] for exclude in excludes)]
    
    # 过滤数据文件
    excludes_data = [
        'translations',
        'qml',
        'examples',
        'doc',
        'include',
        'mkspecs',
        'plugins/platforms/qminimal',
        'plugins/platforms/qoffscreen',
        'plugins/imageformats/qico',
        'plugins/imageformats/qicns',
        'plugins/imageformats/qtga',
        'plugins/imageformats/qtiff',
        'plugins/imageformats/qwbmp',
        'plugins/imageformats/qwebp',
    ]
    
    a.datas = [x for x in a.datas if not any(exclude in x[0] for exclude in excludes_data)]

# 应用优化
remove_unnecessary_files(a)

# 创建PYZ文件
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 创建可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BadgePatternTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # 去除调试信息
    upx=False,   # 禁用UPX压缩（避免兼容性问题）
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 无控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(src_path / "assets" / "icon.ico") if (src_path / "assets" / "icon.ico").exists() else None,
    version_file=None,
)
