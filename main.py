"""
    # pybicc v0.1.2 - 一个简单的类C语言编译器 + 汇编代码解释器
        目前只支持包含+ - * / ( ) < > == != <= >=等运算符的数学表达式
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
        - 7+9*2
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
    6 + 7
"""

DEBUG = True

# 前序遍历输出node，用于调试
def print_node(node):
    if node.kind == parse.NodeKind.ND_NUM:
        print(node.kind, node.val)
    else:
        print(node.kind)

    if node.lhs is not None:
        print_node(node.lhs)
    if node.rhs is not None:
        print_node(node.rhs)

if __name__ == '__main__':
    # 词法分析
    tokenize.token = tokenize.tokenize(codeToCompile)

    if DEBUG:
        # 输出token，用于调试
        print("======词法分析结果======")
        token = tokenize.token
        while token.next is not None:
            print(token.kind, token.str)
            token = token.next

    parse.node = parse.expr()

    if DEBUG:
        # 输出node，用于调试
        print("======语法分析结果======")
        print_node(parse.node)

    # 编译成汇编代码
    code = codegen.codegen(parse.node)
    if DEBUG:
        # 输出汇编代码，用于调试
        print("======编译结果======")
        print(code)

    # 解释执行汇编代码
    print("======执行结果======")
    simulator.run(code)

