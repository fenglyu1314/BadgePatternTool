"""
文件处理工具模块
处理图片文件的导入、验证和管理
"""

import os
import sys
import uuid
from PIL import Image
from PySide6.QtGui import QPixmap
from io import BytesIO

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import SUPPORTED_IMAGE_FORMATS, MAX_IMAGE_COUNT
from common.error_handler import logger, show_error_message, error_handler, resource_manager, ImageProcessingError

# 本地常量
MAX_IMAGE_SIZE_MB = 50  # 最大图片文件大小（MB）
THUMBNAIL_SIZE = 100    # 缩略图尺寸

class FileHandler:
    """文件处理类"""
    
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
        
    @error_handler("选择图片文件失败", show_error=False, default_return=[])
    def select_images(self, parent=None):
        """
        选择图片文件
        返回: 选中的文件路径列表
        """
        from PySide6.QtWidgets import QFileDialog, QMessageBox

        # 构建文件过滤器
        filter_str = "图片文件 ("
        for fmt in SUPPORTED_IMAGE_FORMATS:
            filter_str += f"*{fmt[1]} "
        filter_str = filter_str.strip() + ")"

        file_paths, _ = QFileDialog.getOpenFileNames(
            parent,
            "选择图片文件",
            os.path.expanduser("~"),
            filter_str
        )

        if not file_paths:
            return []

        # 验证文件
        valid_files = []
        invalid_files = []

        for file_path in file_paths:
            try:
                if self.validate_image_file(file_path):
                    valid_files.append(file_path)
                    logger.debug(f"验证通过: {os.path.basename(file_path)}")
                else:
                    invalid_files.append(os.path.basename(file_path))
                    logger.warning(f"文件验证失败: {os.path.basename(file_path)}")
            except Exception as e:
                invalid_files.append(os.path.basename(file_path))
                logger.error(f"验证文件时出错 {os.path.basename(file_path)}: {e}")

        # 显示无效文件警告
        if invalid_files and parent:
            QMessageBox.warning(
                parent,
                "文件格式警告",
                f"以下文件格式不支持或文件损坏：\n" + "\n".join(invalid_files)
            )

        logger.info(f"选择了 {len(valid_files)} 个有效图片文件")
        return valid_files
    
    def validate_image_file(self, file_path):
        """
        验证图片文件是否有效
        参数: file_path - 文件路径
        返回: bool - 是否有效
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.debug(f"文件不存在: {file_path}")
                return False

            # 检查文件扩展名
            _, ext = os.path.splitext(file_path.lower())
            if ext not in self.supported_formats:
                logger.debug(f"不支持的文件格式: {ext}")
                return False

            # 检查文件大小
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > MAX_IMAGE_SIZE_MB:
                logger.warning(f"文件过大 ({file_size_mb:.1f}MB): {os.path.basename(file_path)}")
                return False

            # 尝试打开图片验证格式
            with resource_manager(Image.open(file_path)) as img:
                img.verify()  # 验证图片完整性

            return True

        except Exception as e:
            logger.debug(f"图片验证失败 {os.path.basename(file_path)}: {e}")
            return False
    
    @error_handler("获取图片信息失败", show_error=False)
    def get_image_info(self, file_path):
        """
        获取图片信息
        参数: file_path - 文件路径
        返回: dict - 图片信息
        """
        if not os.path.exists(file_path):
            raise ImageProcessingError(f"图片文件不存在: {file_path}")

        with resource_manager(Image.open(file_path)) as img:
            info = {
                'path': file_path,
                'filename': os.path.basename(file_path),
                'size': img.size,
                'format': img.format,
                'mode': img.mode,
                'file_size': os.path.getsize(file_path)
            }
            logger.debug(f"获取图片信息: {info['filename']} ({info['size'][0]}x{info['size'][1]})")
            return info
    
    def create_thumbnail(self, file_path, size=(THUMBNAIL_SIZE, THUMBNAIL_SIZE)):
        """
        创建缩略图
        参数: file_path - 文件路径, size - 缩略图尺寸
        返回: QPixmap - 缩略图对象
        """
        try:
            with Image.open(file_path) as img:
                # 转换为RGB模式（确保兼容性）
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # 创建缩略图（保持比例）
                img.thumbnail(size, Image.Resampling.LANCZOS)

                # 创建正方形背景
                thumbnail = Image.new('RGB', size, (240, 240, 240))

                # 计算居中位置
                x = (size[0] - img.width) // 2
                y = (size[1] - img.height) // 2

                # 粘贴图片到背景
                thumbnail.paste(img, (x, y))

                # 转换为QPixmap
                buffer = BytesIO()
                try:
                    thumbnail.save(buffer, format='PNG')
                    buffer.seek(0)

                    pixmap = QPixmap()
                    pixmap.loadFromData(buffer.getvalue())
                    return pixmap
                finally:
                    # 确保释放内存
                    buffer.close()
                    del thumbnail

        except Exception as e:
            logger.error(f"创建缩略图失败 {os.path.basename(file_path)}: {e}", exc_info=True)
            # 创建错误占位图
            error_pixmap = QPixmap(size[0], size[1])
            error_pixmap.fill()  # 填充为白色
            return error_pixmap

class ImageItem:
    """图片项目类，用于管理单个图片的信息和状态"""

    # 类变量：用于跟踪同一文件的实例数量
    _file_instance_counters = {}

    def __init__(self, file_path):
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        self.thumbnail = None
        self.info = None
        self.is_processed = False

        # 生成唯一标识
        self.unique_id = str(uuid.uuid4())

        # 为同一文件分配实例序号
        if file_path not in ImageItem._file_instance_counters:
            ImageItem._file_instance_counters[file_path] = 0
        ImageItem._file_instance_counters[file_path] += 1
        self.instance_number = ImageItem._file_instance_counters[file_path]

        # 编辑参数
        self.scale = 1.0      # 缩放比例
        self.offset_x = 0     # X轴偏移
        self.offset_y = 0     # Y轴偏移
        self.rotation = 0     # 旋转角度

        # 排版参数
        self.quantity = 1     # 在画布上出现的数量

        # 加载图片信息
        self.load_info()
    
    def load_info(self):
        """加载图片信息"""
        try:
            file_handler = FileHandler()
            self.info = file_handler.get_image_info(self.file_path)
        except Exception as e:
            logger.error(f"加载图片信息失败 {self.filename}: {e}")
            self.info = {
                'path': self.file_path,
                'filename': self.filename,
                'error': str(e)
            }
    
    def create_thumbnail(self, size=(THUMBNAIL_SIZE, THUMBNAIL_SIZE)):
        """创建缩略图"""
        if not self.thumbnail:
            file_handler = FileHandler()
            self.thumbnail = file_handler.create_thumbnail(self.file_path, size)
        return self.thumbnail
    
    def get_display_name(self):
        """获取显示名称"""
        # 如果同一文件有多个实例，显示序号
        if ImageItem._file_instance_counters.get(self.file_path, 1) > 1:
            name, ext = os.path.splitext(self.filename)
            return f"{name}#{self.instance_number}{ext}"
        return self.filename
    
    def get_size_text(self):
        """获取尺寸文本"""
        if self.info and 'size' in self.info:
            w, h = self.info['size']
            return f"{w}×{h}"
        return "未知"
    
    def get_file_size_text(self):
        """获取文件大小文本"""
        if self.info and 'file_size' in self.info:
            size_mb = self.info['file_size'] / (1024 * 1024)
            if size_mb < 1:
                size_kb = self.info['file_size'] / 1024
                return f"{size_kb:.1f}KB"
            else:
                return f"{size_mb:.1f}MB"
        return "未知"
    
    def reset_edit_params(self):
        """重置编辑参数"""
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.rotation = 0
        self.is_processed = False

    def copy(self):
        """创建当前图片项的副本"""
        # 创建新的ImageItem实例
        new_item = ImageItem(self.file_path)

        # 复制编辑参数
        new_item.scale = self.scale
        new_item.offset_x = self.offset_x
        new_item.offset_y = self.offset_y
        new_item.rotation = self.rotation
        new_item.quantity = self.quantity
        new_item.is_processed = self.is_processed

        return new_item
