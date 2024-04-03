from enum import Enum

"""
    词法分析生成Token
"""

token = None


def ispunct(c):
    return c in ['+', '-', '*', '/', '(', ')', '<', '>', '=',
                 '!', '[', ']', ';', '{', '}', '&', ',', '.']


keywords = ["return", "if", "else", "while", "for",
            "int", "sizeof", "char", "struct", "typedef",]
ops = ["==", "!=", "<=", ">=", "->"]


class TokenKind(Enum):
    TK_RESERVED = 1  # Keywords or punctuators 关键字或者标点符号
    TK_NUM = 2  # Integer literals 整数字面量
    TK_EOF = 3  # End-of-file markers 文件结束标记
    TK_IDENT = 4  # Identifiers 标识符
    TK_STR = 5  # String literals 字符串字面值


class Token:
    kind = TokenKind  # Token kind 标记种类
    str = ""  # Token string Token字符串
    next = None  # Next token 下一个token

    contents = None
    cont_len = None

    def __init__(self, kind, str, next):
        self.kind = kind
        self.str = str
        self.next = next


# Consumes the current token if it matches `op`.
# 如果当前的token匹配op，就消耗掉这个token，返回True
def consume(op):
    global token
    if token is None:
        return None
    # # 测试用
    # print("Got Token: ", token.kind, token.str)
    # print("Expected: ", TokenKind.TK_RESERVED, op)
    # print()

    if token.kind != TokenKind.TK_RESERVED or token.str != op:
        return None

    t = token

    token = token.next
    return t


# 如果当前的token是op，返回token，否则返回None
def peek(s):
    global token
    if token.kind != TokenKind.TK_RESERVED or token.str != s:
        return None
    return token


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
    if peek(op) is None:
        raise RuntimeError("Error: expected '%s', but got '%s'" % (op, token.str))
    token = token.next


# Ensure that the current token is TK_NUM.
# 确保当前的token是数字
def expect_number():
    global token
    if token.kind != TokenKind.TK_NUM:
        raise RuntimeError("Error: expected a number, but got %s" % token.str)
    val = int(token.str)
    token = token.next
    return val


# 确保当前的Token为标识符
def expect_ident():
    global token
    if token.kind != TokenKind.TK_IDENT:
        raise RuntimeError("Error: expected an identifier, but got %s" % token.str)
    ident = token.str
    token = token.next
    return ident


def at_eof():
    global token
    if token is None:
        return True
    return token.kind == TokenKind.TK_EOF


def starts_with_reserved(p, raw):
    for keyword in keywords:
        if raw[p:p + len(keyword)] == keyword and not raw[p + len(keyword)].isalnum():
            return keyword, p + len(keyword)
    for op in ops:
        if raw[p:p + len(op)] == op:
            return op, p + len(op)
    return None, p


def get_escape_char(c):
    if c == 'a':
        return '\a'
    if c == 'b':
        return '\b'
    if c == 'f':
        return '\f'
    if c == 'n':
        return '\n'
    if c == 'r':
        return '\r'
    if c == 't':
        return '\t'
    if c == 'v':
        return '\v'
    if c == '"':
        return '"'
    if c == 'e':
        return 33
    if c == '0':
        return 0
    return c


def read_string_literal(raw, start):
    p = start
    q = p + 1
    buf = ''

    while q < len(raw):
        if raw[q] == '\0':
            raise RuntimeError("unclosed string")
        if raw[q] == '"':
            break
        if raw[q] == '\\':
            q += 2
            buf += get_escape_char(raw[p])
        else:
            buf += raw[q]
            q += 1

    tok = Token(TokenKind.TK_STR, raw[p + 1:q], None)
    tok.contents = raw[p + 1:q]
    tok.cont_len = q - p - 1

    return tok


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

        if raw[p:p+2] == '//':
            p += 2
            while raw[p] != '\n':
                p += 1
            continue

        if raw[p:p+2] == '/*':
            p += 2
            while raw[p:p + 2] != '*/':
                p += 1
            p += 2
            continue

        # 字符串字面值
        if raw[p] == '"':
            cur.next = read_string_literal(raw, p)
            cur = cur.next
            p += cur.cont_len + 2
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

        raise RuntimeError("invalid token: %s" % raw[p])
    cur.next = Token(TokenKind.TK_EOF, None, None)
    return head.next
