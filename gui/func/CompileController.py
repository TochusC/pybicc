from qfluentwidgets import MessageBox

from compiler import interpreter, tokenize, codegen, parse, utils


class CompileController:
    def __init__(self, parent):
        self.parent = parent

    def compile(self, code):
        tokenize.token = tokenize.tokenize(code)

        utils.save_tokenize_result(tokenize.token)
        tokenize_result = utils.tokenize_result
        self.parent.comm.changeTokenizeResult.emit(tokenize_result)

        parse.prog = parse.program()
        utils.save_parse_result(parse.prog)
        parse_result = utils.parse_result
        self.parent.comm.changeParseResult.emit(parse_result)

        fn = parse.prog.fns
        while fn is not None:
            offset = 0
            vl = fn.locals
            while vl is not None:
                offset += vl.var.ty.size
                vl.var.offset = offset
                vl = vl.next
            fn.stack_size = utils.align_to(offset, 8)
            fn = fn.next
        return codegen.codegen(parse.prog)

    def run(self, assembly):
        interpreter.CompileController = self
        interpreter.run(assembly)
        return interpreter.output

    def request_input(self):
        userInput = self.parent.showInputMessageBox()
        try:
            if userInput.isdigit():
                returnValue = int(userInput)
            elif userInput[0:2] == '0x':
                returnValue = int(userInput, 16)
            elif '.' in userInput:
                returnValue = float(userInput)
            elif 'e' in userInput or 'E' in userInput:
                returnValue = float(userInput)
            elif 'f' in userInput:
                returnValue = float(userInput)
            elif 'd' in userInput:
                returnValue = float(userInput)
            elif userInput[0] == '0':
                returnValue = int(userInput, 8)
            elif userInput[0] == 'b':
                returnValue = int(userInput, 2)
            else:
                returnValue = int(userInput)
        except Exception as e:
            w = MessageBox(
                '输入错误！❌',
                f'输入错误：{str(e)}',
                self.parent
            )
            w.cancelButton.setText('关闭')
            if w.exec():
                pass
        return returnValue


if __name__ == '__main__':
    cc = CompileController(None)
    code = """
 
     int main() {
        int x=3;
        int y=5;
        return foo(&x, y);
    }
    """
    assembly = cc.compile(code)
    print(assembly)
    print(cc.run(assembly))
