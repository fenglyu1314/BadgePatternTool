"""
配置管理模块
管理应用程序的配置参数和常量
"""

# 应用程序基本信息
APP_NAME = "BadgePatternTool"
APP_VERSION = "1.0.0"
APP_TITLE = "徽章图案工具"

# 尺寸配置（单位：mm）
BADGE_DIAMETER_MM = 68  # 徽章直径
A4_WIDTH_MM = 210      # A4纸宽度
A4_HEIGHT_MM = 297     # A4纸高度

# DPI配置
PRINT_DPI = 300        # 打印分辨率
SCREEN_DPI = 96        # 屏幕显示分辨率

# 像素尺寸计算（基于300DPI）
def mm_to_pixels(mm, dpi=PRINT_DPI):
    """将毫米转换为像素"""
    return int(mm * dpi / 25.4)

# 计算关键尺寸
BADGE_DIAMETER_PX = mm_to_pixels(BADGE_DIAMETER_MM)  # 徽章直径像素
A4_WIDTH_PX = mm_to_pixels(A4_WIDTH_MM)             # A4宽度像素
A4_HEIGHT_PX = mm_to_pixels(A4_HEIGHT_MM)           # A4高度像素

# 界面配置
WINDOW_WIDTH = 1200    # 主窗口宽度
WINDOW_HEIGHT = 800    # 主窗口高度
THUMBNAIL_SIZE = 100   # 缩略图大小

# 文件格式配置
SUPPORTED_IMAGE_FORMATS = [
    ("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
    ("JPEG文件", "*.jpg *.jpeg"),
    ("PNG文件", "*.png"),
    ("所有文件", "*.*")
]

EXPORT_FORMATS = [
    ("PDF文件", "*.pdf"),
    ("PNG文件", "*.png"),
    ("JPEG文件", "*.jpg")
]

# 默认设置
DEFAULT_SPACING = 5     # 默认间距（mm）
DEFAULT_MARGIN = 10     # 默认页边距（mm）
DEFAULT_LAYOUT = "grid" # 默认布局模式：grid（网格）或 compact（紧密）

# 颜色配置
COLORS = {
    'bg_primary': '#f0f0f0',      # 主背景色
    'bg_secondary': '#ffffff',     # 次背景色
    'border': '#cccccc',          # 边框色
    'text': '#333333',            # 文字色
    'accent': '#0078d4',          # 强调色
    'success': '#107c10',         # 成功色
    'warning': '#ff8c00',         # 警告色
    'error': '#d13438'            # 错误色
}

# 性能配置
MAX_IMAGE_COUNT = 50      # 最大图片数量
MAX_IMAGE_SIZE_MB = 10    # 单张图片最大大小（MB）
PREVIEW_UPDATE_DELAY = 100 # 预览更新延迟（毫秒）
