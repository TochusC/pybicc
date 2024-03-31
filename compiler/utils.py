from compiler import parse


def align_to(n, align):
    """
    将n对齐到align
    :param n:
    :param align:
    :return:
    """
    return (n + align - 1) & ~(align - 1)



def align_to(n, align):
    """
    将n对齐到align
    :param n:
    :param align:
    :return:
    """
    return (n + align - 1) & ~(align - 1)


# 前序遍历输出node，用于调试
def print_node(node):
    if node.kind == parse.NodeKind.ND_NUM:
        print(node.kind, node.val, end=' ')
    elif node.kind == parse.NodeKind.ND_VAR:
        print(node.kind, node.var.name, end=' ')

    elif node.kind == parse.NodeKind.ND_FUNCALL:
        print(node.kind, node.funcname, end='\n')
        args = node.args
        print("==函数参数开始==")
        while args is not None:
            print_node(args)
            args = args.next
        print("==函数参数结束==", end=" ")
    elif node.kind == parse.NodeKind.ND_IF:
        print(node.kind, end=" ")
        print("\n==条件==")
        print_node(node.cond)
        print("==then==")
        print_node(node.then)
        if node.els is not None:
            print("==else==")
            print_node(node.els)
        print("==结束==", end=" ")
    elif node.kind == parse.NodeKind.ND_WHILE:
        print(node.kind, end=" ")
        print("\n==条件==")
        print_node(node.cond)
        print("==then==")
        print_node(node.then)
        print("==结束==", end=" ")
    elif node.kind == parse.NodeKind.ND_FOR:
        print(node.kind, end=" ")
        print("\n==init==")
        print_node(node.init)
        print("==cond==")
        print_node(node.cond)
        print("==inc==")
        print_node(node.inc)
        print("==then==")
        print_node(node.then)
        print("==结束==", end=" ")
    elif node.kind == parse.NodeKind.ND_BLOCK:
        print(node.kind, end=" ")
        print("\n==block开始==")
        body = node.body
        while body is not None:
            print_node(body)
            body = body.next
        print("==block结束==", end=" ")
    else:
        print(node.kind, end=" ")

    print()

    if node.lhs is not None:
        print_node(node.lhs)
    if node.rhs is not None:
        print_node(node.rhs)

