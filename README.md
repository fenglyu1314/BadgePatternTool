# BadgePatternTool - 徽章图案工具

一个专业的徽章制作图片处理和排版工具，支持将用户图片裁剪成可配置直径的圆形并在A4纸上智能排版。

## 🎯 功能特性

- **图片批量导入**: 支持JPG、PNG、BMP、GIF等常用格式，带缩略图预览
- **可配置徽章尺寸**: 支持32mm、58mm、75mm等预设尺寸，可自定义徽章直径和出血半径
- **圆形裁剪**: 精确裁剪成指定直径圆形，支持安全区域和出血区域显示
- **交互式编辑**: 支持缩放、移动、旋转调整，实时预览效果
- **数量控制**: 为每张图片设置在画布上的出现次数
- **智能排版**: A4纸自动排版，支持网格和紧凑六边形排列
- **多页面支持**: 自动分页处理，支持大批量图片排版
- **交互预览**: 鼠标滚轮缩放、拖动平移，支持适应窗口和重置视图
- **高质量输出**: 300DPI打印质量，支持PDF、PNG、JPG格式
- **直接打印**: 内置打印功能，支持彩色/黑白打印选择
- **性能优化**: 多级缓存、防抖机制确保流畅的操作体验

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Windows 7/8/10/11 (主要支持)
- macOS 10.14+ / Linux (基本支持)

### 安装依赖

**普通用户（仅运行程序）：**
```bash
pip install -r requirements.txt
```

**开发者（完整开发环境）：**
```bash
pip install -r requirements-dev.txt
```

### 运行程序
```bash
python src/main.py
```

### 开发工具
```bash
# 查看当前版本
python scripts/version_manager.py --show

# 运行应用程序
python scripts/dev_tools.py run

# 运行测试
python scripts/dev_tools.py test

# 检查代码质量
python scripts/dev_tools.py quality

# 构建可执行文件
python scripts/dev_tools.py build
```

## 📖 使用指南

### 基本工作流程

1. **导入图片**
   - 点击"导入图片"按钮或使用菜单"文件 → 导入图片"
   - 选择一张或多张图片文件
   - 支持格式：JPG、PNG、BMP、GIF等

2. **配置徽章尺寸**
   - 选择预设尺寸（32mm、58mm、75mm）或自定义
   - 设置出血半径（默认5mm）
   - 调整页边距和间距参数

3. **编辑图片**
   - 在左侧列表中选择图片（支持缩略图预览）
   - 双击图片进入交互式编辑模式
   - 使用鼠标拖拽移动图片位置
   - 使用滚轮缩放图片大小
   - 设置该图片在画布上的数量
   - 调整遮罩透明度查看效果

4. **预览排版**
   - 查看"排版预览"窗口的实时效果
   - 选择排列模式（网格/紧凑）
   - 使用鼠标滚轮缩放预览
   - 支持多页面自动分页显示

5. **导出和打印**
   - 点击"自动排版"为所有图片应用最佳参数
   - 选择导出格式（PDF/PNG/JPG）
   - 点击"导出文件"保存结果
   - 或直接使用"打印"功能打印

### 界面说明

- **左侧面板**: 图片列表管理（带缩略图），导入、删除、清空操作
- **中间左区域**: 图片编辑控制
  - 徽章尺寸设置（预设按钮和自定义输入）
  - 遮罩透明度调节
  - 单图编辑参数显示
- **中间右区域**: 交互式图片编辑器
  - 实时圆形预览和遮罩效果
  - 鼠标拖拽和滚轮缩放操作
- **右侧面板**: 排版预览窗口
  - 实时A4排版效果展示
  - 支持多页面显示和缩放拖拽
- **最右侧**: 导出和打印控制面板

## 📁 项目结构

```
BadgePatternTool/
├── src/
│   ├── main.py              # 主程序入口
│   ├── ui/                  # 界面模块
│   │   ├── main_window.py   # 主窗口
│   │   ├── interactive_preview_label.py # 交互预览组件
│   │   ├── interactive_image_editor.py  # 图片编辑器
│   │   └── custom_print_dialog.py       # 自定义打印对话框
│   ├── core/                # 核心业务逻辑
│   │   ├── image_processor.py # 图片处理
│   │   ├── layout_engine.py   # 排版引擎
│   │   └── export_manager.py  # 导出管理
│   ├── utils/               # 工具函数
│   │   ├── config.py        # 配置管理
│   │   └── file_handler.py  # 文件处理
│   ├── common/              # 公共模块
│   │   ├── imports.py       # 统一导入管理
│   │   ├── constants.py     # 常量定义
│   │   ├── path_utils.py    # 路径工具
│   │   └── error_handler.py # 错误处理
│   └── assets/              # 资源文件
├── docs/                    # 项目文档
│   ├── 代码架构文档.md      # 详细技术架构和算法说明
│   ├── 快速入门指南.md      # 新团队成员入门指南
│   ├── API参考文档.md       # 完整API接口规范
│   ├── 需求文档.md          # 详细需求文档
│   └── README.md           # 文档目录说明
├── tests/                   # 测试模块
│   ├── __init__.py         # 测试包初始化
│   ├── test_core.py        # 核心功能测试
│   ├── test_utils.py       # 工具模块测试
│   ├── test_integration.py # 集成测试
│   └── run_tests.py        # 测试运行器
├── scripts/                 # 开发脚本
│   ├── dev_tools.py        # 开发工具集合
│   ├── build.py            # 构建脚本
│   ├── version_manager.py  # 版本管理工具
│   ├── code_quality_check.py # 代码质量检查
│   ├── convert_icon.py     # 图标转换工具
│   └── verify_icons.py     # 图标验证工具
├── requirements.txt         # 核心依赖列表
├── requirements-dev.txt     # 开发依赖列表
├── BadgePatternTool.spec    # PyInstaller配置
├── CHANGELOG.md            # 更新日志
└── README.md               # 项目说明
```

## 📋 开发状态

当前版本: v1.4.0 (文档完善版)

### ✅ 已完成功能
- [x] **现代化GUI**: 基于PySide6的专业界面设计
- [x] **图片导入管理**: 多格式支持，批量导入，文件验证
- [x] **可配置徽章尺寸**: 支持多种预设尺寸和自定义配置
- [x] **交互式图片编辑**: 实时预览，精确缩放，位置调整，旋转支持
- [x] **智能排版引擎**: 网格/紧凑排列，自动计算最优位置
- [x] **多页面支持**: 自动分页处理，支持大批量图片
- [x] **多格式导出**: 高质量PDF/PNG/JPG，300DPI打印级别
- [x] **直接打印功能**: 内置打印对话框，支持彩色/黑白选择
- [x] **参数控制**: 间距调节，页边距设置，预览缩放
- [x] **自动排版**: 一键优化所有图片参数
- [x] **实时预览**: 所见即所得的编辑体验
- [x] **版本管理**: 自动化版本号管理工具
- [x] **完整文档**: 详细的技术文档和API参考

### 🎯 核心特性
- **完整工作流程**: 导入 → 配置 → 编辑 → 排版 → 导出/打印
- **高质量输出**: 300DPI打印级别，专业品质
- **用户友好**: 直观的界面和实时预览反馈
- **灵活配置**: 可配置徽章尺寸和出血区域
- **智能排版**: 支持网格和紧凑两种排列模式
- **跨平台**: 支持Windows、macOS、Linux

## 🛠️ 技术架构

### 技术栈
- **GUI框架**: PySide6 (Qt6) - 现代化跨平台界面
- **图像处理**: Pillow (PIL) - 专业图像处理库
- **PDF生成**: ReportLab - 高质量PDF输出
- **构建工具**: PyInstaller - 可执行文件打包

### 设计特点
- **模块化架构**: 清晰的代码结构，易于维护和扩展
- **MVC模式**: 分离界面、逻辑和数据层
- **智能缓存**: 多层级缓存系统，显著提升性能
- **错误处理**: 完善的异常处理和用户反馈
- **内存优化**: 高效的图像处理和资源管理
- **防抖机制**: 流畅的用户交互体验

## 🛠️ 开发工具

项目提供了完整的开发工具链：

### 快速命令
```bash
# 运行应用程序
python scripts/dev_tools.py run

# 运行测试
python scripts/dev_tools.py test

# 检查代码质量
python scripts/dev_tools.py quality

# 构建可执行文件
python scripts/dev_tools.py build

# 安装依赖
python scripts/dev_tools.py install
```

### 版本管理
```bash
# 查看当前版本状态
python scripts/version_manager.py --show

# 升级版本号
python scripts/version_manager.py 1.4.1

# 强制更新版本号
python scripts/version_manager.py 1.4.0 --force
```

### 测试框架
- **单元测试**: `tests/test_core.py`, `tests/test_utils.py`, `tests/test_ui.py`
- **集成测试**: `tests/test_integration.py`
- **性能测试**: `tests/test_performance.py`
- **多页面测试**: `tests/test_multi_page.py`
- **测试运行器**: `tests/run_tests.py`

### 代码质量
- 自动语法检查
- 导入语句规范检查
- 文档字符串完整性检查
- 项目结构验证
- 代码复杂度分析

### 构建工具
- PyInstaller自动化构建
- 图标验证和转换
- 文件大小优化
- 资源文件管理

## 📚 文档

项目包含完整的技术文档：

- **[代码架构文档](docs/代码架构文档.md)**: 详细的技术实现和算法原理
- **[快速入门指南](docs/快速入门指南.md)**: 新团队成员友好的入门指南
- **[API参考文档](docs/API参考文档.md)**: 完整的接口规范和使用示例
- **[需求文档](docs/需求文档.md)**: 项目需求和功能规格

## 🔗 相关链接

- **GitHub仓库**: https://github.com/fenglyu1314/BadgePatternTool
- **最新版本**: https://github.com/fenglyu1314/BadgePatternTool/releases/latest
- **问题反馈**: https://github.com/fenglyu1314/BadgePatternTool/issues

## 📄 许可证

本项目采用MIT许可证，详见 [LICENSE](LICENSE) 文件。

---

**当前版本**: v1.4.0
**最后更新**: 2025-06-20
**开发团队**: BadgePatternTool Team
