from enum import Enum

from compiler import tokenize, type


class TagScope:
    next = None
    name = None
    ty = None


class VarScope:
    next = None
    name = None
    var = None
    typedef = None


class Scope:
    var_scope = VarScope()
    tag_scope = TagScope()


class NodeKind(Enum):
    ND_ADD = 1
    ND_SUB = 2
    ND_MUL = 3
    ND_DIV = 4
    ND_EQ = 5
    ND_NE = 6
    ND_LT = 7
    ND_LE = 8
    ND_NUM = 9  # 字面值整数常量
    ND_ROOT = 10  # 根节点
    ND_RETURN = 11  # 返回语句
    ND_EXPR_STMT = 12  # 表达式语句
    ND_VAR = 13  # 变量
    ND_ASSIGN = 14  # 赋值语句
    ND_IF = 15  # if 语句
    ND_WHILE = 16  # while 语句
    ND_FOR = 17  # for 语句
    ND_BLOCK = 18  # {}
    ND_DEFAULT = 19
    ND_FUNCALL = 20  # 函数调用
    ND_ADDR = 21  # 引用
    ND_DEREF = 22  # 解引用

    ND_PTR_ADD = 23  # 指针 + 数字
    ND_PTR_SUB = 24  # 指针 - 数字
    ND_PTR_DIFF = 25  # 指针 - 指针

    ND_NULL = 25  # 空
    ND_MEMBER = 26  # 结构体成员

    ND_CAST = 27


class Var:
    name = None  # 函数名
    offset = None  # 函数距离RBP的偏移量
    ty = None  # 类型
    is_local = None  # 是本地变量还是全局变量

    contents = None
    cont_len = None


class VarList:
    next = None
    var = None

    def __init__(self, next=None, var=None):
        self.next = next
        self.var = var


class Function:
    next = None
    name = None
    node = None
    locals = None
    stack_size = None

    # 参数
    params = None
    # 局部变量
    locals = None

    def __init__(self, next=None, name=None, node=None,
                 locals=None, stack_size=None):
        self.next = next
        self.name = name
        self.node = node
        self.locals = locals
        self.stack_size = stack_size


class Program:
    globals = None
    fns = None


class Node:
    kind = NodeKind.ND_NULL
    next = None
    lhs = None
    rhs = None
    val = None

    member = None

    # 指针
    ty = None  # 表示类型

    # 调试用
    tok = None

    # 变量
    var = None

    # if, while, for 语句
    cond = None
    then = None
    els = None
    init = None
    inc = None

    # {}
    body = None

    Member = None

    # 函数相关
    funcname = None
    args = None

    def __init__(self, kind=NodeKind.ND_NULL, val=None, lhs=None, rhs=None, next=None,
                 var=None, cond=None, then=None, els=None, tok=None):
        self.kind = kind
        self.lhs = lhs
        self.rhs = rhs
        self.val = val

        self.next = next

        self.var = var

        self.cond = cond
        self.then = then
        self.els = els

        self.tok = tok


cnt = 0

locals = VarList()
globals = VarList()

var_scope = VarScope()
tag_scope = TagScope()


def enter_scope():
    sc = Scope()
    sc.var_scope = var_scope
    sc.tag_scope = tag_scope
    return sc


def leave_scope(sc):
    global var_scope, tag_scope
    var_scope = sc.var_scope
    tag_scope = sc.tag_scope


def new_label():
    global cnt
    buf = ".L.data." + str(cnt)
    cnt += 1
    return buf


def find_var(tok=tokenize.token):
    global var_scope
    sc = var_scope
    while sc is not None:
        if sc.name == tok.str:
            return sc
        sc = sc.next
    return None


def find_tag(tok):
    global tag_scope
    tag = tag_scope
    while tag is not None:
        if tag.name == tok.str:
            return tag
        tag = tag.next
    return None


def new_var(name, ty, is_local):
    global var_scope

    var = Var()
    var.name = name
    var.ty = ty
    var.is_local = is_local

    return var


def new_lvar(name, ty):
    global locals

    var = new_var(name, ty, True)
    sc = push_scope(name)
    sc.var = var

    vl = VarList()
    vl.var = var
    vl.next = locals
    locals = vl
    return var


def new_gvar(name, ty, emit):
    global globals

    var = new_var(name, ty, False)
    sc = push_scope(name)
    sc.var = var

    if emit:
        vl = VarList()
        vl.var = var
        vl.next = globals
        globals = vl
    return var


def find_typedef(tok):
    if tok.kind == tokenize.TokenKind.TK_IDENT:
        sc = find_var(tok)
        if sc is not None:
            return sc.typedef
    return None

def new_node(kind, tok=tokenize.token):
    return Node(kind, tok=tok)


def new_binary(kind, lhs, rhs, tok=tokenize.token):
    return Node(kind, 0, lhs, rhs, tok=tok)


def new_unary(kind, lhs, tok=tokenize.token):
    return Node(kind, 0, lhs, tok=tok)


def new_num(val, tok=tokenize.token):
    return Node(NodeKind.ND_NUM, val, tok=tok)


def new_var_node(var, tok=tokenize.token):
    return Node(NodeKind.ND_VAR, var=var, tok=tok)


def push_scope(name):
    global var_scope
    sc = VarScope()
    sc.next = var_scope
    sc.name = name
    var_scope = sc
    return sc


def read_expr_stmt():
    return new_unary(NodeKind.ND_EXPR_STMT, expr(), tok=tokenize.token)


def read_type_suffix(base):
    if not tokenize.consume('['):
        return base
    sz = tokenize.expect_number()
    tokenize.expect(']')
    base = read_type_suffix(base)
    return type.array_of(base, sz)


def push_tag_scope(tok, ty):
    global tag_scope
    sc = TagScope()
    sc.next = tag_scope
    sc.name = tok.str
    sc.ty = ty
    tag_scope = sc


# struct-decl = "struct" ident
#             | "struct" ident? "{" struct-member "}"
def struct_decl():
    tokenize.expect("struct")

    tag = tokenize.consume_ident()

    if tag is not None and not tokenize.peek("{"):
        sc = find_tag(tag)
        if sc is None:
            raise RuntimeError("unknown struct type", tokenize.token)
        return sc.ty

    tokenize.expect("{")

    # 读取结构体成员
    head = type.Member()
    cur = head

    while not tokenize.consume('}'):
        cur.next = struct_member()
        cur = cur.next

    ty = type.Type()
    ty.kind = type.TypeKind.TY_STRUCT
    ty.members = head.next

    offset = 0
    mem = ty.members
    while mem is not None:
        offset = type.align_to(offset, mem.ty.align)
        mem.offset = offset
        offset += mem.ty.size

        if ty.align < mem.ty.align:
            ty.align = mem.ty.align

        mem = mem.next

    ty.size = type.align_to(offset, ty.align)

    if tag is not None:
        push_tag_scope(tag, ty)
    return ty


def struct_member():
    mem = type.Member()
    mem.ty = basetype()
    mem.name = tokenize.expect_ident()
    mem.ty = read_type_suffix(mem.ty)
    tokenize.expect(';')
    return mem


def read_func_param():
    ty = basetype()
    name = tokenize.expect_ident()
    vl = VarList()
    vl.var = new_lvar(name, ty)
    return vl


def read_func_params():
    if tokenize.consume(')'):
        return None

    head = read_func_param()
    cur = head

    while not tokenize.consume(')'):
        tokenize.expect(',')
        cur.next = read_func_param()
        cur = cur.next

    return head


prog = None


def global_var():
    ty = basetype()
    name = tokenize.expect_ident()
    ty = read_type_suffix(ty)
    tokenize.expect(';')
    new_gvar(name, ty, True)


# 决定最外层的是函数还是全局变量。
def is_function():
    tok = tokenize.token
    basetype()
    isfunc = tokenize.consume_ident() and tokenize.consume('(')
    tokenize.token = tok
    return isfunc


# program = (global-var | function)*
def program():
    global globals
    head = Function()
    cur = head
    globals = None

    while True:
        if tokenize.at_eof():
            break
        if is_function():
            fn = function()
            if fn is not None:
                cur.next = fn
                cur = cur.next
        else:
            global_var()

    prog = Program()
    prog.globals = globals
    prog.fns = head.next

    return prog


# basetype = builtin-type | struct-decl | typedef-name
# builtin-type = "void" | "_Bool" | "char" | "short" | "int" | "long"
def basetype():
    if not is_typename():
        raise RuntimeError("typename expected, but got %s", tokenize.token.str)
    if tokenize.consume('void'):
        ty = type.void_type
    elif tokenize.consume('bool'):
        ty = type.bool_type
    elif tokenize.consume('char'):
        ty = type.char_type
    elif tokenize.consume('short'):
        ty = type.short_type
    elif tokenize.consume('int'):
        ty = type.int_type
    elif tokenize.consume('long'):
        tokenize.consume('long')

        ty = type.long_type
    else:
        ty = struct_decl()

    while tokenize.consume('*'):
        ty = type.pointer_to(ty)
    return ty


# function = basetype declarator "(" params? ")" ("{" stmt* "}" | ";")
# params   = param ("," param)*
# param    = basetype ident
def function():
    global locals

    locals = None

    ty = basetype()
    fn = Function(name=tokenize.expect_ident())

    new_gvar(fn.name, type.func_type(ty), False)

    tokenize.expect('(')

    sc = enter_scope()
    fn.params = read_func_params()

    if tokenize.consume(';'):
        leave_scope(sc)
        return None

    # 读取函数体
    head = Node(NodeKind.ND_DEFAULT)
    cur = head
    tokenize.expect('{')
    while not tokenize.consume('}'):
        cur.next = stmt()
        cur = cur.next
    leave_scope(sc)

    fn.node = head.next
    fn.locals = locals

    return fn


# declaration = basetype ident ("[" num "]")* ("=" expr) ";"
#             | basetype ";"
def declaration():
    ty = basetype()
    if tokenize.consume(';'):
        return new_node(NodeKind.ND_NULL)

    name = tokenize.expect_ident()
    ty = read_type_suffix(ty)
    var = new_lvar(name, ty)

    if tokenize.consume(';'):
        return new_node(NodeKind.ND_NULL)

    tokenize.expect('=')
    lhs = new_var_node(var, tokenize.token)
    rhs = expr()
    tokenize.expect(';')
    node = new_binary(NodeKind.ND_ASSIGN, lhs, rhs, tokenize.token)
    return new_unary(NodeKind.ND_EXPR_STMT, node, tokenize.token)


def is_typename():
    return (tokenize.peek("int")
            or tokenize.peek("char")
            or tokenize.peek("struct")
            or tokenize.peek("short")
            or tokenize.peek("long")
            or tokenize.peek("void")
            or tokenize.peek("bool")
            or find_typedef(tokenize.token))


def stmt():
    node = stmt2()
    type.add_type(node)
    return node


# stmt2 = "return" expr ";"
#      | "if" "(" expr ")" stmt ("else" stmt)?
#      | "while" "(" expr ")" stmt
#      | "for" "(" expr? ";" expr? ";" expr? ")" stmt
#      | "{" stmt* "}"
#      | "typedef" basetype ident ("[" num "]")* ";"
#      | declaration
#      | expr ";"
def stmt2():
    if tokenize.consume("return"):
        node = new_unary(NodeKind.ND_RETURN, expr(), tok=tokenize.token)
        tokenize.expect(";")
        return node

    if tokenize.consume("if"):
        node = new_node(NodeKind.ND_IF)
        tokenize.expect("(")
        node.cond = expr()
        tokenize.expect(")")
        node.then = stmt()
        if tokenize.consume("else"):
            node.els = stmt()
        return node

    if tokenize.consume("while"):
        node = new_node(NodeKind.ND_WHILE)
        tokenize.expect("(")
        node.cond = expr()
        tokenize.expect(")")
        node.then = stmt()
        return node

    if tokenize.consume("for"):
        node = new_node(NodeKind.ND_FOR)
        tokenize.expect("(")
        if not tokenize.consume(";"):
            node.init = read_expr_stmt()
            tokenize.expect(";")
        if not tokenize.consume(";"):
            node.cond = expr()
            tokenize.expect(";")
        if not tokenize.consume(")"):
            node.inc = read_expr_stmt()
            tokenize.expect(")")
        node.then = stmt()
        return node

    if tokenize.consume("{"):
        head = new_node(NodeKind.ND_DEFAULT)
        cur = head

        sc = enter_scope()
        while not tokenize.consume("}"):
            cur.next = stmt()
            cur = cur.next
        leave_scope(sc)

        node = new_node(NodeKind.ND_BLOCK)
        node.body = head.next

        return node

    if tokenize.consume("typedef"):
        ty = basetype()
        name = tokenize.expect_ident()
        ty = read_type_suffix(ty)
        tokenize.expect(";")
        sc = push_scope(name)
        sc.typedef = ty
        return new_node(NodeKind.ND_NULL)

    if is_typename():
        return declaration()

    node = read_expr_stmt()
    tokenize.expect(";")
    return node


# expr = assign
def expr():
    return assign()


# assign = equality ("=" assign)?
def assign():
    node = equality()
    if tokenize.consume("="):
        node = new_binary(NodeKind.ND_ASSIGN, node, assign(), tok=tokenize.token)
    return node


# equality = relational ("==" relational | "!=" relational)*
def equality():
    node = relational()

    while True:
        if tokenize.consume("=="):
            node = new_binary(NodeKind.ND_EQ, node, relational(), tok=tokenize.token)
        elif tokenize.consume("!="):
            node = new_binary(NodeKind.ND_NE, node, relational(), tok=tokenize.token)
        else:
            return node


# relational = add ("<" add | "<=" add | ">" add | ">=" add)*
def relational():
    node = add()

    while True:
        if tokenize.consume("<"):
            node = new_binary(NodeKind.ND_LT, node, add(), tok=tokenize.token)
        elif tokenize.consume("<="):
            node = new_binary(NodeKind.ND_LE, node, add(), tok=tokenize.token)
        elif tokenize.consume(">"):
            node = new_binary(NodeKind.ND_LT, add(), node, tok=tokenize.token)
        elif tokenize.consume(">="):
            node = new_binary(NodeKind.ND_LE, add(), node, tok=tokenize.token)
        else:
            return node


def new_add(lhs, rhs, tok=tokenize.token):
    type.add_type(lhs)
    type.add_type(rhs)

    if type.is_integer(lhs.ty) and type.is_integer(rhs.ty):
        return new_binary(NodeKind.ND_ADD, lhs, rhs, tok)
    elif lhs.ty.base is not None and type.is_integer(rhs.ty):
        return new_binary(NodeKind.ND_PTR_ADD, lhs, rhs, tok)
    elif rhs.ty.base is not None and type.is_integer(lhs.ty):
        return new_binary(NodeKind.ND_PTR_ADD, rhs, lhs, tok)
    else:
        raise RuntimeError("invalid operands, %s", tok)


def new_sub(lhs, rhs, tok):
    type.add_type(lhs)
    type.add_type(rhs)

    if type.is_integer(lhs.ty) and type.is_integer(rhs.ty):
        return new_binary(NodeKind.ND_SUB, lhs, rhs, tok)
    elif lhs.ty.base is not None and type.is_integer(rhs.ty):
        return new_binary(NodeKind.ND_PTR_SUB, lhs, rhs, tok)
    elif lhs.ty.base is not None and rhs.ty.base is not None:
        return new_binary(NodeKind.ND_PTR_DIFF, lhs, rhs, tok)
    else:
        tokenize.error("invalid operands, %s", tok)


# add = mul ("+" mul | "-" mul)*
def add():
    node = mul()

    while True:
        if tokenize.consume("+"):
            node = new_add(node, mul(), tok=tokenize.token)
        elif tokenize.consume("-"):
            node = new_sub(node, mul(), tok=tokenize.token)
        else:
            return node


# mul = cast ("*" cast | "/" cast)*
def mul():
    node = unary()
    while True:
        if tokenize.consume("*"):
            node = new_binary(NodeKind.ND_MUL, node, cast(), tok=tokenize.token)
        elif tokenize.consume("/"):
            node = new_binary(NodeKind.ND_DIV, node, cast(), tok=tokenize.token)
        else:
            return node

# cast = "(" type-name ")" cast | unary
def cast():
    tok = tokenize.token

    if tokenize.consume('('):
        if is_typename():
            ty = basetype()
            tokenize.expect(')')
            node = new_unary(NodeKind.ND_CAST, cast())
            type.add_type(node.lhs)
            node.ty = ty
            return node
        tokenize.token = tok
    return unary()


# unary = ("+" | "-" | "*" | "&")? unary
#       | postfix
def unary():
    if tokenize.consume("+"):
        return unary()
    if tokenize.consume("-"):
        return new_binary(NodeKind.ND_SUB,
                          new_node(NodeKind.ND_NUM, 0),
                          primary())
    if tokenize.consume("&"):
        return new_unary(NodeKind.ND_ADDR, unary())
    if tokenize.consume("*"):
        return new_unary(NodeKind.ND_DEREF, unary())

    return postfix()


def find_member(ty, name):
    mem = ty.members
    while mem is not None:
        if mem.name == name:
            return mem
        mem = mem.next
    return None


def struct_ref(lhs):
    type.add_type(lhs)
    if lhs.ty.kind != type.TypeKind.TY_STRUCT:
        raise RuntimeError("not a struct", lhs.tok)

    mem = find_member(lhs.ty, tokenize.expect_ident())
    if mem is None:
        raise RuntimeError("no such member", tokenize.token)

    node = new_unary(NodeKind.ND_MEMBER, lhs)
    node.member = mem
    return node


# postfix = primary ("[" expr "]" | "." ident | "->" ident)*
def postfix():
    node = primary()

    while True:
        if tokenize.consume('['):
            exp = new_add(node, expr())
            tokenize.expect(']')
            node = new_unary(NodeKind.ND_DEREF, exp)
            continue
        elif tokenize.consume('.'):
            node = struct_ref(node)
            continue
        elif tokenize.consume('->'):
            node = new_unary(NodeKind.ND_DEREF, node)
            node = struct_ref(node)
            continue
        return node


# func-args = "(" (assign ("," assign)*)? ")"
def func_args():
    if tokenize.consume(')'):
        return None

    head = assign()
    cur = head

    while tokenize.consume(','):
        cur.next = assign()
        cur = cur.next

    tokenize.expect(')')
    return head


# primary = "(" expr ")" | "sizeof" unary | ident func-args? | str | num
# args = "(" ident ("," ident)* ")"
def primary():
    if tokenize.consume("("):
        node = expr()
        tokenize.expect(")")
        return node

    if tokenize.consume("sizeof"):
        node = unary()
        type.add_type(node)
        return new_num(node.ty.size)

    ident = tokenize.consume_ident()
    if ident is not None:
        # 函数调用
        if tokenize.consume('('):
            node = new_node(NodeKind.ND_FUNCALL)
            node.funcname = ident.str
            node.args = func_args()
            return node

        # 变量
        sc = find_var(ident)
        if sc is not None and sc.var is not None:
            return new_var_node(sc.var)
        else:
            raise RuntimeError("undefined variable: %s", ident.str)

    tok = tokenize.token
    if tok.kind == tokenize.TokenKind.TK_STR:
        tokenize.token = tokenize.token.next

        ty = type.array_of(type.char_type, tok.cont_len)
        var = new_gvar(new_label(), ty, True)
        var.contents = tok.contents
        var.cont_len = tok.cont_len
        return new_var_node(var, tok=tok)

    return new_num(tokenize.expect_number(), tok=tokenize.token)
