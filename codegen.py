"""
# 语法分析文件codegen.py

##  将词法分析输出的抽象语法树转换为汇编语言。
"""

import parse

code = ""

labelseq = 1

argreg = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]

funcname = []


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
    global code, labelseq

    if node is None:
        return code

    if node.kind == parse.NodeKind.ND_NUM:
        code += "  push " + str(node.val) + "\n"
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
    elif node.kind == parse.NodeKind.ND_IF:
        seq = labelseq
        labelseq += 1
        if node.els:
            gen(node.cond)
            code += "  pop rax\n"
            code += "  cmp rax, 0\n"
            code += f"  je  .L.else.{seq}\n"
            gen(node.then)
            code += f"  jmp .L.end.{seq}\n"
            code += f".L.else.{seq}:\n"
            gen(node.els)
            code += f".L.end.{seq}:\n"
        else:
            gen(node.cond)
            code += "  pop rax\n"
            code += "  cmp rax, 0\n"
            code += f"  je  .L.end.{seq}\n"
            gen(node.then)
            code += f".L.end.{seq}:\n"

        return code
    elif node.kind == parse.NodeKind.ND_WHILE:
        seq = labelseq
        labelseq += 1
        code += f".L.begin.{seq}:\n"
        gen(node.kind)
        code += "  pop rax\n"
        code += "  cmp rax, 0\n"
        code += f"  je  .L.end.{seq}\n"
        gen(node.then)
        code += f"  jmp .L.begin.{seq}\n"
        code += f".L.end.{seq}:\n"
        return code
    elif node.kind == parse.NodeKind.ND_FOR:
        seq = labelseq
        labelseq += 1
        if node.init:
            gen(node.init)
        code += f".L.begin.{seq}:\n"
        if node.cond:
            gen(node.cond)
            code += "  pop rax\n"
            code += "  cmp rax, 0\n"
            code += f"  je  .L.end.{seq}\n"
        gen(node.then)
        if node.inc:
            gen(node.inc)
        code += f"  jmp .L.begin.{seq}\n"
        code += f".L.end.{seq}:\n"
        return code
    elif node.kind == parse.NodeKind.ND_BLOCK:
        node = node.body
        while node is not None:
            gen(node)
            node = node.next
        return code
    elif node.kind == parse.NodeKind.ND_FUNCALL:
        nargs = 0
        arg = node.args
        while arg is not None:
            gen(arg)
            arg = arg.next
            nargs += 1

        nargs = len(argreg)
        for i in range(nargs - 1, -1, -1):
            code += f"  pop {argreg[i]}"

        seq = labelseq
        labelseq += 1
        code += "  mov rax, rsp\n"
        code += "  and rax, 15\n"
        code += "  jnz .L.call.{seq}\n"
        code += "  mov rax, 0\n"
        code += f"  call {node.funcname}\n"
        code += "  jmp .L.end.{seq}\n"
        code += ".L.call.{seq}:\n"
        code += "  sub rsp, 8\n"
        code += "  mov rax, 0\n"
        code += f"  call {node.funcname}\n"
        code += "  add rsp, 8\n"
        code += f".L.end.{seq}:\n"
        code += "  push rax\n"
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
    global code, funcname

    code += ".intel_syntax noprefix\n"
    # code += "  .global main\n"
    # code += "main:\n"

    fn = prog
    while fn is not None:
        code += f".global {fn.name}\n"
        code += f"{fn.name}:\n"
        funcname = fn.name

        # 前置工作
        code += "  push rbp\n"
        code += "  mov rbp, rsp\n"
        code += f"  sub rsp, {fn.stack_size}\n"

        node = fn.node
        while node is not None:
            gen(node)
            node = node.next

        # 善后工作
        code += ".L.return:\n"
        code += "  mov rsp, rbp\n"
        code += "  pop rbp\n"
        code += "  ret\n"

        fn = fn.next

    return code
