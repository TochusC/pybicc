from enum import Enum
import parse


class TypeKind(Enum):
    TY_INT = 1
    TY_PTR = 2
    TY_ARRAY = 3


class Type:
    kind = None
    size = None
    base = None
    array_len = None


def is_integer(ty):
    if ty.kind == TypeKind.TY_INT:
        return True
    else:
        return False


def pointer_to(base):
    ty = Type()
    ty.kind = TypeKind.TY_PTR
    ty.size = 8
    ty.base = base
    return ty


def add_type(node):
    if node is None or node.kind is None:
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
        parse.NodeKind.ND_VAR,
        parse.NodeKind.ND_FUNCALL,
        parse.NodeKind.ND_NUM,
    ]:
        node.ty = Type()
        node.ty.kind = TypeKind.TY_INT
        return
    elif node.kind in [
        parse.NodeKind.ND_PTR_ADD,
        parse.NodeKind.ND_PTR_SUB,
        parse.NodeKind.ND_ASSIGN,
    ]:
        node.ty = node.lhs.ty
        return
    elif node.kind == parse.NodeKind.ND_ADDR:
        node.ty = pointer_to(node.lhs.ty)
        return
    elif node.kind == parse.NodeKind.ND_DEREF:
        if node.lhs.ty.kind == TypeKind.TY_PTR:
            node.ty = node.lhs.ty.base
        else:
            node.ty = TypeKind.TY_INT
        return


def array_of(base, length):
    ty = Type
    ty.kind = TypeKind.TY_ARRAY
    ty.size = base.size * length
    ty.base = base
    ty.array_len = length
    return ty
