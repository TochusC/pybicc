from enum import Enum

token = None


class TokenKind(Enum):
    TK_RESERVED = 1  # Keywords or punctuators 关键字或者标点符号
    TK_NUM = 2  # Integer literals 整数字面量
    TK_EOF = 3  # End-of-file markers 文件结束标记


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
    # 测试用
    # print("Got Token: ", token.kind, token.str)
    # print("Expected: ", TokenKind.TK_RESERVED, op)
    # print()
    if (token.kind != TokenKind.TK_RESERVED or token.str != op):
        return False
    token = token.next
    return True


# Ensure that the current token is `op`.
# 确保当前的token是op
def expect(op):
    global token
    if (token.kind != TokenKind.TK_RESERVED or token.str != op):
        error("expected '%s'", op)
    token = token.next


# Ensure that the current token is TK_NUM.
# 确保当前的token是数字
def expect_number():
    global token
    if (token.kind != TokenKind.TK_NUM):
        error("expected a number, but got %s", token.str)
    val = token.str
    token = token.next
    return val


def at_eof():
    global token
    return token.kind == TokenKind.TK_EOF


def ispunct(c):
    return c in ['+', '-', '*', '/', '(', ')', '<', '>', '=', '!', ';']


# Tokenize `raw` and returns new tokens.
# 对raw进行tokenize，返回生成的tokens
def tokenize(raw):
    p = 0
    head = Token(TokenKind.TK_RESERVED, None, None)
    cur = head
    while p < len(raw):
        if raw[p].isspace():
            p += 1
            continue
        if raw[p:p + 2] == '==' or raw[p:p + 2] == '!=' or raw[p:p + 2] == '<=' or raw[p:p + 2] == '>=':
            cur.next = Token(TokenKind.TK_RESERVED, raw[p:p + 2], None)
            cur = cur.next
            p += 2
            continue
        if ispunct(raw[p]):
            cur.next = Token(TokenKind.TK_RESERVED, raw[p], None)
            cur = cur.next
            p += 1
            continue
        if raw[p].isdigit():
            cur.next = Token(TokenKind.TK_NUM, raw[p], None)
            cur = cur.next
            p += 1
            while p < len(raw) and raw[p].isdigit():
                cur.str += raw[p]
                p += 1
            continue

        error("invalid token %s", raw[p])
    cur.next = Token(TokenKind.TK_EOF, None, None)
    return head.next
