class DataTraveler:
    def __init__(self, parent):
        self.assembly = ''
        self.parent = parent
        self.currentFileContent = ''
        self.fileList = self.FileList()

    def loadNewFile(self, fileDict):
        self.fileList.addFile(fileDict['filename'], fileDict['data'])
        self.parent.comm.afterActiveFileChange.emit(self.getActiveFile()['data'])

    def getActiveFile(self):
        return self.fileList.getActiveFile()

    def changeActiveFileContent(self, data):
        if self.getActiveFileContent() == data:
            return
        self.fileList.changeActiveFileContent(data)
        self.parent.comm.afterActiveFileChange.emit(self.getActiveFile()['data'])

    def getActiveFileContent(self):
        return self.getActiveFile()['data']

    def getAssembly(self):
        return self.assembly

    def updateAssembly(self, assembly):
        self.assembly = assembly

    class FileList:
        def __init__(self):
            self.fileCount = 1
            self.activeFile = 0
            self.file = [
                {
                    'filename': 'unnamed.c',
                    'data': ''
                }
            ]

        def addFile(self, filename, data):
            self.file.append({'filename': filename, 'data': data})
            self.fileCount += 1
            self.activeFile = self.fileCount - 1

        def getFile(self, index):
            return self.file[index]

        def getActiveFile(self):
            return self.file[self.activeFile]

        def changeActiveFile(self, index):
            self.activeFile = index

        def changeActiveFileContent(self, data):
            self.file[self.activeFile]['data'] = data
