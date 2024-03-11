from enum import Enum

from tokenize import consume, expect, expect_number, at_eof, consume_ident

node = None


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


class Node:
    kind = NodeKind
    next = None
    lhs = None
    rhs = None
    val = None

    def __init__(self, kind, val=None, lhs=None, rhs=None, next=None):
        self.kind = kind
        self.lhs = lhs
        self.rhs = rhs
        self.val = val
        self.next = next


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
    head = Node(NodeKind.ND_ROOT)
    cur = head
    while True:
        if at_eof():
            break
        cur.next = stmt()
        cur = cur.next
    return head.next


def new_var_node(name):
    return Node(NodeKind.ND_VAR, name)


# stmt = "return" expr ";"
#      | expr ";"
def stmt():
    if consume("return"):
        node = new_unary(NodeKind.ND_RETURN, expr())
        expect(";")
        return node

    node = new_unary(NodeKind.ND_EXPR_STMT, expr())
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


# primary = "(" expr ")" | ident | num
def primary():
    if consume("("):
        node = expr()
        expect(")")
        return node

    ident = consume_ident()
    if ident is not None:
        return new_var_node(ident.str)

    return new_num(expect_number())
