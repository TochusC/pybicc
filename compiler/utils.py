from compiler import parse


def align_to(n, align):
    """
    将n对齐到align
    :param n:
    :param align:
    :return:
    """
    return (n + align - 1) & ~(align - 1)


parse_result = ""


def save_parse_result(prog):
    global parse_result
    parse_result = ""

    glbs = prog.globals
    parse_result += "===全局变量===" + "\n"
    while glbs is not None:
        parse_result += "变量名:" + glbs.var.name + "大小:" + str(glbs.var.ty.size) + "offset:" + str(
            glbs.var.offset) + "\n"
        glbs = glbs.next
    parse_result += "===变量结束===" + "\n"

    fn = prog.fns
    while fn is not None:
        parse_result += "=====函数名:" + fn.name + "=====" + "\n"
        parse_result += "===函数参数===" + "\n"
        params = fn.params

        parse_result += "===局部变量===" + "\n"
        locals = fn.locals

        parse_result += "===函数语句===" + "\n"
        node = fn.node
        while node is not None:
            save_node_result(node)
            node = node.next
        parse_result += "=====函数结束======" + "\n"
        fn = fn.next


def save_node_result(node):
    global parse_result
    if node.kind == parse.NodeKind.ND_NUM:
        parse_result += str(node.val) + " "
    elif node.kind == parse.NodeKind.ND_VAR:
        parse_result += str(node.var.name) + " "
    elif node.kind == parse.NodeKind.ND_FUNCALL:
        parse_result += (str(node.kind) + " "
                         + str(node.funcname)) + "\n"
        parse_result += "==函数参数开始=="
        args = node.args
        while args is not None:
            save_node_result(args)
            args = args.next
        parse_result += "==函数参数结束==" + " "
    elif node.kind == parse.NodeKind.ND_IF:
        parse_result += "\n==条件开始==" + "\n"
        save_node_result(node.cond)
        parse_result += "==then开始==" + "\n"
        save_node_result(node.then)
        if node.els is not None:
            parse_result += "==else开始==" + "\n"
            save_node_result(node.els)
            parse_result += "==结束==" + " "
    elif node.kind == parse.NodeKind.ND_WHILE:
        parse_result += "==循环开始==" + "\n"
        parse_result += "\n==条件==" + "\n"
        save_node_result(node.cond)
        parse_result += "==循环体==" + "\n"
        save_node_result(node.then)
        parse_result += "==循环结束=="
    elif node.kind == parse.NodeKind.ND_FOR:
        parse_result += "==for循环开始==" + "\n"
        parse_result += "==初始化==" + "\n"
        save_node_result(node.init)
        parse_result += "==条件==" + "\n"
        save_node_result(node.cond)
        parse_result += "==递增==" + "\n"
        save_node_result(node.inc)
        parse_result += "==循环体==" + "\n"
        save_node_result(node.then)
        parse_result += "==for循环结束=="
    elif node.kind == parse.NodeKind.ND_BLOCK:
        parse_result += "==代码块开始==" + "\n"
        body = node.body
        while body is not None:
            save_node_result(body)
            body = body.next
        parse_result += "==代码块结束=="
    else:
        parse_result += str(node.kind) + " "

    parse_result += "\n"

    if node.lhs is not None:
        save_node_result(node.lhs)
    if node.rhs is not None:
        save_node_result(node.rhs)


tokenize_result = ""


def save_tokenize_result(token):
    global tokenize_result
    tokenize_result = ""
    while token.next is not None:
        tokenize_result += str(token.kind) + " " + str(token.str) + "\n"
        token = token.next


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
