from enum import Enum

from tokenize import consume, expect, expect_number, at_eof, consume_ident

prog = None

locals = None


class Var():
    next = None
    name = None
    offset = None

    def __init__(self, next, name, offset):
        self.next = next
        self.name = name
        self.offset = offset


class Function:
    next = None
    name = None
    node = None
    locals = None
    stack_size = None

    def __init__(self, next, name, node, locals, stack_size):
        self.next = next
        self.name = name
        self.node = node
        self.locals = locals
        self.stack_size = stack_size


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
    ND_WHILE = 15  # while 语句
    ND_FOR = 16  # for 语句
    ND_BLOCK = 17  # {}
    ND_DEFAULT = 18
    ND_FUNCALL = 19  # 函数调用


class Node:
    kind = NodeKind
    next = None
    lhs = None
    rhs = None
    val = None

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

    # 函数相关
    funcname = None
    args = None

    def __init__(self, kind, val=None, lhs=None, rhs=None, next=None,
                 var=None, cond=None, then=None, els=None):
        self.kind = kind
        self.lhs = lhs
        self.rhs = rhs
        self.val = val

        self.next = next

        self.var = var

        self.cond = cond
        self.then = then
        self.els = els


def find_var(tok):
    var = locals
    while var is not None:
        if var.name == tok.str:
            return var
    return None


def new_lvar(name):
    global locals
    var = Var(locals, name, None)
    locals = var
    return var


def new_node(kind):
    return Node(kind)


def new_binary(kind, lhs, rhs):
    return Node(kind, 0, lhs, rhs)


def new_unary(kind, lhs):
    return Node(kind, 0, lhs)


def new_num(val):
    return Node(NodeKind.ND_NUM, val)


# program = stmt*
def program():
    global locals
    locals = None

    head = Node(NodeKind.ND_ROOT)
    cur = head
    while True:
        if at_eof():
            break
        cur.next = stmt()
        cur = cur.next

    prog = Function(head.next, locals, None)
    return prog


def new_var_node(var):
    return Node(NodeKind.ND_VAR, var=var)


def read_expr_stmt():
    return new_unary(NodeKind.ND_EXPR_STMT, expr())


# stmt = "return" expr ";"
#      | "if" "(" expr ")" stmt ("else" stmt)?
#      | "while" "(" expr ")" stmt
#      | "for" "(" expr? ";" expr? ";" expr? ")" stmt
#      | "{" stmt* "}"
#      | expr ";"
def stmt():
    if consume("return"):
        node = new_unary(NodeKind.ND_RETURN, expr())
        expect(";")
        return node

    if consume("if"):
        node = new_node(NodeKind.ND_IF)
        expect("(")
        node.cond = expr()
        expect(")")
        node.then = stmt()
        if consume("else"):
            node.els = stmt()
        return node

    if consume("while"):
        node = new_node(NodeKind)
        expect("(")
        node.cond = expr()
        expect(")")
        node.then = stmt()
        return node

    if consume("for"):
        node = new_node(NodeKind.ND_FOR)
        expect("(")
        if not consume(";"):
            node.init = read_expr_stmt()
            expect(";")
        if not consume(";"):
            node.cond = expr()
            expect(";")
        if not consume(")"):
            node.inc = read_expr_stmt()
            expect(")")
        node.then = stmt()
        return node

    if consume("{"):
        head = new_node(NodeKind.ND_DEFAULT)
        cur = head

        while not consume("}"):
            cur.next = stmt()
            cur = cur.next

        node = new_node(NodeKind.ND_BLOCK)
        node.body = head.next

        return node

    node = read_expr_stmt()
    expect(";")
    return node


# expr = assign
def expr():
    return assign()


# assign = equality ("=" assign)?
def assign():
    node = equality()
    if consume("="):
        node = new_binary(NodeKind.ND_ASSIGN, node, assign())
    return node


# equality = relational ("==" relational | "!=" relational)*
def equality():
    node = relational()

    while True:
        if consume("=="):
            node = new_binary(NodeKind.ND_EQ, node, relational())
        elif consume("!="):
            node = new_binary(NodeKind.ND_NE, node, relational())
        else:
            return node


# relational = add ("<" add | "<=" add | ">" add | ">=" add)*
def relational():
    node = add()

    while True:
        if consume("<"):
            node = new_binary(NodeKind.ND_LT, node, add())
        elif consume("<="):
            node = new_binary(NodeKind.ND_LE, node, add())
        elif consume(">"):
            node = new_binary(NodeKind.ND_LT, add(), node)
        elif consume(">="):
            node = new_binary(NodeKind.ND_LE, add(), node)
        else:
            return node


# add = mul ("+" mul | "-" mul)*
def add():
    node = mul()

    while True:
        if consume("+"):
            node = new_binary(NodeKind.ND_ADD, node, mul())
        elif consume("-"):
            node = new_binary(NodeKind.ND_SUB, node, mul())
        else:
            return node


# mul = unary ("*" unary | "/" unary)*
def mul():
    node = unary()
    while True:
        if consume("*"):
            node = new_binary(NodeKind.ND_MUL, node, unary())
        elif consume("/"):
            node = new_binary(NodeKind.ND_DIV, node, unary())
        else:
            return node


# unary = ("+" | "-")? unary
#       | primary
def unary():
    if consume("+"):
        return unary()
    if consume("-"):
        return new_binary(NodeKind.ND_SUB, new_node(NodeKind.ND_NUM, 0), primary())
    return primary()

# func-args = "(" (assign ("," assign)*)? ")"
def func_args():
    if consume(')'):
        return None

    head = assign()
    cur = head

    while consume(','):
        cur.next = assign()
        cur = cur.next

    expect(')')
    return head


# primary = "(" expr ")" | ident args? | num
# args = "(" ")"
def primary():
    if consume("("):
        node = expr()
        expect(")")
        return node

    ident = consume_ident()
    if ident is not None:

        if consume('('):
            node = new_node(NodeKind.ND_FUNCALL)
            node.funcname = ident.str
            node.args = func_args()
            return node

        var = find_var(ident)
        if var is None:
            var = new_lvar(ident.str)
        return new_var_node(var)

    return new_num(expect_number())
