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
            Action(FluentIcon.ADD, '新建', shortcut='Ctrl+N'),
            Action(FluentIcon.DOCUMENT, '打开',
                   shortcut='Ctrl+O',
                   triggered=self.comm.beforeOpenFile.emit
                   ),
            Action(FluentIcon.SAVE, '保存', shortcut='Ctrl+S'),
            Action(FluentIcon.SAVE_AS, '另存为', shortcut='Ctrl+Shift+S'),
            Action(FluentIcon.PRINT, '打印', shortcut='Ctrl+P'),
            Action(FluentIcon.CLOSE, '关闭', shortcut='Ctrl+W'),
        ])
        fileButton.setMenu(menu)
        self.addWidget(fileButton)

        editButton = TransparentDropDownPushButton(FluentIcon.EDIT, '编辑')
        editButton.setFixedHeight(34)
        setFont(editButton, 12)
        menu = RoundMenu(parent=self)
        menu.addActions([
            Action(FluentIcon.COPY, '复制'),
            Action(FluentIcon.CUT, '剪切'),
            Action(FluentIcon.PASTE, '粘贴'),
            Action(FluentIcon.CANCEL, '取消'),
            Action('全选'),
        ])
        editButton.setMenu(menu)
        self.addWidget(editButton)

        viewButton = TransparentDropDownPushButton(FluentIcon.VIEW, '视图')
        viewButton.setFixedHeight(34)
        setFont(viewButton, 12)
        menu = RoundMenu(parent=self)
        menu.addActions([
            Action(FluentIcon.ZOOM_IN, '放大'),
            Action(FluentIcon.ZOOM_OUT, '缩小'),
            Action(FluentIcon.FIT_PAGE, '适应窗口'),
        ])
        viewButton.setMenu(menu)
        self.addWidget(viewButton)

        runButton = TransparentDropDownPushButton(FluentIcon.COMMAND_PROMPT, '运行')
        runButton.setFixedHeight(34)
        setFont(runButton, 12)
        menu = RoundMenu(parent=self)
        menu.addActions([
            Action(FluentIcon.CODE, '编译',
                   triggered=self.comm.beforeCompile.emit
                   ),
            Action(FluentIcon.COMMAND_PROMPT, '运行',
                   triggered=self.comm.beforeRun.emit
                   ),
            Action(FluentIcon.ASTERISK, '编译并运行'),
        ])
        runButton.setMenu(menu)
        self.addWidget(runButton)

        self.addSeparator()

        self.addActions([
            Action(FluentIcon.HELP, '帮助', shortcut='Ctrl+H'),
            Action(FluentIcon.FEEDBACK, '关于我们', shortcut='Ctrl+F'),
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