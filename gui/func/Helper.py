from PyQt6.QtCore import  QUrl
from PyQt6.QtGui import QDesktopServices
from qfluentwidgets import  MessageBox


class Helper:
    def __init__(self, parent):
        self.parent = parent

    def showMessageBox(self):#显示开发者信息
        messageContent = (

            "代码结构✨：<br>"
            "<pre>"
            "- main.py           编译器程序入口\n"
            "- compiler\\tokenize.py       词法分析，将源代码转换为链表存储的Token\n"
            "- compiler\\parse.py:         语法分析，将Token转换为抽象语法树\n"
            "- compiler\\codegen.py        语义生成，将抽象语法树转换为汇编代码\n"
            "- compiler\\simulator.py      汇编代码解释器\n"
            "- gui\\fluent.py      图形化界面入口\n"
            "</pre>"
            
            
            "<br>如何运行此项目❓<br>"
            "<pre>"
            "- pip install python = 3.12.0 安装Python\n"
            "- pip install -r requirements.txt 安装依赖\n"
            "- python main.py 提供了编译器和解释器使用范例\n"
            "- python interface\\fluent.py 提供了Pybicc的图形化界面\n"
            "</pre>"
            
            "<br>输入样例参考👾：<br>"
            "<pre>"
            "- int main() { int a=3; int z=5; return a+z; }"
            "</pre>"
        )

        w = MessageBox(
            '帮助说明',
            messageContent,
            self.parent  # 确保MessageBox的parent参数是图形界面元素
        )
        w.yesButton.setText('阅读详细README')
        w.cancelButton.setText('关闭')

        if w.exec():
            QDesktopServices.openUrl(QUrl("https://github.com/TochusC/pybicc/blob/master/README.md"))