import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QGridLayout, QWidget, QLabel, QFileDialog
from PyQt6.QtGui import QIcon,QAction

class CustomLayoutWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.central_widget = QWidget()  # 创建一个中央小部件
        self.setCentralWidget(self.central_widget)
        self.grid_layout = QGridLayout(self.central_widget)  # 创建网格布局

        # 创建菜单
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&文件(F)')
        editMenu = menubar.addMenu('&编辑(E)')
        visionMenu = menubar.addMenu('&视图(V)')
        setMenu = menubar.addMenu('&设置(S)')
        runMenu = menubar.addMenu('&运行(R)')
        helpMenu = menubar.addMenu('&帮助(H)')

        openFile = QAction(QIcon('file.png'), 'Open', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.showDialog)
        fileMenu.addAction(openFile)

        # 创建 编译 动作
        compileAction = QAction('编译', self)
        compileAction.setShortcut('Ctrl+B')
        compileAction.setStatusTip('编译代码')
        #compileAction.triggered.connect(self.compileCode)  # 假设有一个名为compileCode的方法来处理编译

        # 创建 运行 动作
        runAction = QAction('运行', self)
        runAction.setShortcut('Ctrl+R')
        runAction.setStatusTip('运行代码')
       # runAction.triggered.connect(self.runCode)  # 假设有一个名为runCode的方法来处理运行代码

        # 创建 编译运行 动作
        compileRunAction = QAction('编译运行', self)
        compileRunAction.setShortcut('Ctrl+Shift+R')
        compileRunAction.setStatusTip('编译并运行代码')
        #compileRunAction.triggered.connect(self.compileAndRunCode)  # 假设有一个名为compileAndRunCode的方法同时处理编译和运行

        # 将动作添加到设置菜单
        runMenu.addAction(compileAction)
        runMenu.addAction(runAction)
        runMenu.addAction(compileRunAction)

        # 添加标签和文本编辑框
        self.left_label = QLabel('要编译的代码')
        self.left_text_edit = QTextEdit()
        self.right_label = QLabel('编译结果')
        self.right_text_edit = QTextEdit()
        self.execution_label = QLabel('运行结果')  # 运行结果标签
        self.execution_text_edit = QTextEdit()  # 运行结果文本框


        # 设置布局
        self.grid_layout.addWidget(self.left_label, 1, 0)
        self.grid_layout.addWidget(self.left_text_edit, 2, 0)
        self.grid_layout.addWidget(self.right_label, 1, 1)
        self.grid_layout.addWidget(self.right_text_edit, 2, 1)
        self.grid_layout.addWidget(self.execution_label, 3, 0)  # 运行结果标签位置
        self.grid_layout.addWidget(self.execution_text_edit, 4, 0, 1, 2)

        self.statusBar().showMessage('未运行')#可修改

        # 设置窗口
        self.setWindowIcon(QIcon('compiler.png'))
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('UPC Compiler')
        self.show()

    def showDialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')
        if fname[0]:
            f = open(fname[0], 'r')

            with f:
                data = f.read()
                self.textEdit.setText(data)

def main():
    app = QApplication(sys.argv)
    ex = CustomLayoutWindow()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
