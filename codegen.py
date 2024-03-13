"""
# 语法分析文件codegen.py

##  将词法分析输出的抽象语法树转换为汇编语言。
"""

import parse

code = ""


def gen_addr(node):
    global code
    if node.kind == parse.NodeKind.ND_VAR:
        code += f"  lea rax, [rbp-{node.var.offset}]\n"
        code += "  push rax\n"
        return code
    else:
        return "not an lvalue"


def load():
    global code
    code += "  pop rax\n"
    code += "  mov rax, [rax]\n"
    code += "  push rax\n"


def store():
    global code
    code += "  pop rdi\n"
    code += "  pop rax\n"
    code += "  mov [rax], rdi\n"
    code += "  push rdi\n"


def gen(node):
    global code

    if node.kind == parse.NodeKind.ND_NUM:
        code += "push " + str(node.val) + "\n"
        return code
    elif node.kind == parse.NodeKind.ND_RETURN:
        gen(node.lhs)
        code += "  pop rax\n"
        code += "  jmp .L.return\n"
        return code
    elif node.kind == parse.NodeKind.ND_EXPR_STMT:
        gen(node.lhs)
        code += "  add rsp, 8\n"
        return code
    elif node.kind == parse.NodeKind.ND_VAR:
        gen_addr(node)
        load()
        return code
    elif node.kind == parse.NodeKind.ND_ASSIGN:
        gen_addr(node.lhs)
        gen(node.rhs)
        store()
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


def codegen(prog):
    global code

    code += "  .intel_syntax noprefix\n"
    code += "  .global main\n"
    code += "main:\n"

    # 前置工作
    code += "  push rbp\n"
    code += "  mov rbp, rsp\n"
    code += f"  sub rsp, {prog.stack_size}\n"

    node = prog.node
    while node is not None:
        gen(node)
        node = node.next

    # 善后工作
    code += ".L.return:\n"
    code += "  mov rsp, rbp\n"
    code += "  pop rbp\n"
    code += "  ret\n"

    return code
