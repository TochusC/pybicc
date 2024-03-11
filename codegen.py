"""
# 语法分析文件codegen.py

##  将词法分析输出的抽象语法树转换为汇编语言。
"""

import parse

code = ""


def gen(node):
    global code

    if node.kind == parse.NodeKind.ND_NUM:
        code += "push " + str(node.val) + "\n"
        return code
    elif node.kind == parse.NodeKind.ND_RETURN:
        gen(node.lhs)
        code += "  pop rax\n"
        code += "  ret\n"
        return code
    elif node.kind == parse.NodeKind.ND_EXPR_STMT:
        gen(node.lhs)
        code += "  add rsp, 8\n"
        return code

    gen(node.lhs)
    gen(node.rhs)

    code += "pop rdi\n"
    code += "pop rax\n"

    if node.kind == parse.NodeKind.ND_ADD:
        code += "add rax, rdi\n"
    elif node.kind == parse.NodeKind.ND_SUB:
        code += "sub rax, rdi\n"
    elif node.kind == parse.NodeKind.ND_MUL:
        code += "imul rax, rdi\n"
    elif node.kind == parse.NodeKind.ND_DIV:
        code += "cqo\n"
        code += "idiv rdi\n"
    elif node.kind == parse.NodeKind.ND_EQ:
        code += "cmp rax, rdi\n"
        code += "sete al\n"
        code += "movzb rax, al\n"
    elif node.kind == parse.NodeKind.ND_NE:
        code += "cmp rax, rdi\n"
        code += "setne al\n"
        code += "movzb rax, al\n"
    elif node.kind == parse.NodeKind.ND_LT:
        code += "cmp rax, rdi\n"
        code += "setl al\n"
        code += "movzb rax, al\n"
    elif node.kind == parse.NodeKind.ND_LE:
        code += "cmp rax, rdi\n"
        code += "setle al\n"
        code += "movzb rax, al\n"

    code += "push rax\n"
    return code


def codegen(node):
    global code

    code += "  .intel_syntax noprefix\n"
    code += "  .global main\n"
    code += "main:\n"

    while node is not None:
        gen(node)
        node = node.next


    return code
