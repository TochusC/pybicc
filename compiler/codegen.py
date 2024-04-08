"""
# 语法分析文件codegen.py

##  将词法分析输出的抽象语法树转换为汇编语言。
"""
import struct

from compiler import type, parse

code = ""

argreg1 = ["dil", "sil", "dl", "cl", "r8b", "r9b"]
argreg2 = ["di", "si", "dx", "cx", "r8w", "r9w"]
argreg4 = ["edi", "esi", "edx", "ecx", "r8d", "r9d"]
argreg8 = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]

labelseq = 1
brkseq = 1
contseq = 1

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


def float_to_ieee754(f):
    # 将浮点数转换为IEEE 754格式的二进制表示（32位）
    packed = struct.pack('>f', f)
    # 只取前4个字节（32位），即4个十六进制数
    hex_representation = ''.join(f'{byte:02x}' for byte in packed[:4])
    return hex_representation


def double_to_ieee754(num):
    # 将浮点数转换为 64 位 IEEE 754 格式的字节序列
    ieee754_bytes = struct.pack('>d', num)
    # 将字节序列转换为十六进制表示
    ieee754_hex = ''.join(f'{byte:02X}' for byte in ieee754_bytes)
    return ieee754_hex


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


def truncate(ty):
    global code
    code += "  pop rax\n"

    if ty.kind is type.TypeKind.TY_BOOL:
        code += "  cmp rax, 0\n"
        code += "  setne al\n"

    if ty.size == 1:
        code += "  movsx rax, al\n"
    elif ty.size == 2:
        code += "  movsx rax, ax\n"
    elif ty.size == 4:
        code += "  movsxd rax, eax\n"

    code += "  push rax\n"


def inc(ty):
    global code
    code += "  pop rax\n"
    if ty.base is None:
        code += "  add rax, 1\n"
    else:
        code += f"  add rax, {ty.base.size}\n"
    code += "  push rax\n"


def dec(ty):
    global code
    code += "  pop rax\n"
    if ty.base is None:
        code += "  sub rax, 1\n"
    else:
        code += f"  sub rax, {ty.base.size}\n"
    code += "  push rax\n"


def gen_binary(node):
    global code
    code += "  pop rdi\n"
    code += "  pop rax\n"

    if node.kind in [parse.NodeKind.ND_ADD, parse.NodeKind.ND_ADD_EQ]:
        code += "  add rax, rdi\n"
    elif node.kind in [parse.NodeKind.ND_SUB, parse.NodeKind.ND_SUB_EQ]:
        code += "  sub rax, rdi\n"
    elif node.kind in [parse.NodeKind.ND_PTR_ADD, parse.NodeKind.ND_PTR_ADD_EQ]:
        code += f"  imul rdi, {node.ty.base.size}\n"
        code += "  add rax, rdi\n"
    elif node.kind in [parse.NodeKind.ND_PTR_SUB, parse.NodeKind.ND_PTR_SUB_EQ]:
        code += f"  imul rdi, {node.ty.base.size}\n"
        code += "  sub rax, rdi\n"
    elif node.kind in [parse.NodeKind.ND_PTR_DIFF]:
        code += "  sub rax, rdi\n"
        code += "  cqo\n"
        code += f"  mov rdi, {node.ty.base.size}\n"
        code += "  idiv rdi\n"
    elif node.kind in [parse.NodeKind.ND_MUL, parse.NodeKind.ND_MUL_EQ]:
        code += "  imul rax, rdi\n"
    elif node.kind in [parse.NodeKind.ND_DIV, parse.NodeKind.ND_DIV_EQ]:
        code += "  cqo\n"
        code += "  idiv rdi\n"
    elif node.kind in [parse.NodeKind.ND_BITAND]:
        code += "  and rax, rdi\n"
    elif node.kind in [parse.NodeKind.ND_BITOR]:
        code += "  or rax, rdi\n"
    elif node.kind in [parse.NodeKind.ND_BITXOR]:
        code += "  xor rax, rdi\n"
    elif node.kind in [parse.NodeKind.ND_SHL, parse.NodeKind.ND_SHL_EQ]:
        code += "  mov cl, rdi\n"
        code += "  shl rax, cl\n"
    elif node.kind in [parse.NodeKind.ND_SHR, parse.NodeKind.ND_SHR_EQ]:
        code += "  mov cl, rdi\n"
        code += "  sar rax, cl\n"
    elif node.kind in [parse.NodeKind.ND_EQ]:
        code += "  cmp rax, rdi\n"
        code += "  sete al\n"
        code += "  movzb rax, al\n"
    elif node.kind in [parse.NodeKind.ND_NE]:
        code += "  cmp rax, rdi\n"
        code += "  setne al\n"
        code += "  movzb rax, al\n"
    elif node.kind in [parse.NodeKind.ND_LT]:
        code += "  cmp rax, rdi\n"
        code += "  setl al\n"
        code += "  movzb rax, al\n"
    elif node.kind in [parse.NodeKind.ND_LE]:
        code += "  cmp rax, rdi\n"
        code += "  setle al\n"
        code += "  movzb rax, al\n"
    code += "  push rax\n"


def gen(node):
    global code, labelseq, brkseq, contseq

    if node is None:
        return code
    elif node.kind == parse.NodeKind.ND_NULL:
        return code
    elif node.kind == parse.NodeKind.ND_NUM:
        if node.ty.kind == type.TypeKind.TY_FLOAT:
            code += f"  push {float_to_ieee754(node.val)}\n"
        elif node.ty.kind == type.TypeKind.TY_DOUBLE:
            code += f"  push {double_to_ieee754(node.val)}\n"
        else:
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
    elif node.kind == parse.NodeKind.ND_PRE_INC:
        gen_lval(node.lhs)
        code += "  push [rsp]\n"
        load(node.ty)
        inc(node.ty)
        store(node.ty)
        return code
    elif node.kind == parse.NodeKind.ND_PRE_DEC:
        gen_lval(node.lhs)
        code += "  push [rsp]\n"
        load(node.ty)
        dec(node.ty)
        store(node.ty)
        return code
    elif node.kind == parse.NodeKind.ND_POST_INC:
        gen_lval(node.lhs)
        code += "  push [rsp]\n"
        load(node.ty)
        inc(node.ty)
        store(node.ty)
        dec(node.ty)
        return code
    elif node.kind == parse.NodeKind.ND_POST_DEC:
        gen_lval(node.lhs)
        code += "  push [rsp]\n"
        load(node.ty)
        dec(node.ty)
        store(node.ty)
        inc(node.ty)
        return code
    elif node.kind in [parse.NodeKind.ND_ADD_EQ, parse.NodeKind.ND_SUB_EQ,
                       parse.NodeKind.ND_PTR_ADD_EQ, parse.NodeKind.ND_PTR_SUB_EQ,
                       parse.NodeKind.ND_MUL_EQ, parse.NodeKind.ND_DIV_EQ,
                       parse.NodeKind.ND_SHL_EQ, parse.NodeKind.ND_SHR_EQ,]:
        gen_lval(node.lhs)
        code += "  push [rsp]\n"
        load(node.lhs.ty)
        gen(node.rhs)
        gen_binary(node)
        store(node.lhs.ty)
        return code
    elif node.kind == parse.NodeKind.ND_COMMA:
        gen(node.lhs)
        gen(node.rhs)
        return code
    elif node.kind == parse.NodeKind.ND_ADDR:
        gen_addr(node.lhs)
        return code
    elif node.kind == parse.NodeKind.ND_DEREF:
        gen(node.lhs)
        if node.ty.kind != type.TypeKind.TY_ARRAY:
            load(node.ty)
        return code
    elif node.kind == parse.NodeKind.ND_NOT:
        gen(node.lhs)
        code += "  pop rax\n"
        code += "  cmp rax, 0\n"
        code += "  sete al\n"
        code += "  movzb rax, al\n"
        code += "  push rax\n"
        return code
    elif node.kind == parse.NodeKind.ND_BITNOT:
        gen(node.lhs)
        code += "  pop rax\n"
        code += "  not rax\n"
        code += "  push rax\n"
        return code
    elif node.kind == parse.NodeKind.ND_LOGAND:
        seq = labelseq
        labelseq += 1
        gen(node.lhs)
        code += "  pop rax\n"
        code += "  cmp rax, 0\n"
        code += f"  je .L.false.{seq}\n"
        gen(node.rhs)
        code += "  pop rax\n"
        code += "  cmp rax, 0\n"
        code += f"  je .L.false.{seq}\n"
        code += "  push 1\n"
        code += f"  jmp .L.end.{seq}\n"
        code += f".L.false.{seq}:\n"
        code += "  push 0\n"
        code += f".L.end.{seq}:\n"
        return code
    elif node.kind == parse.NodeKind.ND_LOGOR:
        seq = labelseq
        labelseq += 1
        gen(node.lhs)
        code += "  pop rax\n"
        code += "  cmp rax, 0\n"
        code += f"  jne .L.true.{seq}\n"
        gen(node.rhs)
        code += "  pop rax\n"
        code += "  cmp rax, 0\n"
        code += f"  jne .L.true.{seq}\n"
        code += "  push 0\n"
        code += f"  jmp .L.end.{seq}\n"
        code += f".L.true.{seq}:\n"
        code += "  push 1\n"
        code += f".L.end.{seq}:\n"
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
        brkseq = contseq = labelseq
        labelseq += 1

        brk = brkseq
        cont = contseq

        code += f".L.continue.{cont}:\n"
        gen(node.cond)
        code += "  pop rax\n"
        code += "  cmp rax, 0\n"
        code += f"  je .L.break.{brk}\n"
        gen(node.then)

        code += f"  jmp .L.continue.{cont}\n"
        code += f".L.break.{brk}:\n"

        brkseq = brk
        contseq = cont
        return code
    elif node.kind == parse.NodeKind.ND_FOR:
        seq = labelseq
        brkseq = contseq = labelseq
        labelseq += 1

        brk = brkseq
        cont = contseq

        if node.init:
            gen(node.init)
        code += f".L.begin.{seq}:\n"
        if node.cond:
            gen(node.cond)
            code += "  pop rax\n"
            code += "  cmp rax, 0\n"
            code += f"  je .L.break.{brk}\n"
        gen(node.then)
        code += f".L.continue.{cont}:\n"
        if node.inc:
            gen(node.inc)
        code += f"  jmp .L.begin.{seq}\n"
        code += f".L.break.{brk}:\n"

        brkseq = brk
        contseq = cont
        return code

    elif node.kind == parse.NodeKind.ND_SWITCH:
        seq = labelseq
        labelseq += 1

        brk = brkseq
        brkseq = seq

        node.case_label = seq

        gen(node.cond)
        code += "  pop rax\n"

        case_node = node.case_next
        while case_node is not None:
            case_node.case_label = labelseq
            labelseq += 1
            case_node.case_end_label = seq
            code += f"  cmp rax, {case_node.val}\n"
            code += f"  je .L.case.{case_node.case_label}\n"
            case_node = case_node.case_next

        if node.default_case:
            node.default_case.case_label = labelseq
            labelseq += 1
            node.default_case.case_end_label = seq
            code += f"  jmp .L.case.{node.default_case.case_label}\n"

        code += f"  jmp .L.break.{brk}\n"
        gen(node.then)
        code += f".L.break.{brk}:\n"

        brkseq = brk
        return code

    elif node.kind == parse.NodeKind.ND_CASE:
        code += f".L.case.{node.case_label}:\n"
        gen(node.lhs)
        return code

    elif node.kind == parse.NodeKind.ND_BLOCK:
        node = node.body
        while node is not None:
            gen(node)
            node = node.next
        return code
    elif node.kind == parse.NodeKind.ND_BREAK:
        if brkseq == 0:
            raise RuntimeError("stray break statement")
        code += f"  jmp .L.break.{brkseq}\n"
        return code
    elif node.kind == parse.NodeKind.ND_CONTINUE:
        if contseq == 0:
            raise RuntimeError("stray continue statement")
        code += f"  jmp .L.continue.{contseq}\n"
        return code
    elif node.kind == parse.NodeKind.ND_GOTO:
        code += f"  jmp .L.label.{node.label_name}\n"
        return code
    elif node.kind == parse.NodeKind.ND_LABEL:
        code += f".L.label.{node.label_name}:\n"
        gen(node.lhs)
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
    elif node.kind is parse.NodeKind.ND_CAST:
        gen(node.lhs)
        truncate(node.ty)
        return code

    gen(node.lhs)
    gen(node.rhs)
    gen_binary(node)

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
        if not fn.is_static:
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
