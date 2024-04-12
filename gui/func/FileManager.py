from PyQt6.QtWidgets import QFileDialog
import os

from qfluentwidgets import MessageBox


class FileManager:
    def __init__(self, parent):
        self.parent = parent

    def open(self):
        current_directory = os.getcwd()

        try:
            filter = "c语言代码文件 (*.c)"
            filename = QFileDialog.getOpenFileName(self.parent, 'Open file', current_directory, filter=filter)
            if filename[0].endswith('.c'):
                if filename[0]:
                    with open(filename[0], 'r') as f:
                        data = f.read()
                        self.parent.comm.afterOpenFile.emit({'filename': filename[0], 'data': data})
            else:
                w = MessageBox(
                    '发生错误！❌',
                    f'打开文件错误：文件格式不支持！',
                    self.parent
                )
                w.cancelButton.setText('关闭')
                if w.exec():
                    pass

        except Exception as e:
            w = MessageBox(
                '发生错误！❌',
                f'打开文件错误：{str(e)}',
                self.parent
            )
            w.cancelButton.setText('关闭')
            if w.exec():
                pass

    def open_file(self, filename):
        with open(filename, 'r') as f:
            data = f.read()
            self.parent.comm.afterOpenFile.emit({'filename': filename, 'data': data})

    def save(self, filename, data):
        with open(filename, 'w') as f:
            f.write(data)