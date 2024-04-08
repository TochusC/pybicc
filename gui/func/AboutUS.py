from PyQt6.QtCore import  QUrl
from PyQt6.QtGui import QDesktopServices
from qfluentwidgets import  MessageBox


class AboutUS:
    def __init__(self, parent):
        self.parent = parent

    def showMessageBox(self):#显示开发者信息
        messageContent = (
            "Pybicc v0.2.1\n"
            "开发团队：UPC-编译原理课设-二组\n\n"
            "我们的团队致力于提供高质量的软件解决方案。Pybicc是我们的努力成果之一，旨在提供编译器功能。\n\n"
            "使用的主要前端框架有：\n"
            "- PyQt6\n"
            "- PyQt-Fluent-Widgets\n\n"
            "版权 © 2024 UPC-编译原理课设-二组。保留所有权利。\n\n"
            "联系我们：队长QQ：205329624\n"
            "遵循我们的GitHub：https://github.com/TochusC/pybicc\n\n"
            "特别感谢所有对Pybicc作出贡献的人，以及使用以下开源项目。\n"
            "我们承诺保护用户隐私，详情请见我们的隐私政策。\n"
            "感谢您选择Pybicc作为您的解决方案，期待您的反馈和支持！"
        )

        w = MessageBox(
            '关于 Pybicc',
            messageContent,
            self.parent  # 确保MessageBox的parent参数是图形界面元素
        )
        w.yesButton.setText('前往GitHub仓库')
        w.cancelButton.setText('关闭')

        if w.exec():
            QDesktopServices.openUrl(QUrl("https://github.com/TochusC/pybicc"))