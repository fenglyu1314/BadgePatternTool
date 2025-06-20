"""
配置管理模块
管理应用程序的动态配置参数
"""

# 导入常量
from common.constants import *
from common.error_handler import logger

# 动态配置管理类
class AppConfig:
    """应用程序配置管理"""

    def __init__(self):
        # 徽章尺寸配置
        self._badge_size_mm = DEFAULT_BADGE_SIZE_MM
        self._bleed_size_mm = DEFAULT_BLEED_SIZE_MM

        # 遮罩透明度配置
        self._outside_opacity = DEFAULT_OUTSIDE_OPACITY
        self._bleed_opacity = DEFAULT_BLEED_OPACITY

        self._listeners = []  # 配置变化监听器

    @property
    def badge_size_mm(self):
        """徽章直径（毫米）"""
        return self._badge_size_mm

    @badge_size_mm.setter
    def badge_size_mm(self, value):
        """设置徽章直径"""
        value = max(10, min(100, value))  # 支持到100mm
        if value != self._badge_size_mm:
            old_value = self._badge_size_mm
            self._badge_size_mm = value
            self._notify_listeners('badge_size_mm', old_value, value)

    @property
    def bleed_size_mm(self):
        """出血半径（毫米）"""
        return self._bleed_size_mm

    @bleed_size_mm.setter
    def bleed_size_mm(self, value):
        """设置出血半径"""
        value = max(0, min(10, value))  # 出血半径最大10mm
        if value != self._bleed_size_mm:
            old_value = self._bleed_size_mm
            self._bleed_size_mm = value
            self._notify_listeners('bleed_size_mm', old_value, value)

    @property
    def badge_diameter_mm(self):
        """总直径（徽章直径 + 出血半径×2）"""
        return self._badge_size_mm + self._bleed_size_mm * 2

    @badge_diameter_mm.setter
    def badge_diameter_mm(self, value):
        """设置总直径（保持出血半径不变，调整徽章直径）"""
        new_badge_size = value - self._bleed_size_mm * 2
        self.badge_size_mm = new_badge_size

    @property
    def outside_opacity(self):
        """圆形外部区域不透明度（%）"""
        return self._outside_opacity

    @outside_opacity.setter
    def outside_opacity(self, value):
        """设置圆形外部区域不透明度"""
        value = max(0, min(100, value))
        if value != self._outside_opacity:
            old_value = self._outside_opacity
            self._outside_opacity = value
            self._notify_listeners('outside_opacity', old_value, value)

    @property
    def bleed_opacity(self):
        """出血区不透明度（%）"""
        return self._bleed_opacity

    @bleed_opacity.setter
    def bleed_opacity(self, value):
        """设置出血区不透明度"""
        value = max(0, min(100, value))
        if value != self._bleed_opacity:
            old_value = self._bleed_opacity
            self._bleed_opacity = value
            self._notify_listeners('bleed_opacity', old_value, value)

    @property
    def badge_diameter_px(self):
        """总直径（像素）"""
        return mm_to_pixels(self.badge_diameter_mm)

    @property
    def badge_radius_px(self):
        """总半径（像素）"""
        return self.badge_diameter_px // 2

    @property
    def badge_size_px(self):
        """徽章尺寸（像素）"""
        return mm_to_pixels(self._badge_size_mm)

    @property
    def bleed_size_px(self):
        """出血区尺寸（像素）"""
        return mm_to_pixels(self._bleed_size_mm)

    def add_listener(self, callback):
        """添加配置变化监听器"""
        self._listeners.append(callback)

    def remove_listener(self, callback):
        """移除配置变化监听器"""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify_listeners(self, key, old_value, new_value):
        """通知监听器配置已变化"""
        for callback in self._listeners:
            try:
                callback(key, old_value, new_value)
            except Exception as e:
                logger.error(f"配置监听器错误: {e}", exc_info=True)

# 全局配置实例
app_config = AppConfig()

# 向后兼容的常量（动态获取）
def get_badge_diameter_mm():
    """获取当前徽章直径（毫米）"""
    return app_config.badge_diameter_mm

def get_badge_diameter_px():
    """获取当前徽章直径（像素）"""
    return app_config.badge_diameter_px

# 为了向后兼容，保留常量形式（但这些值是动态的）
BADGE_DIAMETER_MM = app_config.badge_diameter_mm
BADGE_DIAMETER_PX = app_config.badge_diameter_px
