from compiler import interpreter, tokenize, codegen, parse
from compiler.utils import align_to




class CompileController:
    def __init__(self, parent):
        self.parent = parent


    def compile(self, code):
        tokenize.token = tokenize.tokenize(code)
        parse.prog = parse.program()
        fn = parse.prog.fns
        while fn is not None:
            offset = 0
            vl = fn.locals
            while vl is not None:
                offset += vl.var.ty.size
                vl.var.offset = offset
                vl = vl.next
            fn.stack_size = align_to(offset, 8)
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
