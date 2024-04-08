from enum import Enum

from compiler import tokenize, type


class TagScope:
    next = None
    name = None
    ty = None
    depth = 0


class VarScope:
    next = None
    name = None
    depth = 0

    var = None
    typedef = None
    enum_ty = None
    enum_val = None


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

    ND_CAST = 27  # 类型转换
    ND_COMMA = 28  # 逗号表达式

    ND_PRE_INC = 29  # 前置++
    ND_PRE_DEC = 30  # 前置--
    ND_POST_INC = 31  # 后置++
    ND_POST_DEC = 32  # 后置--
    ND_ADD_EQ = 33  # +=
    ND_SUB_EQ = 34  # -=
    ND_MUL_EQ = 35  # *=
    ND_DIV_EQ = 36  # /=
    ND_PTR_ADD_EQ = 37  # +=
    ND_PTR_SUB_EQ = 38  # -=

    ND_NOT = 39  # !

    ND_BITNOT = 40  # ~
    ND_BITAND = 41  # &
    ND_BITOR = 42  # |
    ND_BITXOR = 43  # ^
    ND_LOGAND = 44  # &&
    ND_LOGOR = 45  # ||

    ND_SWITCH = 46  # switch
    ND_CASE = 47  # case
    ND_BREAK = 48  # break
    ND_CONTINUE = 49  # continue
    ND_GOTO = 50  # goto
    ND_LABEL = 51  # label

    ND_SHR = 52  # >>
    ND_SHL = 53  # <<
    ND_SHR_EQ = 54  # >>=
    ND_SHL_EQ = 55  # <<=


class Var:
    name = None  # 变量名
    offset = None  # 函数距离RBP的偏移量
    ty = None  # 类型
    is_local = None  # 是本地变量还是全局变量
    val = None  # 值

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
    is_static = False

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

    # {}
    body = None

    Member = None
    # 变量
    var = None

    # if, while, for 语句
    cond = None
    then = None
    els = None
    init = None
    inc = None

    # Goto 和 Label语句
    label_name = None

    case_next = None
    default_case = None
    case_label = 0
    case_end_label = 0

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
scope_depth = 0

current_switch = None


def enter_scope():
    global scope_depth
    sc = Scope()
    sc.var_scope = var_scope
    sc.tag_scope = tag_scope
    scope_depth += 1
    return sc


def leave_scope(sc):
    global var_scope, tag_scope, scope_depth
    var_scope = sc.var_scope
    tag_scope = sc.tag_scope
    scope_depth -= 1


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


def new_num():
    if tokenize.token.kind != tokenize.TokenKind.TK_NUM:
        raise RuntimeError("Error: expected a number, but got %s" % tokenize.token.str)
    if {'e', 'E', '.', 'f', "F"} & set(str(tokenize.token.str)):
        if 'f' in tokenize.token.str or 'F' in tokenize.token.str:
            node = Node(NodeKind.ND_NUM, val=float(tokenize.token.str[:-1]), tok=tokenize.token)
            node.ty = type.float_type
            tokenize.token = tokenize.token.next
            return node
        else:
            node = Node(NodeKind.ND_NUM, val=float(tokenize.token.str), tok=tokenize.token)
            node.ty = type.double_type
            tokenize.token = tokenize.token.next
            return node
    else:
        node = Node(NodeKind.ND_NUM, val=int(tokenize.token.str), tok=tokenize.token)
        tokenize.token = tokenize.token.next
        return node


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


# type-suffix = ("[" num? "]" type-suffix)?
def type_suffix(base):
    if not tokenize.consume('['):
        return base

    sz = 0
    is_incomplete = True

    if not tokenize.consume(']'):
        sz = tokenize.expect_number()
        is_incomplete = False
        tokenize.expect(']')

    ty = type_suffix(base)

    if ty.is_incomplete:
        raise RuntimeError("incomplete element type")

    ty = type.array_of(ty, sz)
    ty.is_incomplete = is_incomplete

    return type.array_of(base, sz)


def push_tag_scope(tok, ty):
    global tag_scope, scope_depth
    sc = TagScope()
    sc.next = tag_scope
    sc.name = tok.str
    sc.depth = scope_depth
    sc.ty = ty
    tag_scope = sc


# struct-decl = "struct" ident? ("{" struct-member "}")?
def struct_decl():
    tag = tokenize.consume_ident()

    if tag is not None and not tokenize.peek("{"):
        sc = find_tag(tag)
        if sc is None:
            ty = type.struct_type()
            push_tag_scope(tag, ty)
            return ty

        if sc.ty.kind != type.TypeKind.TY_STRUCT:
            raise RuntimeError("not a struct", tokenize.token)
        return sc.ty

    if not tokenize.consume("{"):
        return type.struct_type()

    sc = TagScope()

    if tag is not None:
        sc = find_tag(tag)

    if sc is not None and sc.depth == scope_depth:
        if sc.ty.kind != type.TypeKind.TY_STRUCT:
            raise RuntimeError("not a struct", tokenize.token)
        ty = sc.ty
    else:
        ty = type.struct_type()
        if tag is not None:
            push_tag_scope(tag, ty)

    # 读取结构体成员
    head = type.Member()
    cur = head

    while not tokenize.consume('}'):
        cur.next = struct_member()
        cur = cur.next

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
    ty.is_incomplete = False

    return ty


def union_decl():
    tag = tokenize.consume_ident()

    if tag is not None and not tokenize.peek("{"):
        sc = find_tag(tag)
        if sc is None:
            ty = type.struct_type()
            push_tag_scope(tag, ty)
            return ty

        if sc.ty.kind != type.TypeKind.TY_STRUCT:
            raise RuntimeError("not a struct", tokenize.token)
        return sc.ty

    if not tokenize.consume("{"):
        return type.struct_type()

    sc = TagScope()

    if tag is not None:
        sc = find_tag(tag)

    if sc is not None and sc.depth == scope_depth:
        if sc.ty.kind != type.TypeKind.TY_STRUCT:
            raise RuntimeError("not a struct", tokenize.token)
        ty = sc.ty
    else:
        ty = type.struct_type()
        if tag is not None:
            push_tag_scope(tag, ty)

    # 读取结构体成员
    head = type.Member()
    cur = head

    while not tokenize.consume('}'):
        cur.next = struct_member()
        cur = cur.next

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
    ty.is_incomplete = False
    return ty


def enum_specifier():
    ty = type.enum_type()
    tag = tokenize.consume_ident()
    if tag is not None and not tokenize.peek("{"):
        sc = find_tag(tag)
        if sc is None:
            raise RuntimeError("unknown enum type", tokenize.token)
        if sc.ty.kind != type.TypeKind.TY_ENUM:
            raise RuntimeError("not an enum type", tokenize.token)
        return sc.ty
    tokenize.expect("{")
    cnt = 0
    while not tokenize.consume("}"):
        name = tokenize.expect_ident()
        if tokenize.consume("="):
            cnt = tokenize.expect_number()
        sc = push_scope(name)
        sc.enum_ty = ty
        sc.enum_val = cnt
        cnt += 1
        if not tokenize.consume(","):
            tokenize.expect("}")
            break
    if tag is not None:
        push_tag_scope(tag, ty)
    return ty


def struct_member():
    mem = type.Member()
    mem.ty = basetype()
    mem.name = tokenize.expect_ident()
    mem.ty = type_suffix(mem.ty)
    tokenize.expect(';')
    return mem


def read_func_param():
    ty = basetype()
    name = tokenize.expect_ident()
    ty = type_suffix(ty)

    if ty.kind == type.TypeKind.TY_ARRAY:
        ty = type.pointer_to(ty.base)

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


def logor():
    node = logand()
    while tokenize.consume('||'):
        node = new_binary(NodeKind.ND_LOGOR, node, logand(), tokenize.token)
    return node


def logand():
    node = bitor()
    while tokenize.consume('&&'):
        node = new_binary(NodeKind.ND_LOGAND, node, bitor(), tokenize.token)
    return node


def bitor():
    node = bitxor()
    while tokenize.consume('|'):
        node = new_binary(NodeKind.ND_BITOR, node, bitxor(), tokenize.token)
    return node


def bitxor():
    node = bitand()
    while tokenize.consume('^'):
        node = new_binary(NodeKind.ND_BITXOR, node, bitxor(), tokenize.token)
    return node


def bitand():
    node = equality()
    while tokenize.consume('&'):
        node = new_binary(NodeKind.ND_BITAND, node, equality(), tokenize.token)
    return node


prog = None


def global_var():
    ty = basetype()
    name = tokenize.expect_ident()
    ty = type_suffix(ty)

    if tokenize.peek('='):
        tokenize.consume('=')
        new_gvar(name, ty, True)
        return

    tokenize.expect(';')
    new_gvar(name, ty, True)


# 决定最外层的是函数还是全局变量。
def is_function():
    tok = tokenize.token
    tokenize.consume('static')
    basetype()
    isfunc = tokenize.consume_ident() and tokenize.consume('(')
    tokenize.token = tok
    return isfunc


# program = (typedef | global-var | function | struct)*
def program():
    global globals
    head = Function()
    cur = head
    globals = None

    while True:
        if tokenize.at_eof():
            break
        if tokenize.consume('typedef'):
            ty = basetype()
            ty = type_suffix(ty)
            name = tokenize.expect_ident()

            push_scope(name)
            var_scope.typedef = ty

            tokenize.expect(';')

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


# basetype = builtin-type | struct-decl | typedef-name | enum-specifier  "*"*
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
    elif tokenize.consume('struct'):
        ty = struct_decl()
    elif tokenize.consume('union'):
        ty = union_decl()
    elif tokenize.consume('enum'):
        ty = enum_specifier()
    elif tokenize.consume('float'):
        ty = type.float_type
    elif tokenize.consume('double'):
        ty = type.double_type
    else:
        ty = find_var(tokenize.consume_ident())
        ty = ty.typedef
    if ty is None:
        raise RuntimeError("unknown type name", tokenize.token)

    while tokenize.consume('*'):
        ty = type.pointer_to(ty)
    return ty


# function = static? basetype declarator "(" params? ")" ("{" stmt* "}" | ";")
# params   = param ("," param)*
# param    = basetype ident
def function():
    global locals

    locals = None

    is_static = tokenize.consume('static')

    ty = basetype()
    fn = Function(name=tokenize.expect_ident())
    fn.is_static = is_static

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
    ty = type_suffix(ty)
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
            or tokenize.peek("enum")
            or tokenize.peek("union")
            or tokenize.peek("float")
            or tokenize.peek("double")
            or find_typedef(tokenize.token))


def stmt():
    node = stmt2()
    type.add_type(node)
    return node


# stmt2 = "return" expr ";"
#      | "if" "(" expr ")" stmt ("else" stmt)?
#      | "switch" "(" expr ")" stmt
#      | "case" num ":" stmt
#      | "default" ":" stmt
#      | "while" "(" expr ")" stmt
#      | "for" "(" (expr? ";" | declaration) expr? ";" expr? ")" stmt
#      | "{" stmt* "}"
#      | "typedef" basetype ident ("[" num "]")* ";"
#      | "break" ";"
#      | "continue" ";"
#      | "goto" ident ";"
#      | ident ":" stmt
#      | declaration
#      | expr ";"
def stmt2():
    global current_switch

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

    if tokenize.consume("switch"):
        node = new_node(NodeKind.ND_SWITCH)
        tokenize.expect("(")
        node.cond = expr()

        tokenize.expect(")")

        sw = current_switch
        current_switch = node
        node.then = stmt()
        current_switch = sw
        return node

    if tokenize.consume("case"):
        if current_switch is None:
            raise RuntimeError("stray case", tokenize.token)
        val = tokenize.expect_number()
        tokenize.expect(":")
        node = new_unary(NodeKind.ND_CASE, stmt())
        node.val = val
        node.case_next = current_switch.case_next
        current_switch.case_next = node
        return node

    if tokenize.consume("default"):
        if current_switch is None:
            raise RuntimeError("stray default", tokenize.token)
        tokenize.expect(":")

        node = new_node(NodeKind.ND_DEFAULT, stmt())
        current_switch.default_case = node
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
        sc = enter_scope()
        if not tokenize.consume(";"):
            if is_typename():
                node.init = declaration()
            else:
                node.init = read_expr_stmt()
                tokenize.expect(";")
        if not tokenize.consume(";"):
            node.cond = expr()
            tokenize.expect(";")
        if not tokenize.consume(")"):
            node.inc = read_expr_stmt()
            tokenize.expect(")")
        node.then = stmt()

        leave_scope(sc)
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
        ty = type_suffix(ty)
        tokenize.expect(";")
        sc = push_scope(name)
        sc.typedef = ty
        return new_node(NodeKind.ND_NULL)

    if is_typename():
        return declaration()

    if tokenize.consume("break"):
        tokenize.expect(";")
        return new_node(NodeKind.ND_BREAK)

    if tokenize.consume("continue"):
        tokenize.expect(";")
        return new_node(NodeKind.ND_CONTINUE)

    if tokenize.consume("goto"):
        node = new_node(NodeKind.ND_GOTO)
        node.label_name = tokenize.expect_ident()
        tokenize.expect(";")
        return node

    tok = tokenize.token
    name = tokenize.consume_ident()
    if name is not None:
        if tokenize.consume(":"):
            node = new_unary(NodeKind.ND_LABEL, stmt())
            node.label_name = name.strFc
            return node
        tokenize.token = tok

    node = read_expr_stmt()
    tokenize.expect(";")
    return node


# expr = assign ("," assign)*
def expr():
    node = assign()
    while tokenize.consume(","):
        node = new_unary(NodeKind.ND_EXPR_STMT, node)
        node = new_binary(NodeKind.ND_COMMA, node, assign())
    return node


# assign    = logor (assign-op assign)?
# assign-op = "=" | "+=" | "-=" | "*=" | "/=" | "<<=" | ">>="
def assign():
    node = logor()
    if tokenize.consume("="):
        return new_binary(NodeKind.ND_ASSIGN, node, assign(), tok=tokenize.token)
    if tokenize.consume("*="):
        return new_binary(NodeKind.ND_MUL_EQ, node, assign(), tok=tokenize.token)
    if tokenize.consume("/="):
        return new_binary(NodeKind.ND_DIV_EQ, node, assign(), tok=tokenize.token)
    if tokenize.consume("<<="):
        return new_binary(NodeKind.ND_SHL_EQ, node, assign(), tok=tokenize.token)
    if tokenize.consume(">>="):
        return new_binary(NodeKind.ND_SHR_EQ, node, assign(), tok=tokenize.token)
    if tokenize.consume("+="):
        type.add_type(node)
        if node.ty.base is not None:
            return new_binary(NodeKind.ND_PTR_ADD_EQ, node, assign(), tok=tokenize.token)
        return new_binary(NodeKind.ND_ADD_EQ, node, assign(), tok=tokenize.token)
    if tokenize.consume("-="):
        type.add_type(node)
        if node.ty.base is not None:
            return new_binary(NodeKind.ND_PTR_SUB_EQ, node, assign(), tok=tokenize.token)
        return new_binary(NodeKind.ND_SUB_EQ, node, assign(), tok=tokenize.token)
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


# relational = shift ("<" shift | "<=" shift | ">" shift | ">=" shift)*
def relational():
    node = shift()

    while True:
        if tokenize.consume("<"):
            node = new_binary(NodeKind.ND_LT, node, shift(), tok=tokenize.token)
        elif tokenize.consume("<="):
            node = new_binary(NodeKind.ND_LE, node, shift(), tok=tokenize.token)
        elif tokenize.consume(">"):
            node = new_binary(NodeKind.ND_LT, shift(), node, tok=tokenize.token)
        elif tokenize.consume(">="):
            node = new_binary(NodeKind.ND_LE, shift(), node, tok=tokenize.token)
        else:
            return node


# shift = add ("<<" add | ">>" add)*
def shift():
    node = add()

    while True:
        if tokenize.consume("<<"):
            node = new_binary(NodeKind.ND_SHL, node, add(), tok=tokenize.token)
        elif tokenize.consume(">>"):
            node = new_binary(NodeKind.ND_SHR, node, add(), tok=tokenize.token)
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
        raise RuntimeError("invalid operands, %s", tok.str)


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


# unary = ("+" | "-" | "*" | "&" | "!")? cast
# | ("++" | "--") unary
# | postfix
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
    if tokenize.consume("!"):
        return new_unary(NodeKind.ND_NOT, unary())
    if tokenize.consume("++"):
        return new_unary(NodeKind.ND_PRE_INC, unary())
    if tokenize.consume("--"):
        return new_unary(NodeKind.ND_PRE_DEC, unary())

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


# postfix = primary ("[" expr "]" | "." ident | "->" ident | "++" | "--")*
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
        elif tokenize.consume("++"):
            node = new_unary(NodeKind.ND_POST_INC, node)
            continue
        elif tokenize.consume("--"):
            node = new_unary(NodeKind.ND_POST_DEC, node)
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


# primary = "(" expr ")"
#         | "sizeof" unary
#         | ident func-args?
#         | str
#         | num
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
        if sc is not None:
            if sc.var is not None:
                return new_var_node(sc.var, tok=ident)
            elif sc.enum_ty is not None:
                return new_num(sc.enum_val, tok=ident)
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

    return new_num()
