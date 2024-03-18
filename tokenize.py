from enum import Enum

"""
    词法分析生成Token
"""

token = None


class TokenKind(Enum):
    TK_RESERVED = 1  # Keywords or punctuators 关键字或者标点符号
    TK_NUM = 2  # Integer literals 整数字面量
    TK_EOF = 3  # End-of-file markers 文件结束标记
    TK_IDENT = 4  # Identifiers 标识符


class Token:
    kind = TokenKind  # Token kind 标记种类
    str = ""  # Token string Token字符串
    next = None  # Next token 下一个token

    def __init__(self, kind, str, next):
        self.kind = kind
        self.str = str
        self.next = next


def error(fmt, *args):
    print(fmt % args)


# Consumes the current token if it matches `op`.
# 如果当前的token匹配op，就消耗掉这个token，返回True
def consume(op):
    global token
    if token is None:
        return False
    # # 测试用
    # print("Got Token: ", token.kind, token.str)
    # print("Expected: ", TokenKind.TK_RESERVED, op)
    # print()

    if (token.kind != TokenKind.TK_RESERVED or token.str != op):
        return False
    token = token.next
    return True


def consume_ident():
    global token

    if token is None:
        return False

    if token.kind != TokenKind.TK_IDENT:
        return None

    ident = token
    token = token.next

    return ident


# Ensure that the current token is `op`.
# 确保当前的token是op
def expect(op):
    global token
    if token.kind != TokenKind.TK_RESERVED or token.str != op:
        error("Error: expected '%s', but got %s", op, token.str)
    token = token.next


# Ensure that the current token is TK_NUM.
# 确保当前的token是数字
def expect_number():
    global token
    if token.kind != TokenKind.TK_NUM:
        error("Error: expected a number, but got %s", token.str)
    val = token.str
    token = token.next
    return val


# 确保当前的Token为标识符
def expect_indent():
    global token
    if token.kind != TokenKind.TK_IDENT:
        error("Error: expected an identifier, but got %s", token.str)
    ident = token.str
    token = token.next
    return ident


def at_eof():
    global token
    if token is None:
        return True
    return token.kind == TokenKind.TK_EOF


def ispunct(c):
    return c in ['+', '-', '*', '/', '(', ')', '<', '>', '=',
                 '!', ';', '{', '}']


keywords = ["return", "if", "else", "while"]
ops = ["==", "!=", "<=", ">="]


def starts_with_reserved(p, raw):
    for keyword in keywords:
        if raw[p:p + len(keyword)] == keyword and not raw[p + len(keyword)].isalnum():
            return keyword, p + len(keyword)
    for op in ops:
        if raw[p:p + len(op)] == op:
            return op, p + len(op)
    return None, p


# Tokenize `raw` and returns new tokens.
# 对raw进行tokenize，返回生成的tokens
def tokenize(raw):
    p = 0
    head = Token(TokenKind.TK_RESERVED, None, None)
    cur = head
    while p < len(raw):
        # 空白字符
        if raw[p].isspace():
            p += 1
            continue

        # 关键字
        reserved, p = starts_with_reserved(p, raw)
        if reserved is not None:
            cur.next = Token(TokenKind.TK_RESERVED, reserved, None)
            cur = cur.next
            continue

        # 变量标识符
        if raw[p].isalpha():
            q = p
            while q < len(raw) and raw[q].isalnum():
                q += 1
            cur.next = Token(TokenKind.TK_IDENT, raw[p:q], None)
            cur = cur.next
            p = q
            continue

        # 单字符运算符
        if ispunct(raw[p]):
            cur.next = Token(TokenKind.TK_RESERVED, raw[p], None)
            cur = cur.next
            p += 1
            continue

        # 字面值常量
        if raw[p].isdigit():
            cur.next = Token(TokenKind.TK_NUM, raw[p], None)
            cur = cur.next
            p += 1
            while p < len(raw) and raw[p].isdigit():
                cur.str += raw[p]
                p += 1
            continue

        error("invalid token: %s", raw[p])
    cur.next = Token(TokenKind.TK_EOF, None, None)
    return head.next
