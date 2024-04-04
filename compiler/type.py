from enum import Enum
from compiler import parse


class TypeKind(Enum):
    TY_INT = 1
    TY_PTR = 2
    TY_ARRAY = 3
    TY_CHAR = 4
    TY_STRUCT = 5
    TY_SHORT = 6
    TY_LONG = 7
    TY_FUNC = 8
    TY_VOID = 9
    TY_BOOL = 10
    TY_ENUM = 11


class Member:
    def __init__(self):
        self.name = None
        self.ty = None
        self.offset = None
        self.next = None



class Type:
    kind = None
    size = None
    base = None
    array_len = None
    members = None
    return_ty = None

    def __init__(self, kind=None, size=None, base=None, array_len=None, align=0):
        self.kind = kind
        self.size = size
        self.base = base
        self.align = align
        self.array_len = array_len


void_type = Type(kind=TypeKind.TY_VOID, size=1, align=1)
bool_type = Type(kind=TypeKind.TY_BOOL, size=1, align=1)
char_type = Type(kind=TypeKind.TY_CHAR, size=1, align=1)
int_type = Type(kind=TypeKind.TY_INT, size=4, align=4)
short_type = Type(kind=TypeKind.TY_SHORT, size=2, align=2)
long_type = Type(kind=TypeKind.TY_LONG, size=8, align=8)

def is_integer(ty):
    kd = ty.kind
    return kd in [TypeKind.TY_INT, TypeKind.TY_CHAR, TypeKind.TY_BOOL,
                  TypeKind.TY_SHORT, TypeKind.TY_LONG]

def enum_type():
    ty = new_type(TypeKind.TY_ENUM, 4, 4)
    return ty

def align_to(n, align):
    """
    将n对齐到align
    :param n:
    :param align:
    :return:
    """
    return (n + align - 1) & ~(align - 1)


def align_to(n, align):
    return (n + align - 1) & ~(align - 1)

def new_type(kind, size, align):
    ty = Type()
    ty.kind = kind
    ty.size = size
    ty.align = align
    return ty

def pointer_to(base):
    ty = new_type(TypeKind.TY_PTR, 8, 8)
    return ty


def func_type(return_ty):
    ty = new_type(TypeKind.TY_FUNC, 1, 1)
    ty.return_ty = return_ty
    return ty

def add_type(node):
    if node is None or node.ty is not None:
        return
    add_type(node.lhs)
    add_type(node.rhs)
    add_type(node.cond)
    add_type(node.then)
    add_type(node.els)
    add_type(node.init)
    add_type(node.inc)

    body = node.body
    while body is not None:
        add_type(body)
        body = body.next

    arg = node.args
    while arg is not None:
        add_type(arg)
        arg = arg.next

    if node.kind in [
        parse.NodeKind.ND_ADD,
        parse.NodeKind.ND_SUB,
        parse.NodeKind.ND_PTR_DIFF,
        parse.NodeKind.ND_MUL,
        parse.NodeKind.ND_DIV,
        parse.NodeKind.ND_EQ,
        parse.NodeKind.ND_NE,
        parse.NodeKind.ND_LT,
        parse.NodeKind.ND_LE,
        parse.NodeKind.ND_FUNCALL,
        parse.NodeKind.ND_NUM,
    ]:
        node.ty = long_type
        return
    elif node.kind in [
        parse.NodeKind.ND_PTR_ADD,
        parse.NodeKind.ND_PTR_SUB,
        parse.NodeKind.ND_ASSIGN,
    ]:
        node.ty = node.lhs.ty
        return
    elif node.kind == parse.NodeKind.ND_VAR:
        node.ty = node.var.ty
        return
    elif node.kind == parse.NodeKind.ND_COMMA:
        node.ty = node.rhs.ty
        return
    elif node.kind == parse.NodeKind.ND_MEMBER:
        node.ty = node.member.ty
        return
    elif node.kind == parse.NodeKind.ND_ADDR:
        if node.lhs.ty.kind == TypeKind.TY_ARRAY:
            node.ty = pointer_to(node.lhs.ty.base)
        else:
            node.ty = pointer_to(node.lhs.ty)
        return
    elif node.kind == parse.NodeKind.ND_DEREF:
        if node.lhs.ty.base is None:
            raise RuntimeError("invalid pointer dereference", node.lhs.ty)
        node.ty = node.lhs.ty.base
        if node.ty.kind == TypeKind.TY_VOID:
            raise RuntimeError("dereferencing a void pointer")
        return


def array_of(base, length):
    ty = new_type(TypeKind.TY_ARRAY, base.size * length, base.align)
    ty.base = base
    ty.array_len = length
    return ty
