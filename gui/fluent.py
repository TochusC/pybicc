# coding:utf-8
import sys
from PyQt6.QtCore import Qt, QUrl, QSize, QEventLoop, QTimer
from PyQt6.QtGui import QIcon, QDesktopServices, QAction
from PyQt6.QtWidgets import QApplication, QStackedWidget, QGridLayout, QMenu, QVBoxLayout, QFileDialog

from qfluentwidgets import (NavigationInterface, NavigationItemPosition, MessageBox,
                            isDarkTheme, qrouter, SplashScreen, setTheme, Theme, SubtitleLabel, LineEdit,
                            MessageBoxBase)
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
from gui.widget.NaviInterface import CompileInterface, OverviewInterface, RunInterface, Widget, \
    AvatarWidget


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

        # 创建子界面
        self.compileInterface = CompileInterface(self, self.comm)
        self.overviewInterface = OverviewInterface(self, self.comm)
        self.runInterface = RunInterface(self, self.comm)

        self.folderInterface = Widget('Folder Interface', self)
        self.settingInterface = Widget('Setting Interface', self)

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
        self.comm.onThemeChange.connect(self.changeTheme)

        self.comm.beforeOpenFile.connect(self.fileManager.open)
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

        self.comm.clickhelper.connect(self.helper.showMessageBox)
        self.comm.clickaboutUS.connect(self.aboutus.showMessageBox)

        self.comm.beforeCreateNewFile.connect(self.dataTraveler.createNewFile)

        self.comm.beforeChangeActiveFile.connect(self.dataTraveler.changeActiveFile)

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

        self.addSubInterface(self.compileInterface, FIF.CODE, '编译')
        self.addSubInterface(self.overviewInterface, FIF.LAYOUT, '总览')
        self.addSubInterface(self.runInterface, FIF.COMMAND_PROMPT, '运行')

        self.navigationInterface.addSeparator()

        self.addSubInterface(self.folderInterface, FIF.FOLDER, 'Folder library', NavigationItemPosition.SCROLL)
        # for i in range(1, 21):
        #     self.navigationInterface.addItem(
        #         f'folder{i}',
        #         FIF.FOLDER,
        #         f'Folder {i}',
        #         lambda: print('Folder clicked'),
        #         position=NavigationItemPosition.SCROLL
        #     )

        # add custom widget to bottom
        self.navigationInterface.addWidget(
            routeKey='avatar',
            widget=AvatarWidget(),
            onClick=self.showMessageBox,
            position=NavigationItemPosition.BOTTOM
        )

        self.addSubInterface(self.settingInterface, FIF.SETTING, 'Settings', NavigationItemPosition.BOTTOM)

        # !IMPORTANT: don't forget to set the default route key
        qrouter.setDefaultRouteKey(self.stackWidget, self.overviewInterface.objectName())

        # set the maximum width
        self.navigationInterface.setExpandWidth(300)

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.stackWidget.setCurrentIndex(1)

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
