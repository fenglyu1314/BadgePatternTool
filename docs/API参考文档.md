# BadgePatternTool API 参考文档

## 📋 概述

本文档详细描述了 BadgePatternTool 项目中各个模块的公共API接口，为开发者提供准确的接口规范和使用示例。

## 🎨 图片处理模块 (image_processor.py)

### ImageProcessor 类

#### `load_image(file_path: str) -> Optional[Image.Image]`
加载图片文件并进行基础验证。

**参数：**
- `file_path`: 图片文件路径

**返回值：**
- `PIL.Image.Image`: 成功加载的图片对象
- `None`: 加载失败

**示例：**
```python
processor = ImageProcessor()
image = processor.load_image("path/to/image.jpg")
if image:
    print(f"图片尺寸: {image.size}")
```

#### `create_circular_crop(params: ImageProcessParams) -> Optional[Image.Image]`
创建圆形裁剪的图片。

**参数：**
- `params`: 图片处理参数对象

**返回值：**
- `PIL.Image.Image`: 圆形裁剪后的图片（RGBA格式）
- `None`: 处理失败

**示例：**
```python
params = ImageProcessParams(
    image_path="image.jpg",
    scale=1.5,
    offset_x=10,
    offset_y=-5,
    rotation=0
)
result = processor.create_circular_crop(params)
```

#### `get_optimal_scale(image_path: str) -> float`
计算图片的最佳缩放比例。

**参数：**
- `image_path`: 图片文件路径

**返回值：**
- `float`: 最佳缩放比例（确保图片能覆盖整个圆形区域）

#### `clear_cache() -> None`
清理图片处理缓存。

### CircleEditor 类

#### `__init__(image_path: str)`
初始化圆形编辑器。

**参数：**
- `image_path`: 图片文件路径

#### `reset_to_optimal() -> None`
重置编辑参数到最佳状态。

**属性：**
- `scale: float`: 缩放比例
- `offset_x: int`: X轴偏移（像素）
- `offset_y: int`: Y轴偏移（像素）
- `rotation: float`: 旋转角度（度）

### ImageProcessParams 类

图片处理参数数据类。

**属性：**
```python
@dataclass
class ImageProcessParams:
    image_path: str
    scale: float = 1.0
    offset_x: int = 0
    offset_y: int = 0
    rotation: float = 0.0
```

## 📐 排版引擎模块 (layout_engine.py)

### LayoutEngine 类

#### `calculate_grid_layout(spacing_mm: float, margin_mm: float) -> Dict`
计算网格布局。

**参数：**
- `spacing_mm`: 圆形间距（毫米）
- `margin_mm`: 页面边距（毫米）

**返回值：**
```python
{
    'positions': List[Tuple[int, int]],  # 位置坐标列表
    'max_count': int,                    # 最大容量
    'rows': int,                         # 行数
    'cols': int                          # 列数
}
```

#### `calculate_compact_layout(spacing_mm: float, margin_mm: float) -> Dict`
计算紧凑布局（六边形排列）。

**参数：**
- `spacing_mm`: 圆形间距（毫米）
- `margin_mm`: 页面边距（毫米）

**返回值：**
```python
{
    'positions': List[Tuple[int, int]],  # 位置坐标列表
    'max_count': int,                    # 最大容量
    'layout_type': str                   # 布局类型
}
```

#### `calculate_multi_page_layout(image_count: int, layout_type: str, spacing_mm: float, margin_mm: float) -> Dict`
计算多页面布局。

**参数：**
- `image_count`: 图片总数
- `layout_type`: 布局类型（'grid' 或 'compact'）
- `spacing_mm`: 圆形间距（毫米）
- `margin_mm`: 页面边距（毫米）

**返回值：**
```python
{
    'total_pages': int,                  # 总页数
    'max_per_page': int,                 # 每页最大容量
    'pages': List[Dict]                  # 每页详细信息
}
```

#### `create_layout_preview(image_items: List, layout_type: str, spacing_mm: float, margin_mm: float, preview_scale: float = 0.5) -> QPixmap`
创建排版预览图。

**参数：**
- `image_items`: 图片项列表
- `layout_type`: 布局类型
- `spacing_mm`: 圆形间距
- `margin_mm`: 页面边距
- `preview_scale`: 预览缩放比例

**返回值：**
- `QPixmap`: 预览图片

#### `create_multi_page_preview(image_items: List, layout_type: str, spacing_mm: float, margin_mm: float, preview_scale: float = 0.5) -> List[QPixmap]`
创建多页面预览图。

**返回值：**
- `List[QPixmap]`: 多页面预览图片列表

### 坐标转换工具函数

#### `mm_to_px(mm_value: float) -> int`
毫米转像素（300 DPI）。

#### `px_to_mm(px_value: int) -> float`
像素转毫米。

## 📤 导出管理模块 (export_manager.py)

### ExportManager 类

#### `export_layout(image_items: List, layout_type: str, spacing_mm: float, margin_mm: float, output_path: str, format_type: str = 'PNG', dpi: int = 300) -> bool`
导出排版布局。

**参数：**
- `image_items`: 图片项列表
- `layout_type`: 布局类型
- `spacing_mm`: 圆形间距
- `margin_mm`: 页面边距
- `output_path`: 输出文件路径
- `format_type`: 文件格式（'PNG', 'JPG', 'PDF'）
- `dpi`: 分辨率

**返回值：**
- `bool`: 导出是否成功

#### `export_to_pdf(image_items: List, layout_type: str, spacing_mm: float, margin_mm: float, output_path: str) -> bool`
导出为PDF格式（支持多页面）。

#### `get_supported_formats() -> List[str]`
获取支持的导出格式列表。

**返回值：**
- `List[str]`: 支持的格式列表 ['PNG', 'JPG', 'PDF']

## 🗂️ 文件处理模块 (file_handler.py)

### FileHandler 类

#### `validate_image_file(file_path: str) -> bool`
验证图片文件。

**参数：**
- `file_path`: 文件路径

**返回值：**
- `bool`: 文件是否有效

**异常：**
- `ValueError`: 文件无效时抛出异常

#### `load_images(file_paths: List[str]) -> List[ImageItem]`
批量加载图片。

**参数：**
- `file_paths`: 文件路径列表

**返回值：**
- `List[ImageItem]`: 图片项列表

#### `get_supported_formats() -> Set[str]`
获取支持的图片格式。

**返回值：**
- `Set[str]`: 支持的格式集合

### ImageItem 类

图片项数据模型。

#### `__init__(file_path: str)`
初始化图片项。

#### `get_display_name() -> str`
获取显示名称。

#### `get_processing_params() -> ImageProcessParams`
获取处理参数对象。

**属性：**
```python
file_path: str          # 文件路径
filename: str           # 文件名
scale: float           # 缩放比例
offset_x: int          # X轴偏移
offset_y: int          # Y轴偏移
rotation: float        # 旋转角度
quantity: int          # 数量
is_processed: bool     # 是否已处理
thumbnail: QPixmap     # 缩略图
```

## ⚙️ 配置管理模块 (config.py)

### AppConfig 类

#### `add_listener(callback: Callable) -> None`
添加配置变化监听器。

**参数：**
- `callback`: 回调函数 `(key: str, old_value: Any, new_value: Any) -> None`

#### `remove_listener(callback: Callable) -> None`
移除配置变化监听器。

#### `get_value(key: str, default: Any = None) -> Any`
获取配置值。

#### `set_value(key: str, value: Any) -> None`
设置配置值。

**主要配置属性：**
```python
badge_size_mm: float        # 徽章直径
bleed_size_mm: float        # 出血半径
badge_diameter_mm: float    # 总直径（只读）
badge_radius_px: int        # 徽章半径像素（只读）
badge_diameter_px: int      # 徽章直径像素（只读）
outside_opacity: int        # 圆外透明度
bleed_opacity: int          # 出血区透明度
```

## 🖼️ 交互式编辑器 (interactive_image_editor.py)

### InteractiveImageEditor 类

继承自 `QWidget`，提供交互式图片编辑功能。

#### `load_image(file_path: str) -> bool`
加载图片到编辑器。

#### `set_parameters(scale: float, offset_x: int, offset_y: int, rotation: float = 0) -> None`
设置编辑参数。

#### `reset_view() -> None`
重置视图到默认状态。

#### `update_mask_radius() -> None`
更新遮罩半径（当徽章尺寸改变时调用）。

**信号：**
```python
parameters_changed = Signal(float, int, int)  # (scale, offset_x, offset_y)
```

**属性：**
```python
image_scale: float      # 当前缩放比例
offset_x: int          # X轴偏移
offset_y: int          # Y轴偏移
mask_radius: int       # 遮罩半径
```

## 📄 多页面预览组件 (multi_page_preview_widget.py)

### MultiPagePreviewWidget 类

继承自 `QWidget`，提供多页面预览功能。

#### `set_pages(pages: List[QPixmap]) -> None`
设置预览页面。

#### `set_scale(scale: float) -> None`
设置缩放比例。

#### `fit_to_window(force: bool = False) -> None`
适应窗口大小。

#### `get_current_scale() -> float`
获取当前缩放比例。

**信号：**
```python
scale_changed = Signal(float)  # 缩放变化信号
```

## 🔧 工具函数

### 常量定义 (common/constants.py)

```python
# 窗口尺寸
WINDOW_WIDTH = 1420
WINDOW_HEIGHT = 800

# 列宽配置
COLUMN_WIDTHS = [260, 340, 480, 300]

# 默认值
DEFAULT_SPACING_MM = 3
DEFAULT_MARGIN_MM = 6
DEFAULT_LAYOUT = 'compact'
DEFAULT_EXPORT_FORMAT = 'PNG'

# 限制值
MAX_IMAGE_COUNT = 100
```

### 错误处理 (common/error_handler.py)

```python
def show_error_message(title: str, message: str, parent=None) -> None
def show_warning_message(title: str, message: str, parent=None) -> None
def show_info_message(title: str, message: str, parent=None) -> None

@handle_exceptions
def decorated_function():
    """自动异常处理装饰器"""
```

### 路径工具 (common/path_utils.py)

```python
def get_asset_path(filename: str) -> Path
def get_icon_path(filename: str) -> Path
def ensure_directory(path: Path) -> None
```

## 📝 使用示例

### 完整工作流程示例

```python
from core.image_processor import ImageProcessor
from core.layout_engine import LayoutEngine
from core.export_manager import ExportManager
from utils.file_handler import FileHandler, ImageItem

# 1. 加载图片
file_handler = FileHandler()
image_items = file_handler.load_images(['img1.jpg', 'img2.jpg'])

# 2. 编辑图片参数
for item in image_items:
    item.scale = 1.5
    item.offset_x = 10
    item.quantity = 2

# 3. 生成布局
layout_engine = LayoutEngine()
layout = layout_engine.calculate_compact_layout(3, 6)

# 4. 导出结果
export_manager = ExportManager()
success = export_manager.export_layout(
    image_items, 'compact', 3, 6, 'output.png', 'PNG', 300
)
```

这份API参考文档提供了所有公共接口的详细说明，帮助开发者正确使用各个模块的功能。
