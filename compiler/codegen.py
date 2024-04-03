"""
# 语法分析文件codegen.py

##  将词法分析输出的抽象语法树转换为汇编语言。
"""

from compiler import type, parse

code = ""

argreg1 = ["dil", "sil", "dl", "cl", "r8b", "r9b"]
argreg2 = ["di", "si", "dx", "cx", "r8w", "r9w"]
argreg4 = ["edi", "esi", "edx", "ecx", "r8d", "r9d"]
argreg8 = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]

labelseq = 1
funcname = None


def gen_addr(node):
    global code
    if node.kind == parse.NodeKind.ND_VAR:
        var = node.var
        if var.is_local:
            code += f"  lea rax, [rbp-{var.offset}]\n"
            code += "  push rax\n"
        else:
            code += f"  push offset {var.name}\n"
    elif node.kind == parse.NodeKind.ND_DEREF:
        gen(node.lhs)
    elif node.kind == parse.NodeKind.ND_MEMBER:
        gen_addr(node.lhs)
        code += f"  pop rax\n"
        code += f"  add rax, {node.member.offset}\n"
        code += "  push rax\n"

    else:
        raise RuntimeError(f"Error: {node.kind, node.tok.str} is not an lvalue.\n")


def gen_lval(node):
    global code
    if node.ty.kind == type.TypeKind.TY_ARRAY:
        raise RuntimeError(f"Error: {node.tok.str} is not an lvalue.\n")
    gen_addr(node)


def load(ty):
    global code
    code += "  pop rax\n"

    if ty.size == 1:
        code += "  movsx rax, byte ptr [rax]\n"
    elif ty.size == 2:
        code += "  movsx rax, word ptr [rax]\n"
    elif ty.size == 4:
        code += "  movsxd rax, dword ptr [rax]\n"
    elif ty.size == 8:
        code += "  mov rax, [rax]\n"

    code += "  push rax\n"


def store(ty):
    global code

    if ty.kind == type.TypeKind.TY_BOOL:
        code += "  cmp rdi, 0\n"
        code += "  setne dil\n"
        code += "  movzb rdi, dil\n"

    if ty.size == 1:
        code += "  pop dil\n"
        code += "  pop rax\n"
        code += "  mov [rax], dil\n"
        code += "  push dil\n"
    elif ty.size == 2:
        code += "  pop di\n"
        code += "  pop rax\n"
        code += "  mov [rax], di\n"
        code += "  push di\n"
    elif ty.size == 4:
        code += "  pop edi\n"
        code += "  pop rax\n"
        code += "  mov [rax], edi\n"
        code += "  push edi\n"
    elif ty.size == 8:
        code += "  pop rdi\n"
        code += "  pop rax\n"
        code += "  mov [rax], rdi\n"
        code += "  push rdi\n"


def gen(node):
    global code, labelseq

    if node is None:
        return code
    elif node.kind == parse.NodeKind.ND_NULL:
        return code
    elif node.kind == parse.NodeKind.ND_NUM:
        code += "  push " + str(node.val) + "\n"
        return code
    elif node.kind == parse.NodeKind.ND_EXPR_STMT:
        gen(node.lhs)
        code += "  add rsp, 8\n"
        return code
    elif node.kind == parse.NodeKind.ND_VAR \
            or node.kind == parse.NodeKind.ND_MEMBER:
        gen_addr(node)
        if node.ty.kind != type.TypeKind.TY_ARRAY:
            load(node.ty)
        return code
    elif node.kind == parse.NodeKind.ND_ASSIGN:
        gen_lval(node.lhs)
        gen(node.rhs)
        store(node.ty)
        return code
    elif node.kind == parse.NodeKind.ND_ADDR:
        gen_addr(node.lhs)
        return code
    elif node.kind == parse.NodeKind.ND_DEREF:
        gen(node.lhs)
        if node.ty.kind != type.TypeKind.TY_ARRAY:
            load(node.ty)
        return code
    elif node.kind == parse.NodeKind.ND_IF:
        seq = labelseq
        labelseq += 1
        if node.els:
            gen(node.cond)
            code += "  pop rax\n"
            code += "  cmp rax, 0\n"
            code += f"  je .L.else.{seq}\n"
            gen(node.then)
            code += f"  jmp .L.end.{seq}\n"
            code += f".L.else.{seq}:\n"
            gen(node.els)
            code += f".L.end.{seq}:\n"
        else:
            gen(node.cond)
            code += "  pop rax\n"
            code += "  cmp rax, 0\n"
            code += f"  je .L.end.{seq}\n"
            gen(node.then)
            code += f".L.end.{seq}:\n"
        return code
    elif node.kind == parse.NodeKind.ND_WHILE:
        seq = labelseq
        labelseq += 1
        code += f".L.begin.{seq}:\n"
        gen(node.cond)
        code += "  pop rax\n"
        code += "  cmp rax, 0\n"
        code += f"  je .L.end.{seq}\n"
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
            code += f"  je .L.end.{seq}\n"
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

        for i in range(nargs - 1, -1, -1):
            code += f"  pop {argreg8[i]}\n"

        seq = labelseq
        labelseq += 1

        code += "  mov rax, rsp\n"
        code += "  and rax, 15\n"
        code += f"  jnz .L.call.{seq}\n"
        code += "  mov rax, 0\n"
        code += f"  call {node.funcname}\n"
        code += f"  jmp .L.end.{seq}\n"
        code += f".L.call.{seq}:\n"
        code += "  sub rsp, 8\n"
        code += "  mov rax, 0\n"
        code += f"  call {node.funcname}\n"
        code += "  add rsp, 8\n"
        code += f".L.end.{seq}:\n"
        code += "  push rax\n"
        return code
    elif node.kind == parse.NodeKind.ND_RETURN:
        gen(node.lhs)
        code += "  pop rax\n"
        code += f"  jmp .L.return.{funcname}\n"
        return code

    gen(node.lhs)
    gen(node.rhs)

    code += "  pop rdi\n"
    code += "  pop rax\n"

    if node.kind == parse.NodeKind.ND_ADD:
        code += "  add rax, rdi\n"
    elif node.kind == parse.NodeKind.ND_PTR_ADD:
        code += f"  imul rdi, {node.ty.base.size}\n"
        code += "  add rax, rdi\n"
    elif node.kind == parse.NodeKind.ND_SUB:
        code += "sub rax, rdi\n"
    elif node.kind == parse.NodeKind.ND_PTR_SUB:
        code += f"  imul rdi, {node.ty.base.size}\n"
        code += "  sub rax, rdi\n"
    elif node.kind == parse.NodeKind.ND_PTR_DIFF:
        code += "  sub rax, rdi\n"
        code += "  cqo\n"
        code += f"  mov rdi, {node.ty.base.size}\n"
        code += "  idiv rdi\n"
    elif node.kind == parse.NodeKind.ND_MUL:
        code += "  imul rax, rdi\n"
    elif node.kind == parse.NodeKind.ND_DIV:
        code += "  cqo\n"
        code += "  idiv rdi\n"
    elif node.kind == parse.NodeKind.ND_EQ:
        code += "  cmp rax, rdi\n"
        code += "  sete al\n"
        code += "  movzb rax, al\n"
    elif node.kind == parse.NodeKind.ND_NE:
        code += "  cmp rax, rdi\n"
        code += "  setne al\n"
        code += "  movzb rax, al\n"
    elif node.kind == parse.NodeKind.ND_LT:
        code += "  cmp rax, rdi\n"
        code += "  setl al\n"
        code += "  movzb rax, al\n"
    elif node.kind == parse.NodeKind.ND_LE:
        code += "  cmp rax, rdi\n"
        code += "  setle al\n"
        code += "  movzb rax, al\n"

    code += "  push rax\n"
    return code


def emit_data(prog):
    global code
    code += ".data\n"

    vl = prog.globals
    while vl is not None:
        var = vl.var
        code += f"{var.name}:\n"

        if not var.contents:
            code += f"  .zero {var.ty.size}\n"
            vl = vl.next
            continue

        for i in range(var.cont_len):
            code += f"  .byte {var.contents[i]}\n"
        vl = vl.next
    return code


def load_arg(var, idx):
    global code
    sz = var.ty.size
    if sz == 1:
        code += f"  mov [rbp-{var.offset}], {argreg1[idx]}\n"
    elif sz == 2:
        code += f"  mov [rbp-{var.offset}], {argreg2[idx]}\n"
    elif sz == 4:
        code += f"  mov [rbp-{var.offset}], {argreg4[idx]}\n"
    elif sz == 8:
        code += f"  mov [rbp-{var.offset}], {argreg8[idx]}\n"


def emit_text(prog):
    global code, funcname

    code += ".text\n"

    fn = prog.fns
    while fn is not None:
        code += f".global {fn.name}\n"
        code += f"{fn.name}:\n"
        funcname = fn.name

        # 前置工作
        code += "  push rbp\n"
        code += "  mov rbp, rsp\n"
        code += f"  sub rsp, {fn.stack_size}\n"

        # 参数入栈
        i = 0
        vl = fn.params
        while vl is not None:
            var = vl.var
            load_arg(var, i)
            i += 1
            vl = vl.next

        node = fn.node
        while node is not None:
            gen(node)
            node = node.next

        # 善后工作
        code += f".L.return.{funcname}:\n"
        code += "  mov rsp, rbp\n"
        code += "  pop rbp\n"
        code += "  ret\n"

        fn = fn.next

    return code


def codegen(prog):
    global code
    code = ""
    code += ".intel_syntax noprefix\n"
    emit_data(prog)
    emit_text(prog)
    return code
