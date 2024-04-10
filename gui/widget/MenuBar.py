from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from qfluentwidgets import CommandBar, FluentIcon, Action, RoundMenu, TransparentDropDownPushButton, setFont, \
    SwitchButton

from gui.func.FileManager import FileManager


class MenuBar(CommandBar):
    def __init__(self, parent=None, comm=None):
        super().__init__(parent)
        self.comm = comm
        fileButton = TransparentDropDownPushButton(FluentIcon.FOLDER, '文件')
        fileButton.setFixedHeight(34)
        setFont(fileButton, 12)
        menu = RoundMenu(parent=self)
        menu.addActions([
            Action(FluentIcon.ADD, '新建', shortcut='Ctrl+N'
                   , triggered=self.comm.beforeCreateNewFile.emit
                   ),
            Action(FluentIcon.DOCUMENT, '打开',
                   shortcut='Ctrl+O',
                   triggered=self.comm.beforeOpenFile.emit
                   ),
            Action(FluentIcon.SAVE, '保存',
                   shortcut='Ctrl+S',
                   triggered=self.comm.beforeSaveFile.emit,
                   ),
            Action(FluentIcon.CLOSE, '关闭', shortcut='Ctrl+W', triggered=self.comm.beforeClose.emit),
        ])
        fileButton.setMenu(menu)
        self.addWidget(fileButton)


        viewButton = TransparentDropDownPushButton(FluentIcon.VIEW, '视图')
        viewButton.setFixedHeight(34)
        setFont(viewButton, 12)
        menu = RoundMenu(parent=self)
        menu.addActions([
            Action(FluentIcon.ZOOM_IN, '放大', shortcut='Ctrl+Plus', triggered=self.comm.enlargeWindow.emit),
            Action(FluentIcon.ZOOM_OUT, '缩小', shortcut='Ctrl+Minus', triggered=self.comm.reduceWindow.emit),
            Action(FluentIcon.FIT_PAGE, '适应窗口', shortcut='Ctrl+0', triggered=self.comm.fitWindow.emit),
        ])
        viewButton.setMenu(menu)
        self.addWidget(viewButton)

        runButton = TransparentDropDownPushButton(FluentIcon.COMMAND_PROMPT, '运行')
        runButton.setFixedHeight(34)
        setFont(runButton, 12)
        menu = RoundMenu(parent=self)
        menu.addActions([
            Action(FluentIcon.CODE, '编译', shortcut='F6',
                   triggered=self.comm.beforeCompile.emit
                   ),
            Action(FluentIcon.COMMAND_PROMPT, '运行', shortcut='F7',
                   triggered=self.comm.beforeRun.emit
                   ),
            Action(FluentIcon.ASTERISK, '编译并运行', shortcut='F5',
                   triggered=self.comm.beforeCompileAndRun.emit
                   ),
        ])
        runButton.setMenu(menu)
        self.addWidget(runButton)

        self.addSeparator()

        self.addActions([
            Action(FluentIcon.HELP, '帮助', shortcut='Ctrl+H', triggered=self.comm.clickhelper.emit),
        ])
        self.addActions([
            Action(FluentIcon.FEEDBACK, '关于我们', shortcut='Ctrl+F', triggered=self.comm.clickaboutUS.emit),
        ])

        self.addSeparator()

        self.switchButton = SwitchButton(self)
        self.switchButton.move(48, 24)
        self.switchButton.checkedChanged.connect(self.onCheckChanged)
        self.switchButton.setText('浅色')
        self.addWidget(self.switchButton)

        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

    def onCheckChanged(self, isChecked):
        text = '深色' if isChecked else '浅色'
        self.switchButton.setText(text)
        self.comm.onThemeChange.emit(isChecked)
