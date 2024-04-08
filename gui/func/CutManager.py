from PyQt6.QtWidgets import QApplication
class CutManager:
    def __init__(self, parent):
        self.parent = parent

    def cut(self):
        self.parent.textEdit.cut()
        clipboard = QApplication.clipboard()
        cut_text = clipboard.text()
        self.afterCut.emit({'cutText': cut_text})
