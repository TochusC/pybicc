from enum import Enum

from compiler import tokenize, type


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


locals = VarList()
globals = VarList()
scope = VarList()


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


def new_label():
    global cnt
    buf = ".L.data." + str(cnt)
    cnt += 1
    return buf


def find_var(tok=tokenize.token):
    var_list = scope
    while var_list is not None:
        var = var_list.var
        if var.name == tok.str:
            return var
        var_list = var_list.next


def new_var(name, ty, is_local):
    global scope

    var = Var()
    var.name = name
    var.ty = ty
    var.is_local = is_local

    sc = VarList()
    sc.var = var
    sc.next = scope
    scope = sc
    return var


def new_lvar(name, ty):
    global locals

    var = new_var(name, ty, True)

    vl = VarList()
    vl.var = var
    vl.next = locals
    locals = vl
    return var


def new_gvar(name, ty):
    global globals
    var = new_var(name, ty, False)

    vl = VarList()
    vl.var = var
    vl.next = globals
    globals = vl
    return var


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


def read_expr_stmt():
    return new_unary(NodeKind.ND_EXPR_STMT, expr(), tok=tokenize.token)


def read_type_suffix(base):
    if not tokenize.consume('['):
        return base
    sz = tokenize.expect_number()
    tokenize.expect(']')
    base = read_type_suffix(base)
    return type.array_of(base, sz)


def struct_decl():
    tokenize.expect("struct")
    tokenize.expect("{")

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
        mem.offset = offset
        offset += mem.ty.size
        mem = mem.next
    ty.size = offset

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
    new_gvar(name, ty)


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
            cur.next = function()
            cur = cur.next
        else:
            global_var()

    prog = Program()
    prog.globals = globals
    prog.fns = head.next

    return prog


# basetype =  ("char" | "int" | struct-decl) "*"*
def basetype():
    if not is_typename():
        raise RuntimeError("typename expected, but got %s", tokenize.token.str)
    if tokenize.consume('char'):
        ty = type.char_type
    elif tokenize.consume('int'):
        ty = type.int_type
    else:
        ty = struct_decl()

    while tokenize.consume('*'):
        ty = type.pointer_to(ty)
    return ty


# function = basetype ident "(" params? ")" "{" stmt* "}"
# params   = param ("," param)*
# param    = basetype ident
def function():
    global locals
    global scope

    locals = None

    basetype()
    fn = Function(name=tokenize.expect_ident())
    tokenize.expect('(')

    sc = scope
    fn.params = read_func_params()
    tokenize.expect('{')

    head = Node(NodeKind.ND_DEFAULT)
    cur = head

    while not tokenize.consume('}'):
        cur.next = stmt()
        cur = cur.next
    scope = sc

    fn.node = head.next
    fn.locals = locals

    return fn


# declaration = basetype ident ("[" num "]")* ("=" expr) ";"
def declaration():
    ty = basetype()
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
            or tokenize.peek("struct"))


def stmt():
    node = stmt2()
    type.add_type(node)
    return node


# stmt2 = "return" expr ";"
#      | "if" "(" expr ")" stmt ("else" stmt)?
#      | "while" "(" expr ")" stmt
#      | "for" "(" expr? ";" expr? ";" expr? ")" stmt
#      | "{" stmt* "}"
#      | expr ";"
def stmt2():
    global scope
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

        sc = scope
        while not tokenize.consume("}"):
            cur.next = stmt()
            cur = cur.next
        scope = sc

        node = new_node(NodeKind.ND_BLOCK)
        node.body = head.next

        return node

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


# mul = unary ("*" unary | "/" unary)*
def mul():
    node = unary()
    while True:
        if tokenize.consume("*"):
            node = new_binary(NodeKind.ND_MUL, node, unary(), tok=tokenize.token)
        elif tokenize.consume("/"):
            node = new_binary(NodeKind.ND_DIV, node, unary(), tok=tokenize.token)
        else:
            return node


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


# postfix = primary ("[" expr "]" | "." ident)*
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
        var = find_var(ident)
        if var is None:
            raise RuntimeError("undefined variable: %s", ident.str)
        return new_var_node(var)

    tok = tokenize.token
    if tok.kind == tokenize.TokenKind.TK_STR:
        tokenize.token = tokenize.token.next

        ty = type.array_of(type.char_type, tok.cont_len)
        var = new_gvar(new_label(), ty)
        var.contents = tok.contents
        var.cont_len = tok.cont_len
        return new_var_node(var, tok=tok)

    return new_num(tokenize.expect_number(), tok=tokenize.token)
