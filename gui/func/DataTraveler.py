class DataTraveler:
    def __init__(self, parent):
        self.unnamedFileCount = 0
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

    def changeActiveFile(self, filename):
        codeFileName = filename[:-2] + '.c'
        compileFileName = filename[:-2] + '.o'
        resultFileName = filename[:-2]

        for i in range(self.fileList.fileCount):
            if self.fileList.getFile(i)['filename'] == codeFileName:
                self.fileList.changeActiveFile(i)
        for i in range(self.compileFileList.fileCount):
            if self.compileFileList.getFile(i)['filename'] == compileFileName:
                self.compileFileList.changeActiveFile(i)
        for i in range(self.resultFileList.fileCount):
            if self.resultFileList.getFile(i)['filename'] == resultFileName:
                self.resultFileList.changeActiveFile(i)

        self.parent.comm.afterChangeActiveFile.emit(filename)


    def createNewFile(self):
        self.unnamedFileCount += 1
        newFile = f'unnamed{self.unnamedFileCount}.c'
        self.fileList.addFile(f'unnamed{self.unnamedFileCount}.c', '')
        self.parent.comm.afterCreateNewFile.emit(newFile)

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
