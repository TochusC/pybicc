from enum import Enum

from tokenize import consume, expect, expect_number

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
    ND_NUM = 9


class Node:
    kind = NodeKind
    lhs = None
    rhs = None
    val = 0

    def __init__(self, kind, val=0, lhs=None, rhs=None):
        self.kind = kind
        self.lhs = lhs
        self.rhs = rhs
        self.val = val


def new_node(kind):
    return Node(kind)


def new_binary(kind, lhs, rhs):
    return Node(kind, 0, lhs, rhs)


def new_num(val):
    return Node(NodeKind.ND_NUM, val)


# expr = equality
def expr():
    return equality()


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
        return primary()
    if consume("-"):
        return new_binary(NodeKind.ND_SUB, new_node(NodeKind.ND_NUM, 0), primary())
    return primary()


# primary = "(" expr ")" | num
def primary():
    if consume("("):
        node = expr()
        expect(")")
        return node
    return new_num(expect_number())
