"""
主窗口界面模块
实现BadgePatternTool的主界面布局
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# 添加父目录到路径以便导入utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import *
from utils.file_handler import FileHandler, ImageItem
from core.image_processor import ImageProcessor, CircleEditor
from core.layout_engine import LayoutEngine
from core.export_manager import ExportManager

class MainWindow:
    """主窗口类"""
    
    def __init__(self, root):
        self.root = root
        self.file_handler = FileHandler()
        self.image_processor = ImageProcessor()
        self.layout_engine = LayoutEngine()
        self.export_manager = ExportManager()
        self.image_items = []  # 存储ImageItem对象列表
        self.current_selection = None  # 当前选中的图片项
        self.current_editor = None  # 当前的圆形编辑器

        # 初始化界面变量
        self.layout_mode = tk.StringVar(value="grid")
        self.spacing_var = tk.DoubleVar(value=DEFAULT_SPACING)
        self.margin_var = tk.DoubleVar(value=DEFAULT_MARGIN)
        self.export_format = tk.StringVar(value="pdf")
        self.scale_var = tk.DoubleVar(value=1.0)
        self.offset_x_var = tk.IntVar(value=0)
        self.offset_y_var = tk.IntVar(value=0)
        self.preview_scale_var = tk.DoubleVar(value=0.5)  # 预览缩放比例

        self.setup_window()
        self.create_menu()
        self.create_layout()
        self.create_status_bar()
        
    def setup_window(self):
        """设置窗口基本属性"""
        self.root.title(f"{APP_TITLE} v{APP_VERSION}")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=COLORS['bg_primary'])
        
        # 设置窗口居中
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (WINDOW_WIDTH // 2)
        y = (self.root.winfo_screenheight() // 2) - (WINDOW_HEIGHT // 2)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        
        # 设置最小窗口大小
        self.root.minsize(800, 600)
        
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导入图片...", command=self.import_images)
        file_menu.add_separator()
        file_menu.add_command(label="导出PDF...", command=self.export_pdf)
        file_menu.add_command(label="导出PNG...", command=self.export_png)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="全选", command=self.select_all)
        edit_menu.add_command(label="清空列表", command=self.clear_all)
        
        # 视图菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="视图", menu=view_menu)
        view_menu.add_command(label="刷新预览", command=self.refresh_preview)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
        
    def create_layout(self):
        """创建主界面布局"""
        # 创建主框架
        main_frame = tk.Frame(self.root, bg=COLORS['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建三个主要区域
        self.create_image_list_panel(main_frame)
        self.create_edit_preview_panel(main_frame)
        self.create_settings_panel(main_frame)
        
    def create_image_list_panel(self, parent):
        """创建图片列表面板（左侧）"""
        # 图片列表框架
        list_frame = tk.LabelFrame(
            parent, 
            text="图片列表", 
            bg=COLORS['bg_secondary'],
            fg=COLORS['text'],
            font=("微软雅黑", 10, "bold")
        )
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        list_frame.configure(width=250)
        list_frame.pack_propagate(False)
        
        # 导入按钮
        import_btn = tk.Button(
            list_frame,
            text="导入图片",
            command=self.import_images,
            bg=COLORS['accent'],
            fg="white",
            font=("微软雅黑", 10),
            relief=tk.FLAT,
            padx=20,
            pady=5
        )
        import_btn.pack(pady=10, padx=10, fill=tk.X)
        
        # 图片列表框架
        list_container = tk.Frame(list_frame, bg=COLORS['bg_secondary'])
        list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 滚动条
        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 图片列表（使用Listbox临时实现，后续会改为自定义控件）
        self.image_listbox = tk.Listbox(
            list_container,
            yscrollcommand=scrollbar.set,
            bg=COLORS['bg_secondary'],
            fg=COLORS['text'],
            font=("微软雅黑", 9),
            selectmode=tk.SINGLE,
            relief=tk.FLAT,
            borderwidth=1
        )
        self.image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.image_listbox.yview)
        
        # 绑定选择事件
        self.image_listbox.bind('<<ListboxSelect>>', self.on_image_select)
        
        # 操作按钮框架
        btn_frame = tk.Frame(list_frame, bg=COLORS['bg_secondary'])
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # 删除按钮
        delete_btn = tk.Button(
            btn_frame,
            text="删除",
            command=self.delete_selected,
            bg=COLORS['error'],
            fg="white",
            font=("微软雅黑", 9),
            relief=tk.FLAT
        )
        delete_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # 清空按钮
        clear_btn = tk.Button(
            btn_frame,
            text="清空",
            command=self.clear_all,
            bg=COLORS['warning'],
            fg="white",
            font=("微软雅黑", 9),
            relief=tk.FLAT
        )
        clear_btn.pack(side=tk.LEFT)
        
    def create_edit_preview_panel(self, parent):
        """创建编辑预览面板（中间）"""
        # 编辑预览框架
        preview_frame = tk.LabelFrame(
            parent,
            text="编辑预览区",
            bg=COLORS['bg_secondary'],
            fg=COLORS['text'],
            font=("微软雅黑", 10, "bold")
        )
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 创建Notebook用于切换不同视图
        self.notebook = ttk.Notebook(preview_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 单图编辑标签页
        self.edit_frame = tk.Frame(self.notebook, bg=COLORS['bg_secondary'])
        self.notebook.add(self.edit_frame, text="单图编辑")
        
        # 编辑区域
        self.create_edit_area()
        
        # A4排版预览标签页
        self.layout_frame = tk.Frame(self.notebook, bg=COLORS['bg_secondary'])
        self.notebook.add(self.layout_frame, text="A4排版预览")
        
        # A4排版预览区域
        self.create_layout_area()
        
    def create_settings_panel(self, parent):
        """创建参数设置面板（右侧）"""
        # 设置面板框架
        settings_frame = tk.LabelFrame(
            parent,
            text="参数设置",
            bg=COLORS['bg_secondary'],
            fg=COLORS['text'],
            font=("微软雅黑", 10, "bold")
        )
        settings_frame.pack(side=tk.RIGHT, fill=tk.Y)
        settings_frame.configure(width=200)
        settings_frame.pack_propagate(False)
        
        # 布局设置
        layout_group = tk.LabelFrame(
            settings_frame,
            text="布局设置",
            bg=COLORS['bg_secondary'],
            fg=COLORS['text'],
            font=("微软雅黑", 9)
        )
        layout_group.pack(fill=tk.X, padx=10, pady=10)
        
        # 布局模式选择
        tk.Label(layout_group, text="排列模式:", bg=COLORS['bg_secondary'], fg=COLORS['text']).pack(anchor=tk.W, padx=5, pady=(5, 0))
        grid_radio = tk.Radiobutton(
            layout_group, text="网格排列", variable=self.layout_mode, value="grid",
            bg=COLORS['bg_secondary'], fg=COLORS['text'], command=self.on_layout_change
        )
        grid_radio.pack(anchor=tk.W, padx=15)
        
        compact_radio = tk.Radiobutton(
            layout_group, text="紧密排列", variable=self.layout_mode, value="compact",
            bg=COLORS['bg_secondary'], fg=COLORS['text'], command=self.on_layout_change
        )
        compact_radio.pack(anchor=tk.W, padx=15, pady=(0, 5))
        
        # 间距设置
        tk.Label(layout_group, text="间距(mm):", bg=COLORS['bg_secondary'], fg=COLORS['text']).pack(anchor=tk.W, padx=5)
        spacing_scale = tk.Scale(
            layout_group, from_=0, to=20, resolution=1, orient=tk.HORIZONTAL,
            variable=self.spacing_var, command=self.on_spacing_change,
            bg=COLORS['bg_secondary'], fg=COLORS['text']
        )
        spacing_scale.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # 导出设置
        export_group = tk.LabelFrame(
            settings_frame,
            text="导出设置",
            bg=COLORS['bg_secondary'],
            fg=COLORS['text'],
            font=("微软雅黑", 9)
        )
        export_group.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # 导出格式
        tk.Label(export_group, text="输出格式:", bg=COLORS['bg_secondary'], fg=COLORS['text']).pack(anchor=tk.W, padx=5, pady=(5, 0))
        format_combo = ttk.Combobox(
            export_group, textvariable=self.export_format,
            values=["pdf", "png", "jpg"], state="readonly", width=15
        )
        format_combo.pack(padx=5, pady=(0, 5))
        
        # 导出按钮
        export_btn = tk.Button(
            export_group,
            text="导出文件",
            command=self.export_file,
            bg=COLORS['success'],
            fg="white",
            font=("微软雅黑", 10),
            relief=tk.FLAT,
            pady=5
        )
        export_btn.pack(fill=tk.X, padx=5, pady=(0, 5))
        
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = tk.Label(
            self.root,
            text="就绪",
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg=COLORS['bg_primary'],
            fg=COLORS['text'],
            font=("微软雅黑", 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_edit_area(self):
        """创建编辑区域"""
        # 主编辑容器
        edit_container = tk.Frame(self.edit_frame, bg=COLORS['bg_secondary'])
        edit_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 预览区域
        preview_frame = tk.Frame(edit_container, bg=COLORS['bg_secondary'])
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 预览标签
        tk.Label(
            preview_frame,
            text="圆形预览",
            bg=COLORS['bg_secondary'],
            fg=COLORS['text'],
            font=("微软雅黑", 10, "bold")
        ).pack(pady=(0, 10))

        # 预览画布
        self.preview_canvas = tk.Canvas(
            preview_frame,
            width=250,
            height=250,
            bg="white",
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.preview_canvas.pack()

        # 控制面板
        control_frame = tk.Frame(edit_container, bg=COLORS['bg_secondary'])
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))
        control_frame.configure(width=200)
        control_frame.pack_propagate(False)

        # 控制标题
        tk.Label(
            control_frame,
            text="编辑控制",
            bg=COLORS['bg_secondary'],
            fg=COLORS['text'],
            font=("微软雅黑", 10, "bold")
        ).pack(pady=(0, 15))

        # 缩放控制
        scale_group = tk.LabelFrame(
            control_frame,
            text="缩放",
            bg=COLORS['bg_secondary'],
            fg=COLORS['text']
        )
        scale_group.pack(fill=tk.X, pady=(0, 10))
        self.scale_scale = tk.Scale(
            scale_group,
            from_=0.1, to=3.0, resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.scale_var,
            command=self.on_scale_change,
            bg=COLORS['bg_secondary'],
            fg=COLORS['text']
        )
        self.scale_scale.pack(fill=tk.X, padx=5, pady=5)

        # 位置控制
        position_group = tk.LabelFrame(
            control_frame,
            text="位置调整",
            bg=COLORS['bg_secondary'],
            fg=COLORS['text']
        )
        position_group.pack(fill=tk.X, pady=(0, 10))

        # X轴偏移
        tk.Label(position_group, text="X偏移:", bg=COLORS['bg_secondary'], fg=COLORS['text']).pack(anchor=tk.W, padx=5)
        self.offset_x_scale = tk.Scale(
            position_group,
            from_=-100, to=100, resolution=1,
            orient=tk.HORIZONTAL,
            variable=self.offset_x_var,
            command=self.on_position_change,
            bg=COLORS['bg_secondary'],
            fg=COLORS['text']
        )
        self.offset_x_scale.pack(fill=tk.X, padx=5)

        # Y轴偏移
        tk.Label(position_group, text="Y偏移:", bg=COLORS['bg_secondary'], fg=COLORS['text']).pack(anchor=tk.W, padx=5)
        self.offset_y_scale = tk.Scale(
            position_group,
            from_=-100, to=100, resolution=1,
            orient=tk.HORIZONTAL,
            variable=self.offset_y_var,
            command=self.on_position_change,
            bg=COLORS['bg_secondary'],
            fg=COLORS['text']
        )
        self.offset_y_scale.pack(fill=tk.X, padx=5, pady=(0, 5))

        # 操作按钮
        btn_frame = tk.Frame(control_frame, bg=COLORS['bg_secondary'])
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        # 重置按钮
        reset_btn = tk.Button(
            btn_frame,
            text="重置",
            command=self.reset_edit,
            bg=COLORS['warning'],
            fg="white",
            font=("微软雅黑", 9),
            relief=tk.FLAT
        )
        reset_btn.pack(fill=tk.X, pady=(0, 5))

        # 应用按钮
        apply_btn = tk.Button(
            btn_frame,
            text="应用",
            command=self.apply_edit,
            bg=COLORS['success'],
            fg="white",
            font=("微软雅黑", 9),
            relief=tk.FLAT
        )
        apply_btn.pack(fill=tk.X)

        # 初始显示提示
        self.show_edit_hint()

    def create_layout_area(self):
        """创建A4排版预览区域"""
        # 主容器
        layout_container = tk.Frame(self.layout_frame, bg=COLORS['bg_secondary'])
        layout_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 预览区域
        preview_frame = tk.Frame(layout_container, bg=COLORS['bg_secondary'])
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 标题和信息
        info_frame = tk.Frame(preview_frame, bg=COLORS['bg_secondary'])
        info_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            info_frame,
            text="A4排版预览",
            bg=COLORS['bg_secondary'],
            fg=COLORS['text'],
            font=("微软雅黑", 10, "bold")
        ).pack(side=tk.LEFT)

        # 布局信息标签
        self.layout_info_label = tk.Label(
            info_frame,
            text="",
            bg=COLORS['bg_secondary'],
            fg=COLORS['text'],
            font=("微软雅黑", 9)
        )
        self.layout_info_label.pack(side=tk.RIGHT)

        # 创建滚动区域
        canvas_frame = tk.Frame(preview_frame, bg=COLORS['bg_secondary'])
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        # A4预览画布 - 使用更大的尺寸以显示完整A4
        self.layout_canvas = tk.Canvas(
            canvas_frame,
            bg="white",
            relief=tk.SUNKEN,
            borderwidth=2,
            scrollregion=(0, 0, 500, 707)  # A4比例 (210:297) 放大
        )

        # 垂直滚动条
        v_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.layout_canvas.yview)
        self.layout_canvas.configure(yscrollcommand=v_scrollbar.set)

        # 水平滚动条
        h_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.layout_canvas.xview)
        self.layout_canvas.configure(xscrollcommand=h_scrollbar.set)

        # 布局滚动条和画布
        self.layout_canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        # 配置网格权重
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        # 绑定鼠标滚轮事件
        self.layout_canvas.bind("<MouseWheel>", self.on_canvas_scroll)
        self.layout_canvas.bind("<Button-4>", self.on_canvas_scroll)
        self.layout_canvas.bind("<Button-5>", self.on_canvas_scroll)

        # 控制面板
        layout_control_frame = tk.Frame(layout_container, bg=COLORS['bg_secondary'])
        layout_control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))
        layout_control_frame.configure(width=180)
        layout_control_frame.pack_propagate(False)

        # 控制标题
        tk.Label(
            layout_control_frame,
            text="排版控制",
            bg=COLORS['bg_secondary'],
            fg=COLORS['text'],
            font=("微软雅黑", 10, "bold")
        ).pack(pady=(0, 15))

        # 布局模式（移动到这里，与原设置面板同步）
        layout_mode_group = tk.LabelFrame(
            layout_control_frame,
            text="排列模式",
            bg=COLORS['bg_secondary'],
            fg=COLORS['text']
        )
        layout_mode_group.pack(fill=tk.X, pady=(0, 10))

        # 同步布局模式变量
        grid_radio2 = tk.Radiobutton(
            layout_mode_group, text="网格排列", variable=self.layout_mode, value="grid",
            bg=COLORS['bg_secondary'], fg=COLORS['text'], command=self.update_layout_preview
        )
        grid_radio2.pack(anchor=tk.W, padx=5, pady=2)

        compact_radio2 = tk.Radiobutton(
            layout_mode_group, text="紧密排列", variable=self.layout_mode, value="compact",
            bg=COLORS['bg_secondary'], fg=COLORS['text'], command=self.update_layout_preview
        )
        compact_radio2.pack(anchor=tk.W, padx=5, pady=2)

        # 间距控制（同步）
        spacing_group = tk.LabelFrame(
            layout_control_frame,
            text="间距设置",
            bg=COLORS['bg_secondary'],
            fg=COLORS['text']
        )
        spacing_group.pack(fill=tk.X, pady=(0, 10))

        tk.Label(spacing_group, text="间距(mm):", bg=COLORS['bg_secondary'], fg=COLORS['text']).pack(anchor=tk.W, padx=5)

        # 同步间距变量
        spacing_scale2 = tk.Scale(
            spacing_group, from_=0, to=20, resolution=1, orient=tk.HORIZONTAL,
            variable=self.spacing_var, command=self.update_layout_preview,
            bg=COLORS['bg_secondary'], fg=COLORS['text']
        )
        spacing_scale2.pack(fill=tk.X, padx=5, pady=(0, 5))

        # 页边距控制
        margin_group = tk.LabelFrame(
            layout_control_frame,
            text="页边距",
            bg=COLORS['bg_secondary'],
            fg=COLORS['text']
        )
        margin_group.pack(fill=tk.X, pady=(0, 10))

        tk.Label(margin_group, text="边距(mm):", bg=COLORS['bg_secondary'], fg=COLORS['text']).pack(anchor=tk.W, padx=5)
        margin_scale = tk.Scale(
            margin_group, from_=5, to=30, resolution=1, orient=tk.HORIZONTAL,
            variable=self.margin_var, command=self.update_layout_preview,
            bg=COLORS['bg_secondary'], fg=COLORS['text']
        )
        margin_scale.pack(fill=tk.X, padx=5, pady=(0, 5))

        # 预览缩放控制
        preview_group = tk.LabelFrame(
            layout_control_frame,
            text="预览缩放",
            bg=COLORS['bg_secondary'],
            fg=COLORS['text']
        )
        preview_group.pack(fill=tk.X, pady=(0, 10))

        tk.Label(preview_group, text="缩放(%):", bg=COLORS['bg_secondary'], fg=COLORS['text']).pack(anchor=tk.W, padx=5)

        preview_scale_scale = tk.Scale(
            preview_group, from_=0.2, to=1.0, resolution=0.1, orient=tk.HORIZONTAL,
            variable=self.preview_scale_var, command=self.update_layout_preview,
            bg=COLORS['bg_secondary'], fg=COLORS['text']
        )
        preview_scale_scale.pack(fill=tk.X, padx=5, pady=(0, 5))

        # 操作按钮
        layout_btn_frame = tk.Frame(layout_control_frame, bg=COLORS['bg_secondary'])
        layout_btn_frame.pack(fill=tk.X, pady=(10, 0))

        # 刷新预览按钮
        refresh_btn = tk.Button(
            layout_btn_frame,
            text="刷新预览",
            command=self.update_layout_preview,
            bg=COLORS['accent'],
            fg="white",
            font=("微软雅黑", 9),
            relief=tk.FLAT
        )
        refresh_btn.pack(fill=tk.X, pady=(0, 5))

        # 自动排版按钮
        auto_layout_btn = tk.Button(
            layout_btn_frame,
            text="自动排版",
            command=self.auto_layout,
            bg=COLORS['success'],
            fg="white",
            font=("微软雅黑", 9),
            relief=tk.FLAT
        )
        auto_layout_btn.pack(fill=tk.X)

        # 初始显示提示
        self.show_layout_hint()

    def show_layout_hint(self):
        """显示排版提示"""
        self.layout_canvas.delete("all")
        # 在画布中心显示提示
        canvas_width = 500
        canvas_height = 707
        self.layout_canvas.create_text(
            canvas_width // 2, canvas_height // 2,
            text="导入图片后\n自动显示排版预览\n\n可使用鼠标滚轮或滚动条\n查看完整A4页面",
            font=("微软雅黑", 12),
            fill=COLORS['text'],
            justify=tk.CENTER
        )
        self.layout_info_label.config(text="")

    def on_canvas_scroll(self, event):
        """处理画布滚轮事件"""
        try:
            # 检测滚轮方向
            if event.delta:  # Windows
                delta = -1 * (event.delta / 120)
            elif event.num == 4:  # Linux 向上
                delta = -1
            elif event.num == 5:  # Linux 向下
                delta = 1
            else:
                return

            # 滚动画布
            self.layout_canvas.yview_scroll(int(delta), "units")
        except Exception as e:
            print(f"滚轮事件处理失败: {e}")

    def show_edit_hint(self):
        """显示编辑提示"""
        self.preview_canvas.delete("all")
        self.preview_canvas.create_text(
            125, 125,
            text="选择左侧图片\n开始编辑",
            font=("微软雅黑", 12),
            fill=COLORS['text'],
            justify=tk.CENTER
        )

    # 事件处理方法
    def import_images(self):
        """导入图片"""
        try:
            # 选择图片文件
            file_paths = self.file_handler.select_images(self.root)

            if not file_paths:
                return

            # 检查图片数量限制
            total_count = len(self.image_items) + len(file_paths)
            if total_count > MAX_IMAGE_COUNT:
                messagebox.showwarning(
                    "数量限制",
                    f"最多只能导入{MAX_IMAGE_COUNT}张图片，当前已有{len(self.image_items)}张"
                )
                return

            # 添加图片到列表
            added_count = 0
            for file_path in file_paths:
                try:
                    # 检查是否已存在
                    if any(item.file_path == file_path for item in self.image_items):
                        continue

                    # 创建图片项
                    image_item = ImageItem(file_path)
                    self.image_items.append(image_item)

                    # 添加到界面列表
                    display_text = f"{image_item.get_display_name()} ({image_item.get_size_text()})"
                    self.image_listbox.insert(tk.END, display_text)

                    added_count += 1

                except Exception as e:
                    print(f"添加图片失败 {file_path}: {e}")
                    continue

            # 更新状态
            if added_count > 0:
                self.status_bar.config(text=f"成功导入 {added_count} 张图片，总计 {len(self.image_items)} 张")
                # 选中最后一个添加的项
                if self.image_items:
                    last_index = len(self.image_items) - 1
                    self.image_listbox.selection_set(last_index)
                    self.image_listbox.see(last_index)

                # 更新A4排版预览
                self.update_layout_preview()
            else:
                self.status_bar.config(text="没有新图片被添加")

        except Exception as e:
            messagebox.showerror("错误", f"导入图片时发生错误：{str(e)}")
            self.status_bar.config(text="图片导入失败")
        
    def export_pdf(self):
        """导出PDF"""
        self.export_file_with_format('pdf')

    def export_png(self):
        """导出PNG"""
        self.export_file_with_format('png')

    def export_file(self):
        """根据选择的格式导出文件"""
        format_type = self.export_format.get()
        self.export_file_with_format(format_type)

    def export_file_with_format(self, format_type):
        """
        导出文件（通用方法）
        参数: format_type - 文件格式 ('pdf', 'png', 'jpg')
        """
        try:
            # 验证导出设置
            is_valid, error_msg = self.export_manager.validate_export_settings(self.image_items, "temp")
            if not is_valid:
                messagebox.showwarning("导出失败", error_msg)
                return

            # 获取当前设置
            layout_type = self.layout_mode.get()
            spacing_mm = self.spacing_var.get()
            margin_mm = self.margin_var.get()

            # 选择保存路径
            suggested_filename = self.export_manager.get_suggested_filename(format_type.upper(), layout_type)

            if format_type.lower() == 'pdf':
                file_types = [("PDF文件", "*.pdf"), ("所有文件", "*.*")]
            elif format_type.lower() == 'png':
                file_types = [("PNG文件", "*.png"), ("所有文件", "*.*")]
            else:  # jpg
                file_types = [("JPEG文件", "*.jpg"), ("所有文件", "*.*")]

            from tkinter import filedialog
            output_path = filedialog.asksaveasfilename(
                title=f"保存{format_type.upper()}文件",
                defaultextension=f".{format_type.lower()}",
                filetypes=file_types,
                initialfile=suggested_filename
            )

            if not output_path:
                return  # 用户取消

            # 显示进度提示
            self.status_bar.config(text=f"正在导出{format_type.upper()}文件...")
            self.root.update()

            # 执行导出
            if format_type.lower() == 'pdf':
                success, count = self.export_manager.export_to_pdf(
                    self.image_items, output_path, layout_type, spacing_mm, margin_mm
                )
            else:
                success, count = self.export_manager.export_to_image(
                    self.image_items, output_path, format_type.upper(),
                    layout_type, spacing_mm, margin_mm
                )

            if success:
                self.status_bar.config(text=f"{format_type.upper()}导出成功")
                messagebox.showinfo(
                    "导出成功",
                    f"成功导出{count}张图片到{format_type.upper()}文件！\n\n"
                    f"文件路径：{output_path}\n"
                    f"布局模式：{'网格排列' if layout_type == 'grid' else '紧密排列'}\n"
                    f"图片数量：{count}张"
                )

                # 询问是否打开文件夹
                if messagebox.askyesno("打开文件夹", "是否打开文件所在文件夹？"):
                    import subprocess
                    subprocess.run(['explorer', '/select,', output_path.replace('/', '\\')])

            else:
                self.status_bar.config(text=f"{format_type.upper()}导出失败")
                messagebox.showerror("导出失败", f"导出{format_type.upper()}文件时发生错误")

        except Exception as e:
            self.status_bar.config(text="导出失败")
            messagebox.showerror("错误", f"导出过程中发生错误：{str(e)}")
        
    def select_all(self):
        """全选"""
        messagebox.showinfo("提示", "全选功能开发中...")
        
    def clear_all(self):
        """清空列表"""
        if self.image_items:
            result = messagebox.askyesno("确认", "确定要清空所有图片吗？")
            if result:
                self.image_items.clear()
                self.image_listbox.delete(0, tk.END)
                self.current_selection = None
                self.status_bar.config(text="已清空图片列表")

    def delete_selected(self):
        """删除选中项"""
        selection = self.image_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.image_items):
                # 删除数据
                deleted_item = self.image_items.pop(index)
                # 删除界面项
                self.image_listbox.delete(index)
                # 清除选择
                self.current_selection = None
                self.status_bar.config(text=f"已删除: {deleted_item.get_display_name()}")

                # 如果还有项目，选中相邻的项
                if self.image_items:
                    new_index = min(index, len(self.image_items) - 1)
                    self.image_listbox.selection_set(new_index)
                    self.image_listbox.see(new_index)
        
    def refresh_preview(self):
        """刷新预览"""
        messagebox.showinfo("提示", "预览刷新功能开发中...")
        
    def on_image_select(self, event):
        """图片选择事件"""
        selection = self.image_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.image_items):
                self.current_selection = self.image_items[index]
                item_info = f"已选择: {self.current_selection.get_display_name()} " \
                           f"({self.current_selection.get_size_text()}, {self.current_selection.get_file_size_text()})"
                self.status_bar.config(text=item_info)

                # 创建编辑器并更新预览
                self.load_image_editor()
        else:
            self.current_selection = None
            self.current_editor = None
            self.show_edit_hint()

    def load_image_editor(self):
        """加载图片编辑器"""
        if self.current_selection:
            try:
                # 创建圆形编辑器
                self.current_editor = CircleEditor(self.current_selection.file_path)

                # 更新控制滑块的值
                self.scale_var.set(self.current_editor.scale)
                self.offset_x_var.set(self.current_editor.offset_x)
                self.offset_y_var.set(self.current_editor.offset_y)

                # 更新预览
                self.update_preview()

            except Exception as e:
                print(f"加载编辑器失败: {e}")
                self.show_edit_hint()

    def update_preview(self):
        """更新预览显示"""
        if self.current_editor:
            try:
                # 获取预览图片
                preview_img = self.current_editor.get_preview(preview_size=240)

                # 清除画布并显示新图片
                self.preview_canvas.delete("all")
                self.preview_canvas.create_image(125, 125, image=preview_img)

                # 保持图片引用防止被垃圾回收
                self.preview_canvas.image = preview_img

            except Exception as e:
                print(f"更新预览失败: {e}")
                self.show_edit_hint()

    def on_scale_change(self, value):
        """缩放改变事件"""
        if self.current_editor:
            self.current_editor.set_scale(float(value))
            self.update_preview()

    def on_position_change(self, value=None):
        """位置改变事件"""
        if self.current_editor:
            offset_x = self.offset_x_var.get()
            offset_y = self.offset_y_var.get()
            self.current_editor.set_offset(offset_x, offset_y)
            self.update_preview()

    def reset_edit(self):
        """重置编辑参数"""
        if self.current_editor:
            self.current_editor.reset_to_optimal()

            # 更新控制滑块
            self.scale_var.set(self.current_editor.scale)
            self.offset_x_var.set(self.current_editor.offset_x)
            self.offset_y_var.set(self.current_editor.offset_y)

            # 更新预览
            self.update_preview()

            self.status_bar.config(text="已重置编辑参数")

    def apply_edit(self):
        """应用编辑"""
        if self.current_editor and self.current_selection:
            # 保存编辑参数到图片项
            self.current_selection.scale = self.current_editor.scale
            self.current_selection.offset_x = self.current_editor.offset_x
            self.current_selection.offset_y = self.current_editor.offset_y
            self.current_selection.rotation = self.current_editor.rotation
            self.current_selection.is_processed = True

            self.status_bar.config(text="编辑参数已应用")

            # 更新A4排版预览
            self.update_layout_preview()

            messagebox.showinfo("提示", "编辑参数已保存，可在A4排版预览中查看效果")
            
    def on_layout_change(self):
        """布局模式改变事件"""
        mode = self.layout_mode.get()
        self.status_bar.config(text=f"布局模式: {'网格排列' if mode == 'grid' else '紧密排列'}")
        self.update_layout_preview()

    def on_spacing_change(self, value):
        """间距改变事件"""
        self.status_bar.config(text=f"间距设置: {value}mm")
        self.update_layout_preview()

    def update_layout_preview(self, value=None):
        """更新A4排版预览"""
        if not self.image_items:
            self.show_layout_hint()
            return

        try:
            # 获取当前设置
            layout_type = self.layout_mode.get()
            spacing_mm = self.spacing_var.get()
            margin_mm = self.margin_var.get()

            # 创建排版预览 - 使用用户选择的缩放比例
            preview_scale = self.preview_scale_var.get()
            preview_img = self.layout_engine.create_layout_preview(
                self.image_items, layout_type, spacing_mm, margin_mm, preview_scale=preview_scale
            )

            # 更新画布
            self.layout_canvas.delete("all")

            # 在画布左上角显示图片，而不是居中
            self.layout_canvas.create_image(0, 0, anchor=tk.NW, image=preview_img)

            # 更新滚动区域以适应图片大小
            self.layout_canvas.configure(scrollregion=self.layout_canvas.bbox("all"))

            # 保持图片引用
            self.layout_canvas.image = preview_img

            # 更新布局信息
            layout_info = self.layout_engine.get_layout_info(layout_type, spacing_mm, margin_mm)
            info_text = f"可放置: {layout_info['max_count']}个 | 已有: {len(self.image_items)}个"
            self.layout_info_label.config(text=info_text)

            # 更新状态栏
            self.status_bar.config(text=f"排版预览已更新 - {layout_info['type']}模式")

        except Exception as e:
            print(f"更新排版预览失败: {e}")
            self.show_layout_hint()

    def auto_layout(self):
        """自动排版（为所有图片应用最佳参数）"""
        if not self.image_items:
            messagebox.showwarning("提示", "请先导入图片")
            return

        try:
            processed_count = 0
            for image_item in self.image_items:
                if not image_item.is_processed:
                    # 计算最佳缩放
                    optimal_scale = self.image_processor.get_optimal_scale(image_item.file_path)

                    # 应用最佳参数
                    image_item.scale = optimal_scale
                    image_item.offset_x = 0
                    image_item.offset_y = 0
                    image_item.rotation = 0
                    image_item.is_processed = True

                    processed_count += 1

            # 更新预览
            self.update_layout_preview()

            if processed_count > 0:
                self.status_bar.config(text=f"自动排版完成，处理了 {processed_count} 张图片")
                messagebox.showinfo("完成", f"自动排版完成！\n处理了 {processed_count} 张图片")
            else:
                messagebox.showinfo("提示", "所有图片都已处理过")

        except Exception as e:
            messagebox.showerror("错误", f"自动排版失败：{str(e)}")
        
    def show_about(self):
        """显示关于对话框"""
        messagebox.showinfo(
            "关于",
            f"{APP_TITLE} v{APP_VERSION}\n\n"
            "徽章图案制作工具\n"
            "支持图片裁剪和A4排版\n\n"
            "开发中..."
        )
