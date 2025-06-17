---
title: "只借助QPrintPreviewDialog就能实现PySide6的打印预览、打印纸质报表、导出为PDF文件的功能"
source: "https://blog.csdn.net/zhouyang/article/details/135900120"
author:
  - "[[zhouyang]]"
published: 2024-01-28
created: 2025-06-17
description: "文章浏览阅读1.3k次，点赞11次，收藏10次。本文介绍了如何使用Pyside6中的QPrintPreviewDialog实现打印预览、纸质报表打印及PDF导出，通过提供两个关键函数，用户可以轻松定制纸张大小、布局和内容，满足实际需求。"
tags:
  - "clippings"
---
AI 搜索

[晨辉软件](https://blog.csdn.net/zhouyang "晨辉软件") 已于 2024-01-29 20:09:15 修改

文章标签： [python](https://so.csdn.net/so/search/s.do?q=python&t=all&o=vip&s=&l=&f=&viparticle=&from_tracking_code=tag_word&from_code=app_blog_art) [pdf](https://so.csdn.net/so/search/s.do?q=pdf&t=all&o=vip&s=&l=&f=&viparticle=&from_tracking_code=tag_word&from_code=app_blog_art)

于 2024-01-28 21:13:42 首次发布

版权声明：本文为博主原创文章，遵循 [CC 4.0 BY-SA](http://creativecommons.org/licenses/by-sa/4.0/) 版权协议，转载请附上原文出处链接和本声明。

本文链接： [https://blog.csdn.net/zhouyang/article/details/135900120](https://blog.csdn.net/zhouyang/article/details/135900120)

版权

本文介绍了如何使用Pyside6中的QPrintPreviewDialog实现打印预览、纸质报表打印及PDF导出，通过提供两个关键函数，用户可以轻松定制纸张大小、布局和内容，满足实际需求。

摘要生成于 [C知道](https://ai.csdn.net/?utm_source=cknow_pc_ai_abstract) ，由 DeepSeek-R1 满血版支持， [前往体验 >](https://ai.csdn.net/?utm_source=cknow_pc_ai_abstract)

使用 [Pyside6](https://so.csdn.net/so/search?q=Pyside6&spm=1001.2101.3001.7020) 开发软件经常会遇到打印报表的需求，有QPrintPreviewDialog、QPrint、QPrintPreviewWidget等选择。我经过较长时间的摸索，找到了一条只需要借助QPrintPreviewDialog就能实现打印预览、打印纸质报表、导出为PDF文件的功能，这里分享给大家。

只需要在自己的代码中增加两个函数。

第一个，打开QPrintPreviewDialog的函数，此函数一般应作为某个按钮clicked信号的槽函数，以便于启动执行(比如，这里定义为按钮but1的clicked信号的槽函数)。可以在这个函数中定义预览打印机的纸张类型等。

\# 不需要在Designer设计器中进行信号/槽的设置，加上@QtCore.Slot()这一行，就表示下面的这个函数是某个信号的槽函数，函数名以on开头

```
@QtCore.Slot()
def on_but1_clicked(self):
    user_page = QPageLayout() 
    # A4纸
    user_page.setPageSize(QPageSize(QPageSize.A4))
    # 横向
    user_page.setOrientation(QPageLayout.Orientation.Landscape)
    # 设置页边距
    user_page.setMargins(QMarginsF(30, 30, 30, 30))
    preview = QPrintPreviewDialog()  # 不指定打印机
    preview.printer().setPageLayout(user_page)  # 设置预览打印机的纸张
    # 将打印预览信号连接到槽函数,不加lambda就预览不到内容
    preview.paintRequested.connect(lambda: self.my_paint(preview.printer()))
    # 打印预览窗口最大化
    preview.setWindowState(Qt.WindowMaximized)
    # 执行打印预览
    preview.exec()
```

第二个，接收预览信号的槽函数，里面是打印的具体内容。这里打印一张考场的门牌

def my\_preview\_kcmp(self, user\_print):

mp = QPainter(user\_print)

user\_font = [QFont](https://so.csdn.net/so/search?q=QFont&spm=1001.2101.3001.7020) ()

user\_font.setFamily("宋体")

user\_font.setPointSize(48)

mp.setFont(user\_font) # 设置字体

\# 居中打印考试名称

mp.drawText(QRect(0, 90, 1035, 100), Qt.AlignmentFlag.AlignCenter, "湖北省2023年专升本考试")

\# 更换字体

user\_font.setFamily("黑体")

user\_font.setPointSize(120)

mp.setFont(user\_font) # 设置字体

\# 打印考场

mp.drawText(QRect(0, 280, 1035, 200), Qt.AlignmentFlag.AlignCenter, "第 1 考场")

\# 如果有多页，添加一页后再打印具体内容

\# user\_print.newPage()

\# mp.drawText(QRect(0, 280, 1035, 200), Qt.AlignmentFlag.AlignCenter, "第 2 页的内容")

mp.end() # 结束

运行时，单击but1按钮，会弹出打印预览对话框，并显示具体的打印内容。可以在这个对话框中更改纸张类型、更改页面设置，点击“打印机”按钮就能执行打印操作，在弹出的打印对话框中选择真实的打印机就能打印出纸质报表，选择PDF打印机或勾选“打印到文件”，就能实现将报表转为PDF文件。具体如下图：

![](https://i-blog.csdnimg.cn/blog_migrate/a05216039deaafa05f9266aedc6abbda.png)

博客[Qt *打印* *功能* ； *QPr* *int* *Preview* Widget使用； *QPr* *int* *Dialog* 使用； *QPr* *int* *Preview* *Dialog* 使用；](https://blog.csdn.net/qq_36626674/article/details/120828490)

[qq\_36626674的博客](https://blog.csdn.net/qq_36626674)

11-03 8675[一、 *QPr* *int* *Dialog* 使用 在需要使用的地方直接使用： *QPr* *int* er pr *int* erpng;//创建一个 *打印* 机 *QPr* *int* *Dialog* dlg(&pr *int* erpng);//创建 *打印* 页面，并传入 *打印* 机 qDebug()<<dlg.exec();//显示 *打印* 界面，返回值判断点击的是0表示取消，1表示 *打印* //界面显示后，可以通过pr *int* erpng获取设置的 *打印* 页面信息 qDebug()<<" *打印* 页面设置的纸张页面布局：](https://blog.csdn.net/qq_36626674/article/details/120828490)

博客[17-窗口、窗口控件、对话框以及相关 *功能* 类- *打印* 对话框和 *打印* *预览*](https://blog.csdn.net/qq_40597070/article/details/131038086)

[\*\*\*\*\*](https://blog.csdn.net/qq_40597070)

06-05 1355[QAbstractPr *int* *Dialog* 类为用于配置 *打印* 机的 *打印* 对话框提供了一个基本 *实现* 此类 *实现* getter和setter函数,这些函数用于自定义 *打印* 对话框中显示的设置,但不直接使用。使用 *QPr* *int* *Dialog* 在应用程序中显示 *打印* 对话框。](https://blog.csdn.net/qq_40597070/article/details/131038086)

博客[Qt——day02](https://blog.csdn.net/qq_43403759/article/details/122022994)

[qq\_43403759的博客](https://blog.csdn.net/qq_43403759)

12-20 2738[文章目录一、QMainWindow1.菜单栏1.1 创建菜单栏1.2 往菜单栏添加菜单1.3 往某个菜单添加菜单动作1.4 在菜单项间增加分割线1.5 菜单栏数量问题2.工具栏2.1 创建工具栏对象2.2 改变工具栏的默认位置2.3 设置工具栏运行停靠的位置2.4 设置工具栏浮动2.5 设置工具栏移动性2.6 往工具栏添加工具2.7 工具栏数量问题3. 状态栏3.1 状态栏的数量3.2 往状态栏添加部件4. 铆接部件（浮动窗口）4.1 添加浮动窗口5. 核心部件（中心部件）6.资源 *文件* 6.1 准备好外部的资](https://blog.csdn.net/qq_43403759/article/details/122022994)

博客[*QPr* *int* *Preview* *Dialog* *打印* *预览* 使用实例](https://blog.csdn.net/arv002/article/details/122235170)

6-6[使用方法: 创建 *QPr* *int* *Preview* *Dialog* 对象,并将待 *预览* 的 *打印* 机设备和 *打印* 设置传递给它。 添加需要 *打印* 的内容到 *预览* 窗口中,可以使用QPa *int* er在 *预览* 窗口上绘制 *打印* 内容。 显示 *预览* 对话框,让用户进行 *预览* 和调整 *打印* 设置。 用户可以在 *预览* 对话框中进行 *打印* 、 *导出* 为 *PDF* 等操作。](https://blog.csdn.net/arv002/article/details/122235170)

博客[【 *pyside* 6拓展】 *QPr* *int* *Preview* *Dialog* \_ *pyside* 6 *qpr* *int* *preview* *dialog*...](https://blog.csdn.net/m0_62599305/article/details/145509480)

5-15[4️⃣ 总结 ✨ *pyside* 6 拓展:*QPr* *int* *Preview* *Dialog* 类介绍 🖨️👀 1️⃣ *QPr* *int* *Preview* *Dialog* 类概述 🧐 *QPr* *int* *Preview* *Dialog* 是QtPr *int* Support模块中的一个类,用于提供 *打印* *预览* *功能* 。与 *QPr* *int* *Dialog* 主要用于直接启动 *打印* 任务不同,*QPr* *int* *Preview* *Dialog* 允许用户在实际 *打印* 之前查看文档的 *打印* 效果。这样,用户可以在 *打印* 前...](https://blog.csdn.net/m0_62599305/article/details/145509480)

评论

被折叠的 0 条评论 [为什么被折叠?](https://blogdev.blog.csdn.net/article/details/122245662)[到【灌水乐园】发言](https://bbs.csdn.net/forums/FreeZone)

添加红包

实付 元

[使用余额支付](https://blog.csdn.net/zhouyang/article/details/)

点击重新获取

扫码支付

钱包余额 0

抵扣说明：

1.余额是钱包充值的虚拟货币，按照1:1的比例进行支付金额的抵扣。  
2.余额无法直接购买下载，可以购买VIP、付费专栏及课程。

[余额充值](https://i.csdn.net/#/wallet/balance/recharge)

举报

[![](https://i-operation.csdnimg.cn/images/4e0dcc3d96eb497193f3eb9e3c0f60dc.gif)](https://mall.csdn.net/vip?utm_source=25618_vip_blogrighticon) [![](https://csdnimg.cn/release/blogv2/dist/pc/img/toolbar/Group.png) 点击体验  
DeepSeekR1满血版](https://ai.csdn.net/?utm_source=cknow_pc_blogdetail&spm=1001.2101.3001.10583) 隐藏侧栏 ![程序员都在用的中文IT技术交流社区](https://g.csdnimg.cn/side-toolbar/3.6/images/qr_app.png)

程序员都在用的中文IT技术交流社区

![专业的中文 IT 技术社区，与千万技术人共成长](https://g.csdnimg.cn/side-toolbar/3.6/images/qr_wechat.png)

专业的中文 IT 技术社区，与千万技术人共成长

![关注【CSDN】视频号，行业资讯、技术分享精彩不断，直播好礼送不停！](https://g.csdnimg.cn/side-toolbar/3.6/images/qr_video.png)

关注【CSDN】视频号，行业资讯、技术分享精彩不断，直播好礼送不停！

客服 返回顶部

![](https://i-blog.csdnimg.cn/blog_migrate/a05216039deaafa05f9266aedc6abbda.png)