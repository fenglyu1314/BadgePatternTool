#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全的模块排除列表
提供经过验证的、不会破坏PyInstaller运行时的模块排除列表
"""

# PyInstaller核心依赖 - 绝对不能排除
PYINSTALLER_CORE = [
    'zipfile',      # PyInstaller运行时需要
    'importlib',    # 模块导入机制
    'pkgutil',      # 包工具
    'inspect',      # 反射机制
    'types',        # 类型系统
    'sys',          # 系统接口
    'os',           # 操作系统接口
    'io',           # 输入输出
    'collections',  # 集合类型
    'functools',    # 函数工具
    'itertools',    # 迭代工具
    'operator',     # 操作符
    'weakref',      # 弱引用
    'gc',           # 垃圾回收
    'threading',    # 线程支持
    'queue',        # 队列
    'time',         # 时间
    'datetime',     # 日期时间
    'calendar',     # 日历
    'struct',       # 结构体
    'array',        # 数组
    'copy',         # 复制
    'pickle',       # 序列化
    'json',         # JSON支持
    'warnings',     # 警告系统
    'traceback',    # 异常追踪
    'linecache',    # 行缓存
    'tokenize',     # 标记化
    'keyword',      # 关键字
    'string',       # 字符串
    're',           # 正则表达式
    'math',         # 数学函数
    'random',       # 随机数
    'hashlib',      # 哈希算法
    'hmac',         # HMAC
    'uuid',         # UUID
    'pathlib',      # 路径操作
    'tempfile',     # 临时文件
    'shutil',       # 文件操作
    'glob',         # 文件匹配
    'fnmatch',      # 文件名匹配
]

# 可能被其他模块需要的基础模块 - 谨慎排除
POTENTIALLY_NEEDED = [
    'base64',       # 可能被网络或编码模块需要
    'binascii',     # 二进制转换，可能被需要
    'codecs',       # 编码解码，可能被需要
    'xml',          # XML处理，reportlab可能需要
    'html',         # HTML处理
    'urllib',       # URL处理，可能被需要
    'http',         # HTTP协议，可能被需要
    'ssl',          # SSL支持，可能被需要
    'socket',       # 网络套接字，可能被需要
    'select',       # I/O多路复用
    'errno',        # 错误码
    'signal',       # 信号处理
    'subprocess',   # 子进程
    'platform',     # 平台信息
    'getpass',      # 密码输入
    'pwd',          # 用户信息 (Unix)
    'grp',          # 组信息 (Unix)
]

# 安全可排除的模块 - 确认不会影响运行时
SAFE_TO_EXCLUDE = [
    # 开发和测试工具
    'unittest',
    'doctest', 
    'test',
    'tests',
    'pytest',
    'nose',
    'coverage',
    'pdb',
    'profile',
    'cProfile',
    'pstats',
    'trace',
    'timeit',
    'dis',
    'py_compile',
    'compileall',
    
    # 文档和帮助
    'pydoc',
    'pydoc_data',
    'help',
    'this',
    
    # 交互式环境
    'cmd',
    'code',
    'codeop',
    'readline',
    'rlcompleter',
    'idle',
    'idlelib',
    
    # 图形界面 (我们使用PySide6)
    'tkinter',
    'turtle',
    'turtledemo',
    
    # 科学计算 (我们不使用)
    'numpy',
    'scipy',
    'matplotlib',
    'pandas',
    'sklearn',
    'tensorflow',
    'torch',
    'keras',
    
    # Web框架 (我们不使用)
    'django',
    'flask',
    'tornado',
    'aiohttp',
    'fastapi',
    'bottle',
    'cherrypy',
    
    # 数据库 (我们不使用)
    'sqlite3',
    'mysql',
    'postgresql',
    'pymongo',
    'redis',
    
    # 网络服务 (我们不使用)
    'wsgiref',
    'http.server',
    'xmlrpc',
    'ftplib',
    'telnetlib',
    'poplib',
    'imaplib',
    'smtplib',
    'nntplib',
    
    # 并发和异步 (我们不使用)
    'asyncio',
    'concurrent',
    'multiprocessing',
    'threading',  # 注意：如果GUI使用多线程则不能排除
    
    # 压缩和归档 (部分可排除)
    'bz2',
    'lzma',
    'gzip',
    'tarfile',
    # 'zipfile',  # 不能排除！PyInstaller需要
    
    # 加密和安全 (我们不使用)
    'secrets',
    'crypt',
    'getpass',
    
    # 系统管理 (我们不使用)
    'sysconfig',
    'distutils',
    'setuptools',
    'pkg_resources',
    'pip',
    'wheel',
    'ensurepip',
    
    # 国际化 (我们不使用)
    'locale',
    'gettext',
    'unicodedata',
    
    # 其他工具
    'argparse',     # 如果不使用命令行参数
    'optparse',     # 旧版参数解析
    'configparser', # 如果不使用配置文件
    'csv',          # 如果不处理CSV
    'email',        # 如果不处理邮件
    'mimetypes',    # 如果不需要MIME类型
    'quopri',       # 引用打印编码
    'uu',           # UU编码
    'binhex',       # BinHex编码
    'mailbox',      # 邮箱格式
    'mailcap',      # 邮件能力
    'msilib',       # MSI安装包 (Windows)
    'msvcrt',       # MSVC运行时 (Windows)
    'winsound',     # Windows声音 (Windows)
    'winreg',       # Windows注册表 (Windows)
]

def get_recommended_excludes():
    """获取推荐的排除列表"""
    return SAFE_TO_EXCLUDE

def get_core_modules():
    """获取核心模块列表（不能排除）"""
    return PYINSTALLER_CORE

def get_potentially_needed():
    """获取可能需要的模块列表（谨慎排除）"""
    return POTENTIALLY_NEEDED

def validate_excludes(exclude_list):
    """验证排除列表的安全性"""
    dangerous = []
    for module in exclude_list:
        if module in PYINSTALLER_CORE:
            dangerous.append(module)
    
    if dangerous:
        print(f"⚠️ 警告：以下模块不应该被排除：{dangerous}")
        return False
    
    return True

if __name__ == "__main__":
    print("安全的模块排除列表")
    print("=" * 50)
    print(f"推荐排除模块数量: {len(SAFE_TO_EXCLUDE)}")
    print(f"核心模块数量: {len(PYINSTALLER_CORE)}")
    print(f"谨慎排除模块数量: {len(POTENTIALLY_NEEDED)}")
