class DataTraveler:
    def __init__(self, parent):
        self.unnamedFileCount = 0
        self.parent = parent
        self.currentFileContent = ''
        self.fileList = self.FileList([{'filename': 'unnamed.c', 'data': ''}])
        self.compileFileList = self.FileList([{'filename': 'unnamed.o', 'data': ''}])
        self.resultFileList = self.FileList([{'filename': 'unnamed', 'data': ''}])


    def loadNewFile(self, fileDict):
        self.fileList.addFile(fileDict['filename'], fileDict['data'])
        self.compileFileList.addFile(fileDict['filename'][:-2] + '.o', '')
        self.resultFileList.addFile(fileDict['filename'][:-2], '')

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

    def getResult(self):
        return self.resultFileList.getActiveFile()['data']

    def updateAssembly(self, assembly):
        self.compileFileList.changeActiveFileContent(assembly)
        self.parent.comm.afterActiveCompileFileChange.emit(self.resultFileList.getActiveFile()['data'])

    def updateResult(self, result):
        self.resultFileList.changeActiveFileContent(result)
        self.parent.comm.afterActiveResultFileChange.emit(self.resultFileList.getActiveFile()['data'])

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

        self.parent.comm.afterActiveFileChange.emit(self.getActiveFile()['data'])
        self.parent.comm.afterActiveCompileFileChange.emit(self.getAssembly())
        self.parent.comm.afterActiveResultFileChange.emit(self.resultFileList.getActiveFile()['data'])

    def createNewFile(self):
        self.unnamedFileCount += 1
        newFile = f'unnamed{self.unnamedFileCount}.c'

        self.fileList.addFile(f'unnamed{self.unnamedFileCount}.c', '')
        self.compileFileList.addFile(f'unnamed{self.unnamedFileCount}.o', '')
        self.resultFileList.addFile(f'unnamed{self.unnamedFileCount}', '')

        self.parent.comm.afterCreateNewFile.emit(newFile)

    def removeFile(self, filename):
        try:
            fileIndex = None

            for i in range(self.fileList.fileCount):
                if self.fileList.getFile(i)['filename'] == filename:
                    fileIndex = i
            self.fileList.removeFile(fileIndex)

            for i in range(self.compileFileList.fileCount):
                if self.compileFileList.getFile(i)['filename'] == filename[:-2] + '.o':
                    fileIndex = i
            self.compileFileList.removeFile(fileIndex)

            for i in range(self.resultFileList.fileCount):
                if self.resultFileList.getFile(i)['filename'] == filename[:-2]:
                    fileIndex = i
            self.resultFileList.removeFile(fileIndex)

            self.parent.comm.afterRemoveFile.emit(filename)

            if self.fileList.fileCount != 0:
                self.parent.comm.afterChangeActiveFile.emit(self.getActiveFile()['filename'])
                self.parent.comm.afterActiveFileChange.emit(self.getActiveFile()['data'])
                self.parent.comm.afterActiveCompileFileChange.emit(self.getAssembly())
                self.parent.comm.afterActiveResultFileChange.emit(self.resultFileList.getActiveFile()['data'])

        except Exception as e:
            print(e)

    class FileList:
        def __init__(self, file):
            self.fileCount = 1
            self.activeFile = 0
            self.file = file

        def addFile(self, filename, data, ):
            self.file.append({'filename': filename, 'data': data})
            self.fileCount += 1
            self.activeFile = self.fileCount - 1

        def removeFile(self, index):
            self.file.pop(index)
            self.fileCount -= 1
            self.activeFile = 0

        def getFile(self, index):
            return self.file[index]

        def getActiveFile(self):
            return self.file[self.activeFile]

        def changeActiveFile(self, index):
            self.activeFile = index

        def changeActiveFileContent(self, data):
            self.file[self.activeFile]['data'] = data
