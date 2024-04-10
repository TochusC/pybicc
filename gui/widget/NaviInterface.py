import sys
from PyQt6.QtCore import Qt, QRect, QUrl
from PyQt6.QtGui import QIcon, QPainter, QImage, QBrush, QColor, QFont, QDesktopServices
from PyQt6.QtWidgets import QApplication, QFrame, QStackedWidget, QHBoxLayout, QLabel, QVBoxLayout, \
    QGridLayout

from qfluentwidgets import (NavigationInterface, NavigationItemPosition, NavigationWidget, MessageBox,
                            isDarkTheme, setTheme, Theme, qrouter, TextEdit, SubtitleLabel, TabBar, FluentIcon,
                            CaptionLabel, IconWidget)
from qfluentwidgets import FluentIcon as FIF

from qframelesswindow import FramelessWindow, TitleBar

from gui.func.CodeHighlighter import CHighlighter, AssemblyHighlighter


class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(' ', '-'))
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignmentFlag.AlignCenter)

        # leave some space for title bar
        self.hBoxLayout.setContentsMargins(0, 32, 0, 0)


class AvatarWidget(NavigationWidget):
    """ Avatar widget """

    def __init__(self, parent=None):
        super().__init__(isSelectable=False, parent=parent)
        self.avatar = QImage('resource/logo.png').scaled(
            24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.RenderHint.SmoothPixmapTransform | QPainter.RenderHint.Antialiasing)

        painter.setPen(Qt.PenStyle.NoPen)

        if self.isPressed:
            painter.setOpacity(0.7)

        # draw background
        if self.isEnter:
            c = 255 if isDarkTheme() else 0
            painter.setBrush(QColor(c, c, c, 10))
            painter.drawRoundedRect(self.rect(), 5, 5)

        # draw avatar
        painter.setBrush(QBrush(self.avatar))
        painter.translate(8, 6)
        painter.drawEllipse(0, 0, 24, 24)
        painter.translate(-8, -6)

        if not self.isCompacted:
            painter.setPen(Qt.GlobalColor.white if isDarkTheme() else Qt.GlobalColor.black)
            font = QFont('Segoe UI')
            font.setPixelSize(14)
            painter.setFont(font)
            painter.drawText(QRect(44, 0, 255, 36), Qt.AlignmentFlag.AlignVCenter, 'Pybicc')


class CodeEditor(QFrame):
    """ Code editor """

    def __init__(self, parent=None, comm=None):
        super().__init__(parent)
        self.comm = comm
        self.setObjectName('CodeEditor')
        self.tabBar = TabBar()
        self.tabBar.setMovable(True)
        self.tabBar.setScrollable(True)
        self.tabBar.addTab('unnamed.c', 'unnamed.c', FluentIcon.DOCUMENT)
        self.tabBar.currentChanged.connect(self.onTabChanged)
        self.tabBar.tabAddRequested.connect(self.onTabAddRequested)
        self.tabBar.tabCloseRequested.connect(self.removeTab)

        self.text_edit = TextEdit(self)
        self.highlighter = CHighlighter(self.text_edit.document())
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(self.tabBar)
        self.vBoxLayout.addWidget(self.text_edit)

        self.text_edit.textChanged.connect(lambda: self.comm.onActiveFileChange.emit(self.text_edit.toPlainText()))
        self.comm.afterActiveFileChange[str].connect(self.changeToActiveFile)

        self.comm.afterCreateNewFile[str].connect(self.addTab)

        self.comm.afterChangeActiveFile.connect(self.changeTabToActiveFile)

        self.comm.afterOpenFile.connect(self.addNewFile)

    def addNewFile(self, file_dict):
        filename = file_dict['filename']
        self.tabBar.addTab(filename, filename, FluentIcon.DOCUMENT)
        self.tabBar.setCurrentTab(filename)

    def removeTab(self, index):
        filename = self.tabBar.tabText(index)
        self.tabBar.removeTab(index)
        self.comm.beforeRemoveFile.emit(filename)


    def changeTabToActiveFile(self, text):
        filename = text[:-2] + '.c'
        self.tabBar.setCurrentTab(filename)


    def addTab(self, text):
        self.tabBar.addTab(text, text, FluentIcon.DOCUMENT)

    def changeToActiveFile(self, text):
        if self.text_edit.toPlainText() != text:
            self.text_edit.setText(text)

    def onTabChanged(self, index: int):
        objectName = self.tabBar.currentTab().routeKey()
        self.comm.beforeChangeActiveFile.emit(objectName)

    def onTabAddRequested(self):
        self.comm.beforeCreateNewFile.emit()


class CompileResult(QFrame):
    """ Compile result """

    def __init__(self, parent=None, comm=None):
        super().__init__(parent)
        self.comm = comm
        self.setObjectName('CompileResult')
        self.tabBar = TabBar()
        self.tabBar.addTab('unnamed.o', 'unnamed.o', FluentIcon.DOCUMENT)
        self.tabBar.currentChanged.connect(self.onTabChanged)

        self.tabBar.setMovable(True)
        self.tabBar.setScrollable(True)

        self.text_edit = TextEdit(self)
        self.highlighter = AssemblyHighlighter(self.text_edit.document())
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(self.tabBar)
        self.vBoxLayout.addWidget(self.text_edit)

        self.comm.afterCompile[str].connect(self.text_edit.setText)

        self.text_edit.textChanged.connect(
            lambda: self.comm.onActiveCompileFileChange.emit(self.text_edit.toPlainText()))
        self.comm.afterActiveCompileFileChange[str].connect(self.changeToActiveFile)
        self.comm.afterCreateNewFile[str].connect(self.addTab)

        self.comm.afterChangeActiveFile.connect(self.changeTabToActiveFile)

        self.comm.afterOpenFile.connect(self.addNewFile)
        self.comm.afterRemoveFile.connect(self.removeFile)

    def removeFile(self, filename):
        filename = filename[:-2] + '.o'
        self.tabBar.removeTabByKey(filename)

    def addNewFile(self, file_dict):
        filename = file_dict['filename'][0:-2] + '.o'
        self.tabBar.addTab(filename, filename, FluentIcon.DOCUMENT)
        self.tabBar.setCurrentTab(filename)

    def changeTabToActiveFile(self, text):
        filename = text[:-2] + '.o'
        self.tabBar.setCurrentTab(filename)

    def changeToActiveFile(self, text):
        if self.text_edit.toPlainText() != text:
            self.text_edit.setText(text)

    def addTab(self, text):
        text = text[:-2] + '.o'
        self.tabBar.addTab(text, text, FluentIcon.DOCUMENT)

    def onTabChanged(self, index: int):
        objectName = self.tabBar.currentTab().routeKey()


class RunResult(QFrame):
    """ Run result """

    def __init__(self, parent=None, comm=None):
        super().__init__(parent)
        self.comm = comm
        self.setObjectName('RunResult')
        self.tabBar = TabBar()
        self.tabBar.addTab('unnamed', 'unnamed', FluentIcon.DOCUMENT)
        self.tabBar.currentChanged.connect(self.onTabChanged)

        self.tabBar.setMovable(True)
        self.tabBar.setScrollable(True)

        self.text_edit = TextEdit(self)
        self.text_edit.setReadOnly(True)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(self.tabBar)
        self.vBoxLayout.addWidget(self.text_edit)
        self.comm.afterRun[str].connect(self.text_edit.setText)

        self.comm.afterCreateNewFile[str].connect(self.addTab)

        self.comm.afterChangeActiveFile.connect(self.changeTabToActiveFile)
        self.comm.afterActiveResultFileChange[str].connect(self.changeToActiveFile)

        self.comm.afterOpenFile.connect(self.addNewFile)
        self.comm.afterRemoveFile.connect(self.removeFile)

    def addNewFile(self, file_dict):
        filename = file_dict['filename'][0:-2]
        self.tabBar.addTab(filename, filename, FluentIcon.DOCUMENT)
        self.tabBar.setCurrentTab(filename)

    def removeFile(self, filename):
        filename = filename[:-2]
        self.tabBar.removeTabByKey(filename)


    def changeTabToActiveFile(self, text):
        filename = text[:-2]
        self.tabBar.setCurrentTab(filename)

    def addTab(self, text):
        text = text[:-2]
        self.tabBar.addTab(text, text, FluentIcon.DOCUMENT)

    def changeToActiveFile(self, text):
        if self.text_edit.toPlainText() != text:
            self.text_edit.setText(text)

    def onTabChanged(self, index: int):
        objectName = self.tabBar.currentTab().routeKey()


class Interface(QFrame):
    def __init__(self, parent, name):
        super().__init__(parent)

        self.setObjectName(name)


class CompileInterface(Interface):
    """ Compile interface """

    def __init__(self, parent=None, comm=None):
        super().__init__(parent, 'CompileInterface')
        self.comm = comm
        self.codeEditor = CodeEditor(self, comm)
        self.compileResult = CompileResult(self, comm)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(self.codeEditor)
        self.vBoxLayout.setStretch(0, 3)
        self.vBoxLayout.addWidget(self.compileResult)
        self.vBoxLayout.setStretch(1, 2)


class OverviewInterface(Interface):
    """ Overview interface """

    def __init__(self, parent=None, comm=None):
        super().__init__(parent, 'OverviewInterface')
        self.comm = comm
        self.grid_layout = QGridLayout(self)
        self.codeEditor = CodeEditor(self, comm)
        self.compileResult = CompileResult(self, comm)
        self.runResult = RunResult(self, comm)
        self.grid_layout.addWidget(self.codeEditor, 0, 0)
        self.grid_layout.addWidget(self.compileResult, 0, 1)
        self.grid_layout.setRowStretch(0, 3)
        self.grid_layout.setRowStretch(1, 2)
        self.grid_layout.addWidget(self.runResult, 1, 0, 1, 2)


class RunInterface(Interface):
    """ Run interface """

    def __init__(self, parent=None, comm=None):
        super().__init__(parent, 'RunInterface')
        self.comm = comm
        self.codeEditor = CodeEditor(self, comm)
        self.runResult = RunResult(self, comm)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(self.codeEditor)
        self.vBoxLayout.addWidget(self.runResult)
        self.vBoxLayout.setStretch(0, 3)
        self.vBoxLayout.setStretch(1, 2)
