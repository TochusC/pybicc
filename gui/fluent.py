# coding:utf-8
import sys
import time
import ctypes

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Pybicc")

from PyQt6.QtCore import Qt, QUrl, QSize, QEventLoop, QTimer
from PyQt6.QtGui import QIcon, QDesktopServices, QAction
from PyQt6.QtWidgets import QApplication, QStackedWidget, QGridLayout, QMenu, QVBoxLayout, QFileDialog

from qfluentwidgets import (NavigationInterface, NavigationItemPosition, MessageBox,
                            isDarkTheme, qrouter, SplashScreen, setTheme, Theme, SubtitleLabel, LineEdit,
                            MessageBoxBase, StateToolTip, FlyoutView, PushButton, Flyout)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, StandardTitleBar

from gui.func.CompileController import CompileController
from gui.func.FileManager import FileManager
from gui.func.DataTraveler import DataTraveler
from gui.func.SignalManager import SignalManager
from gui.func.AboutUS import AboutUS
from gui.func.Helper import Helper
from gui.func.CutManager import CutManager
from gui.widget.MenuBar import MenuBar
from gui.widget.NaviInterface import TokenizeInterface, OverviewInterface, ParseInterface, Widget, \
    AvatarWidget, FileInterface


class Window(FramelessWindow):
    def __init__(self):
        super().__init__()
        titleBar = StandardTitleBar(self)
        titleBar.setIcon(self.windowIcon())
        titleBar.setTitle(self.windowTitle())
        self.setTitleBar(titleBar)

        # 初始化窗口
        self.initWindow()
        # 设置启动动画
        self.splashScreen = SplashScreen('resource/logo.png', self)
        self.splashScreen.setIconSize(QSize(164, 164))
        titleBar = StandardTitleBar(self.splashScreen)
        titleBar.setIcon(self.windowIcon())
        titleBar.setTitle(self.windowTitle())
        self.splashScreen.setTitleBar(titleBar)

        self.show()

        # 让动画至少播放1000ms
        loop = QEventLoop(self)
        QTimer.singleShot(600, loop.quit)
        loop.exec()

        # 初始化功能类
        self.cutManager = CutManager(self)
        self.fileManager = FileManager(self)
        self.signalManager = SignalManager(self)
        self.dataTraveler = DataTraveler(self)
        self.compileController = CompileController(self)
        self.aboutus = AboutUS(self)
        self.helper = Helper(self)
        self.comm = self.signalManager.comm

        self.initComm()

        self.navigationInterface = NavigationInterface(
            self, showMenuButton=True, showReturnButton=True)
        self.stackWidget = QStackedWidget(self)

        self.stateTooltip = None
        self.settingButton = None

        # 创建子界面
        self.tokenizeInterface = TokenizeInterface(self, self.comm)
        self.overviewInterface = OverviewInterface(self, self.comm)
        self.parseInterface = ParseInterface(self, self.comm)
        self.fileInterface = FileInterface(self, self.comm)

        # 显示启动画面
        self.menuBar = MenuBar(self, comm=self.comm)

        # 初始化布局
        self.gridLayout = QGridLayout(self)
        self.vBoxLayout = QVBoxLayout()
        # 初始化窗口
        self.initLayout()
        # 添加导航栏
        self.initNavigation()
        # 关闭启动画面
        self.splashScreen.finish()

    def initComm(self):
        try:
            self.comm.onThemeChange.connect(self.changeTheme)

            self.comm.beforeOpenFile.connect(self.fileManager.open)
            self.comm.onOpenFile[str].connect(self.openFile)
            self.comm.afterOpenFile[dict].connect(self.dataTraveler.loadNewFile)

            self.comm.beforeCut.connect(self.cutManager.cut)

            self.comm.onActiveFileChange[str].connect(self.dataTraveler.changeActiveFileContent)
            self.comm.onActiveCompileFileChange[str].connect(self.dataTraveler.changeActiveCompileFileContent)

            self.comm.beforeCompile.connect(
                lambda: self.comm.onCompile.emit(self.dataTraveler.getActiveFileContent()))

            self.comm.onCompile[str].connect(self.startCompile)

            self.comm.afterCompile[str].connect(self.dataTraveler.updateAssembly)

            self.comm.beforeRun.connect(
                lambda: self.comm.onRun.emit(self.dataTraveler.getAssembly()))
            self.comm.onRun[str].connect(self.startRun)
            self.comm.afterRun[str].connect(self.dataTraveler.updateResult)

            self.comm.clickhelper.connect(self.helper.showMessageBox)
            self.comm.clickaboutUS.connect(self.aboutus.showMessageBox)

            self.comm.beforeCreateNewFile.connect(self.dataTraveler.createNewFile)

            self.comm.beforeChangeActiveFile[str].connect(self.dataTraveler.changeActiveFile)

            self.comm.beforeRemoveFile[str].connect(self.dataTraveler.removeFile)

            self.comm.beforeCompileAndRun.connect(self.compileAndRun)

            self.comm.enlargeWindow.connect(self.enlargeWindow)
            self.comm.reduceWindow.connect(self.reduceWindow)
            self.comm.fitWindow.connect(self.resetWindow)

            self.comm.beforeSaveFile.connect(self.saveFile)

            self.comm.beforeClose.connect(self.close)
        except Exception as e:
            w = MessageBox(
                '发生错误！❌',
                f'未知错误：{e}',
                self
            )
            w.cancelButton.setText('关闭')
            if w.exec():
                pass



    def saveFile(self):
        try:
            filename, type = QFileDialog.getSaveFileName(self, '保存文件', '', 'C文件(*.c);;汇编文件(*.o);;运行结果(*.txt)')
            if type == 'C文件(*.c)':
                data = self.dataTraveler.getActiveFileContent()
            elif type == '汇编文件(*.o)':
                data = self.dataTraveler.getAssembly()
            elif type == '运行结果(*.txt)':
                data = self.dataTraveler.getResult()
            self.fileManager.save(filename, data)

        except Exception as e:
            w = MessageBox(
                '发生错误！❌',
                f'保存错误：{e}',
                self
            )
            w.cancelButton.setText('关闭')
            if w.exec():
                pass

    def compileAndRun(self):
        self.stateTooltip = StateToolTip('正在编译', "请耐心等待", self)
        self.stateTooltip.show()
        self.startCompile(self.dataTraveler.getActiveFileContent())
        time.sleep(0.5)
        self.startRun(self.dataTraveler.getAssembly())
        self.stateTooltip.close()

    def openFile(self, filename):
        self.fileManager.open_file(filename)
        w = MessageBox(
            '已打开.c代码文件✅！',
            filename,
            self
        )
        w.yesButton.setText('确定')
        w.cancelButton.setText('取消')
        if w.exec():
            pass

    def startRun(self, assembly):
        try:
            self.comm.afterRun.emit(self.compileController.run(assembly))
        except Exception as e:
            w = MessageBox(
                '发生错误！❌',
                f'运行错误：{e}',
                self
            )
            w.cancelButton.setText('关闭')
            if w.exec():
                pass

    class InputMessageBox(MessageBoxBase):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.titleLabel = SubtitleLabel('请求输入', self)
            self.inputEdit = LineEdit(self)

            self.inputEdit.setPlaceholderText('输入')
            self.inputEdit.setClearButtonEnabled(True)

            # add widget to view layout
            self.viewLayout.addWidget(self.titleLabel)
            self.viewLayout.addWidget(self.inputEdit)

            # change the text of button
            self.yesButton.setText('确定')

            self.widget.setMinimumWidth(350)

    def showInputMessageBox(self):
        w = self.InputMessageBox(self)
        if w.exec():
            return w.inputEdit.text()

    def startCompile(self, code):
        try:
            self.comm.afterCompile.emit(self.compileController.compile(code))
        except Exception as e:
            w = MessageBox(
                '发生错误！❌',
                f'编译错误：{e}',
                self
            )
            w.cancelButton.setText('关闭')
            if w.exec():
                pass

    def startRun(self, assembly):
        try:
            self.comm.afterRun.emit(self.compileController.run(assembly))
        except Exception as e:
            w = MessageBox(
                '发生错误！❌',
                f'运行错误：{e}',
                self
            )
            w.cancelButton.setText('关闭')
            if w.exec():
                pass

    def initLayout(self):  #初始化窗口
        self.gridLayout.setSpacing(0)
        self.gridLayout.addWidget(self.navigationInterface, 0, 0, 2, 1)
        self.vBoxLayout.setContentsMargins(0, 32, 0, 0)
        self.vBoxLayout.addWidget(self.menuBar)
        self.vBoxLayout.addWidget(self.stackWidget)
        self.gridLayout.addLayout(self.vBoxLayout, 0, 1, 2, 1)

        self.titleBar.raise_()
        self.navigationInterface.displayModeChanged.connect(self.titleBar.raise_)

    def initNavigation(self):  #导航栏
        # enable acrylic effect
        self.navigationInterface.setAcrylicEnabled(True)

        self.addSubInterface(self.overviewInterface, FIF.LAYOUT, '总览视图')
        self.addSubInterface(self.tokenizeInterface, FIF.LANGUAGE, '词法分析')
        self.addSubInterface(self.parseInterface, FIF.CODE, '语法分析')

        self.navigationInterface.addSeparator()

        self.addSubInterface(self.fileInterface, FIF.FOLDER, '文件管理', )

        # add custom widget to bottom
        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=AvatarWidget(),
            onClick=self.showMessageBox,
            position=NavigationItemPosition.BOTTOM
        )

        self.settingButton = self.navigationInterface.addItem(
            routeKey="setting",  #设置
            icon=FIF.SETTING,
            text="设置",
            onClick=self.showSetting,
            position=NavigationItemPosition.BOTTOM,
            tooltip="设置"
        )


        # !IMPORTANT: don't forget to set the default route key
        qrouter.setDefaultRouteKey(self.stackWidget, self.overviewInterface.objectName())

        # set the maximum width
        self.navigationInterface.setExpandWidth(300)

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.navigationInterface.setCurrentItem(self.overviewInterface.objectName())
        self.stackWidget.setCurrentIndex(0)

    def showSetting(self):
        try:
            view = FlyoutView(
                title='Pybicc',
                content="好像没什么可以设置的...",
                image='resource/logo.png',
                isClosable=True
            )

            # add button to view
            button = PushButton('好的')
            button.clicked.connect(view.close)
            button.setFixedWidth(120)
            view.addWidget(button)

            # adjust layout (optional)
            view.widgetLayout.insertSpacing(1, 5)
            view.widgetLayout.addSpacing(5)

            # show view
            w = Flyout.make(view, self.settingButton, self)
            view.closed.connect(w.close)
        except Exception as e:
            print(e)


    def changeTheme(self, isDark: bool):  #转换颜色模式
        setTheme(Theme.DARK if isDark else Theme.LIGHT)
        self.setQss()

    def initWindow(self):  #初始化窗口
        self.resize(900, 700)
        self.setWindowIcon(QIcon('resource/logo.png'))
        self.setWindowTitle('Pybicc')
        self.titleBar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        self.setQss()

    def enlargeWindow(self):
        current_size = self.size()  # 获取当前窗口大小
        new_width = current_size.width() * 1.1  # 增大宽度
        new_height = current_size.height() * 1.1  # 增大高度
        self.resize(int(new_width), int(new_height))  # 设置新的窗口大小

    def reduceWindow(self):
        current_size = self.size()
        new_width = current_size.width() * 0.9
        new_height = current_size.height() * 0.9
        self.resize(int(new_width), int(new_height))  # 设置新的窗口大小

    def resetWindow(self):
        self.resize(900, 700)

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP):
        """ add sub interface """
        self.stackWidget.addWidget(interface)
        self.navigationInterface.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            position=position,
            tooltip=text
        )

    def setQss(self):  #具体转换颜色
        color = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/{color}/demo.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())
        qrouter.push(self.stackWidget, widget.objectName())

    def showMessageBox(self):  #显示开发者信息
        w = MessageBox(
            'Pybicc💯 v0.2.1',
            'Made With 💖 by UPC-编译原理课设-二组\n\nPowered by PyQt6, PyQt-Fluent-Widgets\n',
            self
        )
        w.yesButton.setText('前往GitHub仓库')
        w.cancelButton.setText('关闭')

        if w.exec():
            QDesktopServices.openUrl(QUrl("https://github.com/TochusC/pybicc"))

    def resizeEvent(self, e):
        self.titleBar.move(46, 0)
        self.titleBar.resize(self.width() - 46, self.titleBar.height())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec()
