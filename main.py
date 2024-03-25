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

# 循环有问题
# codeToCompile = """
#  int main() {
#  int x = 0;
#  while(x <= 10){
#  x = x + 1;
#  }
#  return 0;
# }
# """

codeToCompile = """
 int main() {
    int x=3;
    int y=5;
    return foo(&x, y);
    }
    int foo(int *x, int y)
    {
        return *x + y;
    }
"""

DEBUG = True


# 前序遍历输出node，用于调试
def print_node(node):
    if node.kind == parse.NodeKind.ND_NUM:
        print(node.kind, node.val, end=' ')
    elif node.kind == parse.NodeKind.ND_VAR:
        print(node.kind, node.var.name, end=' ')

    elif node.kind == parse.NodeKind.ND_FUNCALL:
        print(node.kind, node.funcname, end='\n')
        args = node.args
        print("==函数参数开始==")
        while args is not None:
            print_node(args)
            args = args.next
        print("==函数参数结束==", end=" ")
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

    fn = parse.prog
    while fn is not None:
        offset = 0
        vl = fn.locals
        while vl is not None:
            offset += 8
            vl.var.offset = offset
            vl = vl.next
        fn.stack_size = offset
        fn = fn.next
    offset = 0

    if DEBUG:
        # 输出node，用于调试
        print("======语法分析结果======")
        fn = parse.prog

        while fn is not None:
            print("=====函数名:", fn.name, "=====", sep="")
            print("===函数参数===")
            params = fn.params

            print("===局部变量===")
            locals = fn.locals

            print("===函数语句===")
            node = fn.node
            while node is not None:
                print_node(node)
                node = node.next
            print("=====函数结束======")
            fn = fn.next


    # 编译成汇编代码
    code = codegen.codegen(parse.prog)
    print("======编译开始======")
    if DEBUG:
        # 输出汇编代码，用于调试
        print("======编译结果======")
        print(code)

    # 解释执行汇编代码
    print("======解释执行开始======")
    simulator.run(code)
