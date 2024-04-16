import re
from PyQt6.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter


class CHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(CHighlighter, self).__init__(parent)

        self.highlight_rules = []

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keywords = [
            "auto", "break", "case", "char", "const", "continue", "default",
            "do", "double", "else", "enum", "extern", "float", "for",
            "goto.c", "if", "int", "long", "register", "return", "short",
            "signed", "sizeof", "static", "struct", "switch", "typedef",
            "union", "unsigned", "void", "volatile", "while"
        ]
        self.highlight_rules.extend(
            [(re.compile(r'\b%s\b' % w), keyword_format) for w in keywords])

        quotation_format = QTextCharFormat()
        quotation_format.setForeground(QColor("#d7ba7d"))
        self.highlight_rules.append((re.compile("\".*\""), quotation_format))
        self.highlight_rules.append((re.compile("\'.*\'"), quotation_format))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self.highlight_rules.append((re.compile(r'//[^\n]*'), comment_format))
        self.highlight_rules.append((re.compile(r'/\*.*\*/'), comment_format))

        semicolon_format = QTextCharFormat()
        semicolon_format.setForeground(QColor("#FF0000"))  # Red
        self.highlight_rules.append((re.compile(r';'), semicolon_format))

        bracket_format = QTextCharFormat()
        bracket_format.setForeground(QColor("#800080"))  # Purple
        self.highlight_rules.append((re.compile(r'[\(\)\[\]\{\}]'), bracket_format))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#008000"))  # Green
        self.highlight_rules.append((re.compile(r'\b\d+\b'), number_format))

        type_format = QTextCharFormat()
        type_format.setForeground(QColor("#B58900"))  # Orange
        types = [
            "char", "double", "float", "int", "long", "short", "signed",
            "unsigned", "void", "bool"
        ]
        self.highlight_rules.extend(
            [(re.compile(r'\b%s\b' % t), type_format) for t in types])

        struct_format = QTextCharFormat()
        struct_format.setForeground(QColor("#268BD2"))  # Blue
        self.highlight_rules.append((re.compile(r'\bstruct\b'), struct_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlight_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)


class AssemblyHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.highlight_rules = []

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))  # 设置颜色
        keyword_format.setFontWeight(QFont.Weight.Bold)  # 设置字体粗细
        keywords = [
            "mov", "add", "sub", "mul", "div", "inc", "dec",
            "jmp", "je", "jne", "jg", "jge", "jl", "jle", "call",
            "push", "pop", "cmp", "xor", "and", "or", "not"
            # 添加更多的关键字
        ]
        self.highlight_rules.extend(
            [(re.compile(r"\b%s\b" % w), keyword_format) for w in keywords])

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self.highlight_rules.append((re.compile(";[^\n]*"), comment_format))  # 注释

        label_format = QTextCharFormat()
        label_format.setForeground(QColor("#800080"))  # 设置颜色
        self.highlight_rules.append((re.compile(r"^[A-Za-z_][A-Za-z0-9_]*:"), label_format))  # 标签

    def highlightBlock(self, text):
        for pattern, format in self.highlight_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)


class TokenHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(TokenHighlighter, self).__init__(parent)

        self.highlight_rules = []

        # Define text formats for different token kinds
        formats = {
            'TK_RESERVED': QColor("#569CD6"),  # Reserved keywords
            'TK_IDENT': QColor("#d7ba7d"),  # Identifiers
            'TK_NUM': QColor("#008000"),  # Numbers
            'TK_COMMENT': QColor("#6A9955"),  # Comments
        }

        for kind, color in formats.items():
            format = QTextCharFormat()
            format.setForeground(color)
            self.highlight_rules.append((re.compile(kind), format))

    def highlightBlock(self, text):
        for pattern, format in self.highlight_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)


class NodeKind:
    # Define different node kinds
    ND_EXPR_STMT = "NodeKind.ND_EXPR_STMT"
    ND_ASSIGN = "NodeKind.ND_ASSIGN"
    ND_MEMBER = "NodeKind.ND_MEMBER"
    ND_DEREF = "NodeKind.ND_DEREF"
    ND_VAR = "NodeKind.ND_VAR"
    ND_NUM = "NodeKind.ND_NUM"
    ND_RETURN = "NodeKind.ND_RETURN"
    ND_PTR_DIFF = "NodeKind.ND_PTR_DIFF"
    ND_FUNCALL = "NodeKind.ND_FUNCALL"
    ND_ADDR = "NodeKind.ND_ADDR"
    ND_ADD = "NodeKind.ND_ADD"

class ParseHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(ParseHighlighter, self).__init__(parent)

        self.highlight_rules = []

        # Define text formats for different node kinds
        formats = {
            NodeKind.ND_EXPR_STMT: QColor("#FF5733"),
            NodeKind.ND_ASSIGN: QColor("#FFC300"),
            NodeKind.ND_MEMBER: QColor("#C70039"),
            NodeKind.ND_DEREF: QColor("#900C3F"),
            NodeKind.ND_VAR: QColor("#581845"),
            NodeKind.ND_NUM: QColor("#6A1B9A"),
            NodeKind.ND_RETURN: QColor("#1E8449"),
            NodeKind.ND_PTR_DIFF: QColor("#0E6655"),
            NodeKind.ND_FUNCALL: QColor("#2874A6"),
            NodeKind.ND_ADDR: QColor("#154360"),
            NodeKind.ND_ADD: QColor("#7D3C98"),
        }

        for kind, color in formats.items():
            format = QTextCharFormat()
            format.setForeground(color)
            self.highlight_rules.append((re.compile(kind), format))

    def highlightBlock(self, text):
        for pattern, format in self.highlight_rules:
            expression = pattern.search(text)
            while expression:
                start, end = expression.span()
                self.setFormat(start, end - start, format)
                expression = pattern.search(text, end)