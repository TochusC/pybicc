from PyQt6.QtWidgets import QFileDialog
import os


class FileManager:
    def __init__(self, parent):
        self.parent = parent

    def open(self):
        current_directory = os.getcwd()

        filename = QFileDialog.getOpenFileName(self.parent, 'Open file', current_directory)
        if filename[0]:
            with open(filename[0], 'r') as f:
                data = f.read()
                self.parent.comm.afterOpenFile.emit({'filename': filename[0], 'data': data})

    def save(self, filename, data):
        with open(filename, 'w') as f:
            f.write(data)