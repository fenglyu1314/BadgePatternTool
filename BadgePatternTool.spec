# -*- mode: python ; coding: utf-8 -*-
"""
BadgePatternTool PyInstaller 配置文件
优化版本 - 减小文件大小，提高性能

项目负责人: 喵喵mya (231750570@qq.com)
版本: 动态获取
"""

import sys
import os
from pathlib import Path

# 项目路径 - 使用当前工作目录而不是__file__
project_root = Path(os.getcwd())
src_path = project_root / "src"

# 动态获取版本号
sys.path.insert(0, str(src_path))
try:
    from common.constants import APP_VERSION
    version = APP_VERSION
except ImportError:
    version = "1.5.6"  # 备用版本号

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

        # 网络相关模块 (reportlab需要部分，谨慎排除)
        'requests',
        'urllib3',
        # 'email',       # reportlab需要，不能排除
        'smtplib',
        'poplib',
        'imaplib',
        'ftplib',
        'telnetlib',
        'socketserver',
        'http.server',
        # 'http.client', # 可能被需要，保留
        # 'http.cookies', # 可能被需要，保留
        'xmlrpc',

        # 其他不需要的标准库
        'curses',
        'dbm',
        'ensurepip',
        'idlelib',
        'lib2to3',
        'pydoc_data',
        'turtle',
        'turtledemo',
        'venv',
        'wsgiref',
        'ctypes.test',
        'json.tests',
        'logging.config',
        'logging.handlers',
        'msilib',
        'optparse',
        'plistlib',
        'pty',
        'readline',
        'rlcompleter',
        'sched',
        'shelve',
        'statistics',
        'stringprep',
        'symbol',
        'tabnanny',
        'this',
        'timeit',
        'trace',
        'tty',
        'webbrowser',

        # 数据库和并发
        'sqlite3',
        'asyncio',
        'multiprocessing',
        'concurrent',

        # 构建和打包工具
        'distutils',
        'setuptools',
        'pkg_resources',
        'pip',
        'wheel',

        # Qt6额外模块
        'PySide6.QtSvg',
        'PySide6.QtSvgWidgets',
        'PySide6.QtNetwork',
        'PySide6.QtConcurrent',
        'PySide6.QtSql',
        'PySide6.QtTest',
        'PySide6.QtQuick',
        'PySide6.QtQml',
        'PySide6.QtWebEngine',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtMultimedia',
        'PySide6.QtMultimediaWidgets',
        'PySide6.QtOpenGL',
        'PySide6.QtOpenGLWidgets',
        'PySide6.Qt3DCore',
        'PySide6.Qt3DRender',
        'PySide6.Qt3DInput',
        'PySide6.Qt3DLogic',
        'PySide6.Qt3DAnimation',
        'PySide6.Qt3DExtras',
        'PySide6.QtCharts',
        'PySide6.QtDataVisualization',
        'PySide6.QtDesigner',
        'PySide6.QtHelp',
        'PySide6.QtLocation',
        'PySide6.QtPositioning',
        'PySide6.QtSensors',
        'PySide6.QtSerialPort',
        'PySide6.QtWebChannel',
        'PySide6.QtWebSockets',
        'PySide6.QtXml',
        'PySide6.QtXmlPatterns',
        'PySide6.QtBluetooth',
        'PySide6.QtNfc',
        'PySide6.QtRemoteObjects',
        'PySide6.QtScxml',
        'PySide6.QtStateMachine',
        'PySide6.QtUiTools',
        'PySide6.QtWebView',

        # PIL/Pillow不需要的格式支持
        'PIL.IcnsImagePlugin',
        'PIL.IcoImagePlugin',
        'PIL.ImImagePlugin',
        'PIL.McIdasImagePlugin',
        'PIL.MicImagePlugin',
        'PIL.MpoImagePlugin',
        'PIL.PcdImagePlugin',
        'PIL.PcxImagePlugin',
        'PIL.PdfImagePlugin',
        'PIL.PixarImagePlugin',
        'PIL.PpmImagePlugin',
        'PIL.PsdImagePlugin',
        'PIL.SgiImagePlugin',
        'PIL.SpiderImagePlugin',
        'PIL.SunImagePlugin',
        'PIL.TgaImagePlugin',
        'PIL.WebPImagePlugin',
        'PIL.WmfImagePlugin',
        'PIL.XbmImagePlugin',
        'PIL.XpmImagePlugin',
        'PIL.XVThumbImagePlugin',

        # PIL字体和其他功能
        'PIL.ImageFont',
        'PIL.ImageMath',
        'PIL.ImagePath',
        'PIL.ImageQt',
        'PIL.ImageShow',
        'PIL.ImageTk',
        'PIL.ImageWin',

        # ReportLab高级功能模块 (新增优化)
        # 注意：不能排除rl_config，reportlab核心需要
        'reportlab.graphics',
        'reportlab.platypus.tableofcontents',
        'reportlab.platypus.xpreformatted',
        # 'reportlab.lib.styles',    # 可能被需要，保留
        # 'reportlab.lib.units',     # 可能被需要，保留
        # 'reportlab.lib.enums',     # 可能被需要，保留
        'reportlab.lib.sequencer',
        'reportlab.lib.randomtext',
        'reportlab.lib.testutils',
        'reportlab.lib.validators',
        # 'reportlab.pdfbase.pdfutils',  # 可能被需要，保留
        # 'reportlab.pdfbase.pdfdoc',    # 可能被需要，保留
        # 'reportlab.pdfbase.pdfpattern', # 可能被需要，保留
        # 'reportlab.pdfbase.cidfonts',   # 可能被需要，保留
        # 'reportlab.pdfbase.ttfonts',    # 可能被需要，保留
        # 'reportlab.pdfbase.afm',        # 可能被需要，保留
        # 'reportlab.rl_config',     # reportlab核心需要，不能排除

        # 更多编码和压缩模块 (新增优化)
        # 注意：不能排除zipfile，PyInstaller运行时需要
        'bz2',
        'lzma',
        'gzip',
        'tarfile',
        # 'zipfile',  # PyInstaller需要，不能排除
        # 'base64',   # 可能被其他模块需要，保留
        # 'binascii', # 可能被其他模块需要，保留
        # 'codecs',   # 编码相关，可能被需要，保留
        # 'locale',   # 本地化可能被需要，保留
        # 'gettext',  # PySide6需要，不能排除
        # 'unicodedata', # Unicode数据可能被需要，保留
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
        # Windows系统DLL
        'api-ms-win-',
        'ucrtbase.dll',
        'msvcp140.dll',
        'vcruntime140.dll',

        # Qt6模块DLL
        'Qt6Network',
        'Qt6Sql',
        'Qt6Test',
        'Qt6Quick',
        'Qt6Qml',
        'Qt6WebEngine',
        'Qt6WebEngineCore',
        'Qt6WebEngineWidgets',
        'Qt6Multimedia',
        'Qt6MultimediaWidgets',
        'Qt6OpenGL',
        'Qt6OpenGLWidgets',
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
        'Qt6Svg',
        'Qt6SvgWidgets',
        'Qt6Concurrent',
        'Qt6Bluetooth',
        'Qt6Nfc',
        'Qt6RemoteObjects',
        'Qt6Scxml',
        'Qt6StateMachine',
        'Qt6UiTools',
        'Qt6WebView',

        # OpenGL相关
        'opengl32sw.dll',
        'libEGL.dll',
        'libGLESv2.dll',
        'd3dcompiler_47.dll',

        # 其他不需要的DLL
        'mf.dll',
        'mfplat.dll',
        'mfreadwrite.dll',
        'propsys.dll',
    ]
    
    # 过滤二进制文件
    a.binaries = [x for x in a.binaries if not any(exclude in x[0] for exclude in excludes)]
    
    # 过滤数据文件
    excludes_data = [
        # Qt翻译和文档
        'translations',
        'qml',
        'examples',
        'doc',
        'docs',
        'include',
        'mkspecs',

        # Qt平台插件 (只保留必需的)
        'plugins/platforms/qminimal',
        'plugins/platforms/qoffscreen',
        'plugins/platforms/qlinuxfb',
        'plugins/platforms/qvnc',

        # 图像格式插件 (只保留JPG/PNG/BMP)
        'plugins/imageformats/qico',
        'plugins/imageformats/qicns',
        'plugins/imageformats/qtga',
        'plugins/imageformats/qtiff',
        'plugins/imageformats/qwbmp',
        'plugins/imageformats/qwebp',
        'plugins/imageformats/qsvg',
        'plugins/imageformats/qpdf',

        # 其他不需要的插件
        'plugins/multimedia',
        'plugins/sqldrivers',
        'plugins/bearer',
        'plugins/position',
        'plugins/sensors',
        'plugins/webview',
        'plugins/printsupport/cupsprintersupport',

        # 字体文件 (保留系统默认)
        'fonts',

        # 其他资源
        'resources',
        'lib/python3.11/site-packages/PySide6/examples',
        'lib/python3.11/site-packages/PySide6/docs',
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
    upx=True,    # 启用UPX压缩以减小文件大小
    upx_exclude=[
        # 排除可能有兼容性问题的文件
        'vcruntime140.dll',
        'python311.dll',
        'Qt6Core.dll',
        'Qt6Gui.dll',
        'Qt6Widgets.dll',
    ],
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
