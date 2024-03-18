"""
    # pybicc v0.1.4u - 一个简单的类C语言编译器 + 汇编代码解释器
        目前只支持包含+ - * / ( ) < > == != <= >=等运算符的数学表达式
        完成了变量定义的词法分析和语法分析
        支持多条以;分隔的表达式。
        不支持浮点数/负数

    ## 代码结构：
    ---
        - main.py           目前的编译器程序入口
        - tokenize.py       词法分析，将源代码转换为链表存储的Token
        - parse.py:         语法分析，将Token转换为抽象语法树
        - codegen.py        语义生成，将抽象语法树转换为汇编代码
        - simulator.py      汇编代码解释器
        - interface.py      图形化界面，尚未与编译器和解释器整合

    ## 输入样例：
    ---
        - 7 + 9 * 2
        - 3+ (4 / 2)
        - 1 != 2
        - 5 == 3+1 + 4
        - 8 <= 9 * (3 +1)
"""

import codegen
import simulator
import tokenize
import parse

# 需要编译的代码
codeToCompile = """
    main() { x=3; y=5; *(&y-8)=7; return x; }
"""

DEBUG = True


# 前序遍历输出node，用于调试
def print_node(node):

    if node.kind == parse.NodeKind.ND_NUM:
        print(node.kind, node.val, end=' ')
    elif node.kind == parse.NodeKind.ND_VAR:
        print(node.kind, node.var.name, end=' ')

    elif node.kind == parse.NodeKind.ND_FUNCALL:
        print(node.funcname, end=' ')
        args = node.args
        print("args:", end="\n==函数参数开始==\n")
        while args is not None:
            print_node(args)
            args = args.next
        print("==函数参数结束==")
    else:
        print(node.kind, end=" ")
    print()

    if node.lhs is not None:
        print_node(node.lhs)
    if node.rhs is not None:
        print_node(node.rhs)

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

    if DEBUG:
        # 输出node，用于调试
        print("======语法分析结果======")
        print("====函数名:", parse.prog.name, "====", sep="")

        print("====函数参数====")
        params = parse.prog.params

        print("====局部变量====")
        locals = parse.prog.locals

        print("===函数语句===")
        func = parse.prog.node
        while func is not None:
            print_node(func)
            func = func.next
        print("===语句结束===")



    offset = 0
    var = parse.prog.locals
    while var is not None:
        offset += 8
        var.offset = offset
        var = var.next
    parse.prog.stack_size = offset

    # # TODO 变量定义还未完成，会报错。
    # # 编译成汇编代码
    # code = codegen.codegen(parse.prog)
    # print("======编译开始======")
    # if DEBUG:
    #     # 输出汇编代码，用于调试
    #     print("======编译结果======")
    #     print(code)
    #
    # # 解释执行汇编代码
    # print("======解释执行开始======")
    # simulator.run(code)
