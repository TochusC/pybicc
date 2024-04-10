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
        return self.parent.showInputMessageBox()


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
