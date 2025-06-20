"""
应用程序常量定义
集中管理所有硬编码的常量值
"""

# 应用程序基本信息
APP_NAME = "BadgePatternTool"
APP_VERSION = "1.5.4"
APP_TITLE = "徽章图案工具"

# 尺寸配置（单位：mm）
DEFAULT_BADGE_SIZE_MM = 58      # 默认徽章直径：58mm
DEFAULT_BLEED_SIZE_MM = 5       # 默认出血半径：5mm
A4_WIDTH_MM = 210               # A4纸宽度
A4_HEIGHT_MM = 297              # A4纸高度

# 布局配置（根据打印机测试结果调整）
DEFAULT_SPACING_MM = 3          # 默认间距：3mm
DEFAULT_MARGIN_MM = 6           # 默认页边距：6mm
MIN_MARGIN_MM = 5               # 最小页边距：5mm
MAX_MARGIN_MM = 30              # 最大页边距：30mm

# 单图编辑区遮罩配置
DEFAULT_OUTSIDE_OPACITY = 80    # 圆形外部区域不透明度（%）
DEFAULT_BLEED_OPACITY = 24      # 出血区不透明度（%）

# DPI配置
PRINT_DPI = 300                 # 打印分辨率
SCREEN_DPI = 96                 # 屏幕显示分辨率

# 界面配置
WINDOW_WIDTH = 1420             # 主窗口宽度
WINDOW_HEIGHT = 800             # 主窗口高度
THUMBNAIL_SIZE = 100            # 缩略图大小

# 列宽配置（固定列宽）
COLUMN_WIDTHS = [260, 340, 480, 300]  # [图片列表, 编辑控制, A4预览, 导出控制]

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
DEFAULT_LAYOUT = "compact"      # 默认布局模式
DEFAULT_EXPORT_FORMAT = "PNG"  # 默认导出格式

# 颜色配置
COLORS = {
    'bg_primary': '#f0f0f0',      # 主背景色
    'bg_secondary': '#ffffff',     # 次背景色
    'bg_canvas': '#404040',        # 画布背景色（深灰）
    'border': '#cccccc',          # 边框色
    'text': '#333333',            # 文字色
    'accent': '#0078d4',          # 强调色
    'success': '#107c10',         # 成功色
    'warning': '#ff8c00',         # 警告色
    'error': '#d13438'            # 错误色
}

# 性能配置
MAX_IMAGE_COUNT = 50            # 最大图片数量
MAX_IMAGE_SIZE_MB = 10          # 单张图片最大大小（MB）
PREVIEW_UPDATE_DELAY = 100      # 预览更新延迟（毫秒）
MAX_CACHE_SIZE = 50             # 最大缓存数量

# 预设徽章尺寸（直径mm + 出血半径mm）
PRESET_BADGE_SIZES = [
    {"name": "小徽章", "diameter": 32, "bleed": 5},
    {"name": "标准徽章", "diameter": 58, "bleed": 5},
    {"name": "大徽章", "diameter": 75, "bleed": 5}
]

# 文件路径配置
ICON_FILENAME = "icon.ico"
ICON_FALLBACK = "icon.png"

# 工具函数
def mm_to_pixels(mm, dpi=PRINT_DPI):
    """将毫米转换为像素"""
    return int(mm * dpi / 25.4)

def pixels_to_mm(pixels, dpi=PRINT_DPI):
    """将像素转换为毫米"""
    return pixels * 25.4 / dpi

# 计算的常量
A4_WIDTH_PX = mm_to_pixels(A4_WIDTH_MM)
A4_HEIGHT_PX = mm_to_pixels(A4_HEIGHT_MM)
