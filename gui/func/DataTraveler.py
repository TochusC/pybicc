class DataTraveler:
    def __init__(self, parent):
        self.parent = parent
        self.currentFileContent = ''
        self.fileList = self.FileList()
        self.compileFileList = self.CompileFileList()
        self.resultFileList = self.ResultFileList()

    def loadNewFile(self, fileDict):
        self.fileList.addFile(fileDict['filename'], fileDict['data'])
        self.parent.comm.afterActiveFileChange.emit(self.getActiveFile()['data'])

    def changeActiveFileContent(self, data):
        if self.getActiveFileContent() == data:
            return
        self.fileList.changeActiveFileContent(data)
        self.parent.comm.afterActiveFileChange.emit(self.getActiveFile()['data'])

    def changeActiveCompileFileContent(self, data):
        if self.getAssembly() == data:
            return
        self.compileFileList.changeActiveFileContent(data)
        self.parent.comm.afterActiveCompileFileChange.emit(self.getAssembly())

    def getActiveFile(self):
        return self.fileList.getActiveFile()

    def getActiveFileContent(self):
        return self.getActiveFile()['data']

    def getAssembly(self):
        return self.compileFileList.getActiveFile()['data']

    def updateAssembly(self, assembly):
        self.compileFileList.changeActiveFileContent(assembly)
        self.parent.comm.afterActiveCompileFileChange.emit(self.resultFileList.getActiveFile()['data'])

    class CompileFileList:
        def __init__(self):
            self.fileCount = 1
            self.activeFile = 0
            self.file = [
                {
                    'filename': 'unnamed.o',
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

    class ResultFileList:
        def __init__(self):
            self.fileCount = 1
            self.activeFile = 0
            self.file = [
                {
                    'filename': 'unnamed',
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
