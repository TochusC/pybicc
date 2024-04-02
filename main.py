"""
    # pybicc v0.2.4u - 一个简单的类C语言编译器 + 汇编代码解释器
    ---
        未完成版本，缺少解释器实现。
        图形化界面取得了突破性进展🥰
        支持的变量类型：int, char, int* , char*, int[] , char[]
        支持字面值常量。
        支持运算符：+ - * / % == != < <= > >= && || ! = & ^
        支持指针、函数定义和函数调用。
        支持IF-ELSE, FOR, WHILE语句

    ## 代码结构：
    ---
        - main.py           编译器程序入口
        - compiler\tokenize.py       词法分析，将源代码转换为链表存储的Token
        - compiler\parse.py:         语法分析，将Token转换为抽象语法树
        - compiler\codegen.py        语义生成，将抽象语法树转换为汇编代码
        - compiler\simulator.py      汇编代码解释器
        - gui\fluent.py      图形化界面入口

    ## 输入样例：
    ---

     int foo(int *x, int y)
    {
        return *x + y;
    }
     int main() {
        int x=3;
        int y=5;
        return foo(&x, y);
    }

"""

from compiler import tokenize, parse, codegen, interpreter, utils

codeToCompile = """
int x;
int main(){
x = 3;
return x;
}
"""

DEBUG = True

if __name__ == '__main__':
    print("======需要编译的代码=======")
    print(codeToCompile)
    print("======词法分析开始======")
    # 词法分析
    tokenize.token = tokenize.tokenize(codeToCompile)

    if DEBUG:
        # 输出token，用于调试
        print("======词法分析结果======")
        token = tokenize.token
        while token.next is not None:
            print(token.kind, token.str)
            token = token.next

    print("======语法分析开始======")
    parse.prog = parse.program()

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
    offset = 0

    if DEBUG:
        # 输出node，用于调试
        print("======语法分析结果======")

        glbs = parse.prog.globals
        print("===全局变量===")
        while glbs is not None:
            print("变量名:", glbs.var.name, "大小:", glbs.var.ty.size, "offset:", glbs.var.offset)
            glbs = glbs.next
        print("===变量结束===")

        fn = parse.prog.fns
        while fn is not None:
            print("=====函数名:", fn.name, "=====", sep="")
            print("===函数参数===")
            params = fn.params

            print("===局部变量===")
            locals = fn.locals

            print("===函数语句===")
            node = fn.node
            while node is not None:
                utils.print_node(node)
                node = node.next
            print("=====函数结束======")
            fn = fn.next

    # 编译成汇编代码
    print("======编译开始======")
    try:
        code = codegen.codegen(parse.prog)
    except Exception as e:
        print("编译错误：", e)
        print(codegen.code)
        exit(1)
    if DEBUG:
        # 输出汇编代码，用于调试
        print("======编译结果======")
        print(code)

    # 解释执行汇编代码
    print("======解释执行开始======")
    interpreter.run(code)
    print(interpreter.output)
