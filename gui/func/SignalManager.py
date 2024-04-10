from PyQt6.QtCore import pyqtSignal, QObject


class SignalManager:
    def __init__(self, parent):
        self.parent = parent
        self.comm = Communicate()


class Communicate(QObject):
    beforeOpenFile = pyqtSignal()
    afterOpenFile = pyqtSignal(dict)

    onActiveFileChange = pyqtSignal(str)
    afterActiveFileChange = pyqtSignal(str)

    onActiveCompileFileChange = pyqtSignal(str)
    afterActiveCompileFileChange = pyqtSignal(str)

    onActiveResultFileChange = pyqtSignal(str)
    afterActiveResultFileChange = pyqtSignal(str)

    beforeCompile = pyqtSignal()
    onCompile = pyqtSignal(str)
    afterCompile = pyqtSignal(str)

    beforeRun = pyqtSignal()
    onRun = pyqtSignal(str)
    afterRun = pyqtSignal(str)

    onThemeChange = pyqtSignal(bool)
    clickaboutUS = pyqtSignal()
    clickhelper = pyqtSignal()
    afterCut = pyqtSignal(dict)
    beforeCut = pyqtSignal()

    requestInput = pyqtSignal()

    beforeCreateNewFile = pyqtSignal()
    afterCreateNewFile = pyqtSignal(str)

    beforeChangeActiveFile = pyqtSignal(str)
    afterChangeActiveFile = pyqtSignal(str)

    beforeRemoveFile = pyqtSignal(str)
    afterRemoveFile = pyqtSignal(str)
