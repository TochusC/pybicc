import re
from PyQt6.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter


class CHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(CHighlighter, self).__init__(parent)

        self.highlight_rules = []

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = [
            "and", "as", "assert", "break", "class", "continue", "def",
            "del", "elif", "else", "except", "False", "finally", "for",
            "from", "global", "if", "import", "in", "is", "lambda", "None",
            "nonlocal", "not", "or", "pass", "raise", "return", "True",
            "try", "while", "with", "yield"
        ]
        self.highlight_rules.extend(
            [(re.compile(r"\b%s\b" % w), keyword_format) for w in keywords])

        quotation_format = QTextCharFormat()
        quotation_format.setForeground(QColor("#d7ba7d"))
        self.highlight_rules.append((re.compile("\".*\""), quotation_format))
        self.highlight_rules.append((re.compile("\'.*\'"), quotation_format))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self.highlight_rules.append((re.compile("#[^\n]*"), comment_format))

        # 添加规则：分号高亮
        semicolon_format = QTextCharFormat()
        semicolon_format.setForeground(QColor("#FF0000"))  # 使用红色
        self.highlight_rules.append((re.compile(";"), semicolon_format))

        # 添加规则：括号高亮
        bracket_format = QTextCharFormat()
        bracket_format.setForeground(QColor("#800080"))  # 使用紫色
        self.highlight_rules.append((re.compile("[\(\)\[\]\{\}]"), bracket_format))

        # 添加规则：数字高亮
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#008000"))  # 使用绿色
        self.highlight_rules.append((re.compile(r"\b\d+\b"), number_format))

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
