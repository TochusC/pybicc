"""
    Intel 80x86 模拟器
    用于模拟汇编代码的执行过程
"""
import struct
from enum import Enum

MEMORY_SIZE = 8196
CompileController = None


# 寻址模式
class AddressingMode(Enum):
    IMMEDIATE = 0
    REGISTER = 1
    MEMORY = 2


# 确定寻址模式
def addressing(source):
    """
    根据源操作数（source）的形式，确认源操作数的寻址模式
    :param source: 需要确定寻址模式的源操作数
    :return AddressingMode:  枚举类型的寻址模式
    """
    # 寄存器寻址模式
    if source in Register_Table:
        return AddressingMode.REGISTER

    # 内存寻址模式
    elif "[" in source and "]" in source:
        return AddressingMode.MEMORY

    # 立即数寻址模式
    else:
        return AddressingMode.IMMEDIATE

# 根据寻址模式获取操作数的值
def getValueByAddressing(AddressingMode, source):
    """
    根据寻址模式获取操作数的值
    :param AddressingMode: 寻址模式
    :param source: 源操作数
    :return value: 源操作数的值
    """
    if AddressingMode == AddressingMode.IMMEDIATE:
        try:
            return int(source)
        except ValueError:
           return source

    elif AddressingMode == AddressingMode.REGISTER:
        return Register_Table[source].get()

    elif AddressingMode == AddressingMode.MEMORY:
        raise RuntimeError("在不确定大小的情况下无法获取内存值")
    else:
        raise RuntimeError("无法识别的源操作数: %s" % source)



MAX_64BIT_INT = 0x7FFFFFFFFFFFFFFF


class Register:
    shared_storage = [0 for t in range(256)]

    def __init__(self, name, pos, size):
        self.name = name
        self.pos = pos
        self.size = size

    def insert(self, value):
        for i in range(self.size):
            self.shared_storage[self.pos + i] = (value >> (i * 8)) & 0xFF

    def get(self):
        value = 0
        for i in range(self.size):
            value += self.shared_storage[self.pos + i] << (i * 8)
        return value


Register_Table = {
    # 64bit寄存器
    "rax": Register("rax", 0, 8),
    "rsp": Register("rsp", 8, 8),
    "rbp": Register("rbp", 16, 8),
    "rdi": Register("rdi", 24, 8),
    "rsi": Register("rsi", 32, 8),
    "rdx": Register("rdx", 40, 8),
    "rcx": Register("rcx", 48, 8),
    "r8": Register("r8", 56, 8),
    "r9": Register("r9", 64, 8),
    "rbx": Register("rbx", 72, 8),
    "r10": Register("r10", 80, 8),
    "r11": Register("r11", 88, 8),
    "r12": Register("r12", 96, 8),
    "r13": Register("r13", 104, 8),
    "r14": Register("r14", 112, 8),
    "r15": Register("r15", 120, 8),

    # 32bit寄存器
    "eax": Register("eax", 0, 4),
    "esp": Register("esp", 8, 4),
    "ebp": Register("ebp", 16, 4),
    "edi": Register("edi", 24, 4),
    "esi": Register("esi", 32, 4),
    "edx": Register("edx", 40, 4),
    "ecx": Register("ecx", 48, 4),
    "r8d": Register("r8d", 56, 4),
    "r9d": Register("r9d", 64, 4),
    "ebx": Register("ebx", 72, 4),
    "r10d": Register("r10d", 80, 4),
    "r11d": Register("r11d", 88, 4),
    "r12d": Register("r12d", 96, 4),
    "r13d": Register("r13d", 104, 4),
    "r14d": Register("r14d", 112, 4),
    "r15d": Register("r15d", 120, 4),

    # 16bit寄存器
    "ax": Register("ax", 0, 2),
    "sp": Register("sp", 8, 2),
    "bp": Register("bp", 16, 2),
    "di": Register("di", 24, 2),
    "si": Register("si", 32, 2),
    "dx": Register("dx", 40, 2),
    "cx": Register("cx", 48, 2),
    "r8w": Register("r8w", 56, 2),
    "r9w": Register("r9w", 64, 2),
    "bx": Register("bx", 72, 2),
    "r10w": Register("r10w", 80, 2),
    "r11w": Register("r11w", 88, 2),
    "r12w": Register("r12w", 96, 2),
    "r13w": Register("r13w", 104, 2),
    "r14w": Register("r14w", 112, 2),
    "r15w": Register("r15w", 120, 2),

    # 8bit寄存器
    "al": Register("al", 0, 1),
    "spl": Register("spl", 8, 1),
    "bpl": Register("bpl", 16, 1),
    "dil": Register("dil", 24, 1),
    "sil": Register("sil", 32, 1),
    "dl": Register("dl", 40, 1),
    "cl": Register("cl", 48, 1),
    "r8b": Register("r8b", 56, 1),
    "r9b": Register("r9b", 64, 1),
    "bl": Register("bl", 72, 1),
    "r10b": Register("r10b", 80, 1),
    "r11b": Register("r11b", 88, 1),
    "r12b": Register("r12b", 96, 1),
    "r13b": Register("r13b", 104, 1),
    "r14b": Register("r14b", 112, 1),
    "r15b": Register("r15b", 120, 1),

    # 标志寄存器
    "CF": Register("CF", 128, 1),
    "OF": Register("OF", 129, 1),
    "SF": Register("SF", 130, 1),
    "ZF": Register("ZF", 131, 1),
}


class MemoryClass:
    storage = [0 for t in range(MEMORY_SIZE)]

    def insert(self, pos, value, size):
        if type(value) == int:
            for i in range(size):
                self.storage[pos + i] = (value >> (i * 8)) & 0xFF
        else:
            print("value:", value)

    def get(self, pos, size):
        value = 0
        for i in range(size):
            value += self.storage[pos + i] << (i * 8)
        return value

Memory = MemoryClass()

output = ''

function_entry_index_table = {}



def getMemoryAddress(src):
    class TokenKind(Enum):
        TK_RESERVED = 0
        TK_NUM = 1
        TK_REGISTER = 2
        TK_EOF = 3

    class Token:
        def __init__(self, kind, str, next):
            self.kind = kind
            self.str = str
            self.next = next

    class NodeKind(Enum):
        ND_REGISTER = 0
        ND_NUM = 1

        ND_ADD = 2
        ND_SUB = 3
        ND_MUL = 4
        ND_DIV = 5

    class Node:
        def __init__(self, kind, val, lhs, rhs):
            self.kind = kind
            self.val = val
            self.lhs = lhs
            self.rhs = rhs

    def eval(root):
        if root is None:
            return 0
        if root.kind == NodeKind.ND_NUM:
            return root.val
        elif root.kind == NodeKind.ND_REGISTER:
            return Register_Table[root.val].get()
        elif root.kind == NodeKind.ND_ADD:
            return eval(root.lhs) + eval(root.rhs)
        elif root.kind == NodeKind.ND_SUB:
            return eval(root.lhs) - eval(root.rhs)
        elif root.kind == NodeKind.ND_MUL:
            return eval(root.lhs) * eval(root.rhs)
        elif root.kind == NodeKind.ND_DIV:
            return eval(root.lhs) // eval(root.rhs)

    def tokenize():
        nonlocal expr
        pos = 0
        head = Token(TokenKind.TK_RESERVED, None, None)
        cur = head

        while pos < len(expr):
            if expr[pos] == ' ':
                pos += 1
                continue
            if expr[pos].isdigit():
                val = 0
                while pos < len(expr) and expr[pos].isdigit():
                    val = val * 10 + int(expr[pos])
                    pos += 1
                cur.next = Token(TokenKind.TK_NUM, val, None)
                cur = cur.next
            elif expr[pos].isalpha():
                val = ''
                while pos < len(expr) and expr[pos] not in operand:
                    val += expr[pos]
                    pos += 1
                cur.next = Token(TokenKind.TK_REGISTER, val, None)
                cur = cur.next
            elif expr[pos] in operand:
                cur.next = Token(TokenKind.TK_RESERVED, expr[pos], None)
                cur = cur.next
                pos += 1
            else:
                raise RuntimeError("无法识别的字符: %s" % expr[pos])
        return head.next

    # mul = primary ("*" primary | "/" primary)*
    def mul():
        nonlocal token
        node = primary()
        while token is not None:
            if token.str == "*":
                node = Node(NodeKind.ND_MUL, 0, node, primary())
                token = token.next

            elif token.str == "/":
                node = Node(NodeKind.ND_DIV, 0, node, primary())
                token = token.next
            else:
                return node
        return node

    # primary = num | register | "(" expr ")"
    def primary():
        nonlocal token
        if token.kind == TokenKind.TK_NUM:
            node = Node(NodeKind.ND_NUM, int(token.str), None, None)
            token = token.next
            return node
        elif token.kind == TokenKind.TK_REGISTER:
            node = Node(NodeKind.ND_REGISTER, token.str, None, None)
            token = token.next
            return node
        elif token.str == "(":
            token = token.next
            node = expr()
            if token.str != ")":
                raise RuntimeError("括号不匹配")
            token = token.next
            return node

    expr = src[1:-1]
    operand = ['+', '-', '*', '/', '(', ')']
    token = tokenize()
    # expr = mul ("+" mul | "-" mul)*
    root = mul()

    while token is not None:
        if token.str == "+":
            token = token.next
            root = Node(NodeKind.ND_ADD, 0, root, mul())
        elif token.str == "-":
            token = token.next
            root = Node(NodeKind.ND_SUB, 0, root, mul())
        else:
            raise RuntimeError("无法识别的字符: %s" % token.str)

    result = eval(root)
    return result


def float_to_ieee754(value):
    # 将浮点数解析为字节序列
    packed = struct.pack('>f', value)
    # 将字节序列转换为十六进制字符串
    return ''.join(['%02x' % b for b in packed])


def double_to_ieee754(value):
    # 将浮点数解析为字节序列
    packed = struct.pack('>d', value)
    # 将字节序列转换为十六进制字符串
    return ''.join(['%02x' % b for b in packed])


def ieee754_to_float(hex_str):
    # 将十六进制字符串转换为字节序列
    packed = bytes.fromhex(hex_str)
    # 将字节序列解析为浮点数
    return struct.unpack('>f', packed)[0]


def ieee754_to_double(ieee754_hex):
    # 将十六进制字符串转换为字节序列
    ieee754_bytes = bytes.fromhex(ieee754_hex)
    # 将字节序列解析为浮点数
    value = struct.unpack('>d', ieee754_bytes)[0]
    return value





RUNNING_COMMAND_LINE_INDEX = 0
CURRENT_FUNC = 'main'
PREV_FUNC = []


class Func:
    def __init__(self):
        self.labels = {}
        self.entry = None
        self.ret = None


class Vars:
    def __init__(self, name, size):
        self.pos = 0
        self.name = name
        self.size = size


glb_vars = {}
glb_func = {}

inset_func = {'read', 'write'}

glb_vars_size = 0

current_var = Vars('', 0)


def enterDataSegment(command_line_index, assembly_commands):
    """
    进入数据段，处理数据段的数据
    :param command_line_index:
    :param assembly_commands:
    :return:
    """
    global current_var, glb_vars_size, glb_vars

    while command_line_index < len(assembly_commands):
        command_line = assembly_commands[command_line_index]  # 获取当前行的汇编代码
        command_line_index += 1

        command_line = command_line.strip()  # 去掉行首行尾的空格

        if command_line == '.text':
            return command_line_index

        elif command_line[-1] == ':':
            current_var = Vars(command_line[:-1], 0)
            current_var.pos = glb_vars_size
            glb_vars[command_line[:-1]] = current_var

        elif command_line[0:5] == '.zero':
            command_segment = command_line.split(" ")
            glb_vars_size += int(command_segment[1])
            current_var.size += int(command_segment[1])

        elif command_line[0:5] == '.byte':
            command_segment = command_line.split(" ")
            Memory.insert(glb_vars_size, int(command_segment[1]), 1)
            current_var.size += 1
            glb_vars_size += 1


def init():
    Register_Table['rsp'].insert(MEMORY_SIZE)
    Register_Table['rbp'].insert(MEMORY_SIZE)


def run(code):
    """
      解释执行汇编代码
      :param code: 要执行的汇编代码
      :return: Nothing?
    """
    global output
    global glb_vars, glb_func
    global CURRENT_FUNC, RUNNING_COMMAND_LINE_INDEX
    global register

    init()

    output = ''

    assembly_commands = code.split("\n")  # 将汇编代码按行分割

    command_line_index = 0

    while command_line_index < len(assembly_commands):
        command_line = assembly_commands[command_line_index]  # 获取当前行的汇编代码

        command_line_index += 1  # 执行完一行代码后，指针指向下一行, 类似与PC寄存器

        if command_line == "":
            continue

        command_line = command_line.strip()  # 去掉行首行尾的空格

        if command_line[0] == '.':
            command_segment = command_line.split(" ")
            if command_segment[0] == ".intel_syntax":
                pass
            elif command_segment[0] == '.data':
                command_line_index = enterDataSegment(command_line_index, assembly_commands)
            elif command_segment[0] == '.text':
                pass
            elif command_segment[0] == '.global':
                pass

        elif command_line[-1] == ':':
            current_func = Func()
            glb_func[command_line[:-1]] = current_func
            current_func.entry = command_line_index
            while command_line_index < len(assembly_commands):
                command_line = assembly_commands[command_line_index]
                command = command_line.strip()
                if command[0:2] == '.L':
                    current_func.labels[command[:-1]] = command_line_index + 1
                elif command[0:3] == 'ret':
                    current_func.ret = command_line_index
                    break
                command_line_index += 1

    RUNNING_COMMAND_LINE_INDEX = glb_func[CURRENT_FUNC].entry
    while RUNNING_COMMAND_LINE_INDEX < len(assembly_commands):
        # 取完指令，RUNNING_COMMAND_LINE_INDEX自增
        command = assembly_commands[RUNNING_COMMAND_LINE_INDEX]
        RUNNING_COMMAND_LINE_INDEX += 1
        command = command.strip()
        # 运行指令
        run_command(command)


def run_command(command):
    """
    运行指令
    :param command:
    :return:
    """
    global output, register
    global CURRENT_FUNC, RUNNING_COMMAND_LINE_INDEX, PREV_FUNC
    # print("RUNNING INDEX: %d" % RUNNING_COMMAND_LINE_INDEX, "COMMAND: ", command) # DEBUG USE

    segment = command.split(" ")  # 将每行汇编代码按空格分割
    # push指令:将数据压入栈中 通用形式：push ( source | offset source )
    if segment[0] == "push":
        if len(segment) == 2:
            source = segment[1]

            addressing_mode = addressing(source)

            if addressing_mode == AddressingMode.MEMORY:
                source_value = Memory.get(getMemoryAddress(source), 8)
            else:
                source_value = getValueByAddressing(addressing_mode, source)

            rsp = Register_Table['rsp']
            value = rsp.get()
            value -= 8
            rsp.insert(value)

            stack_top = Register_Table['rsp'].get()
            Memory.insert(stack_top, source_value, 8)

        elif len(segment) == 3:
            if segment[1] == 'offset':
                var_name = segment[2]

                rsp = Register_Table['rsp']
                value = rsp.get()
                value -= 8
                rsp.insert(value)

                stack_top = Register_Table['rsp'].get()
                Memory.insert(stack_top, glb_vars[var_name].pos, 8)
        else:
            raise RuntimeError("push的参数量错误，共有%d个参数" % len(segment))

    # pop指令:将数据从栈中弹出 通用形式：pop destination
    elif segment[0] == "pop":
        if len(segment) == 2:
            destination = segment[1]
            addressing_mode = addressing(destination)

            if addressing_mode == AddressingMode.REGISTER:
                register = Register_Table[destination]

                stack_top = Register_Table['rsp'].get()
                # print("top index:", stack_top)
                register.insert(Memory.get(stack_top, register.size))

                Register_Table['rsp'].insert(stack_top + 8)
            elif addressing_mode == AddressingMode.MEMORY:
                raise RuntimeError("pop指令的目的操作数错误, %s" % destination)

            else:
                raise RuntimeError("pop指令的目的操作数错误, %s" % destination)

    # 加法指令add 通用形式：add destination, source
    elif segment[0] == "add":
        if len(segment) == 3:
            destination = segment[1][:-1]

            addressing_mode = addressing(destination)

            if addressing_mode != AddressingMode.REGISTER:
                raise RuntimeError("add指令的目的操作数错误, %s" % destination)

            source = segment[2]
            addressing_mode = addressing(source)

            source_value = getValueByAddressing(addressing_mode, source)

            register = Register_Table[destination]
            register.insert(register.get() + source_value)

        else:
            raise RuntimeError("add指令的参数量错误，共有%d个参数" % len(segment))

    # 减法指令sub 通用形式：sub destination, source
    elif segment[0] == "sub":
        if len(segment) == 3:
            destination = segment[1][:-1]

            addressing_mode = addressing(destination)

            if addressing_mode != AddressingMode.REGISTER:
                raise RuntimeError("sub指令的目的操作数错误, %s" % destination)

            source = segment[2]
            addressing_mode = addressing(source)

            source_value = getValueByAddressing(addressing_mode, source)

            register = Register_Table[destination]
            register.insert(register.get() - source_value)

        else:
            raise RuntimeError("sub指令的参数量错误，共有%d个参数" % len(segment))

    # 整数乘法指令imul 通用形式：imul destination, source
    elif segment[0] == "imul":
        if len(segment) == 3:
            destination = segment[1][:-1]

            addressing_mode = addressing(destination)

            if addressing_mode != AddressingMode.REGISTER:
                raise RuntimeError("imul指令的目的操作数错误, %s" % destination)

            source = segment[2]
            addressing_mode = addressing(source)

            source_value = getValueByAddressing(addressing_mode, source)

            register = Register_Table[destination]
            register.insert(register.get() * source_value)

        else:
            raise RuntimeError("imul指令的参数量错误，共有%d个参数" % len(segment))

    # 整数除法指令idiv 通用形式：idiv operand
    # idiv指令实现的有些粗糙，可能出现问题
    elif segment[0] == "idiv":
        if len(segment) == 2:
            operand = segment[1]
            addressing_mode = addressing(operand)

            if addressing_mode == AddressingMode.REGISTER:
                rax = Register_Table['rax']
                rdx = Register_Table['rdx']

                src = rax.get()

                rax.insert(src // getValueByAddressing(addressing_mode, operand))
                rdx.insert(src % getValueByAddressing(addressing_mode, operand))
            else:
                raise RuntimeError("idiv指令的源操作数错误, %s" % operand)

        else:
            raise RuntimeError("idiv指令的参数量错误，共有%d个参数" % len(segment))

    # cqo指令, 将rax的值扩展到rdx:rax中
    elif segment[0] == "cqo":
        if len(segment) == 1:
            pass
            # 将rax的值扩展到rdx:rax中
            # 模拟器还未模拟到如此深度，所以暂时不实现
        else:
            raise RuntimeError("cqo指令的参数量错误，共有%d个参数" % len(segment))

    # 比较指令cmp 通用形式：cmp operand1 operand2
    elif segment[0] == "cmp":
        if len(segment) == 3:

            operand1 = segment[1][:-1]
            operand2 = segment[2]

            operand1_addressing_mode = addressing(operand1)
            operand2_addressing_mode = addressing(operand2)

            operand1_value = getValueByAddressing(operand1_addressing_mode, operand1)
            operand2_value = getValueByAddressing(operand2_addressing_mode, operand2)

            cmp_result = operand1_value - operand2_value

            if cmp_result == 0:
                Register_Table['ZF'].insert(1)
            else:
                Register_Table['ZF'].insert(0)

            if cmp_result < 0:
                Register_Table['SF'].insert(1)
            else:
                Register_Table['SF'].insert(0)

            # TODO 溢出标志位实现不够完善
            if cmp_result > MAX_64BIT_INT or cmp_result < -MAX_64BIT_INT:
                Register_Table['OF'].insert(1)
            else:
                Register_Table['OF'].insert(0)

            if cmp_result > 0:
                Register_Table['CF'].insert(1)
            else:
                Register_Table['CF'].insert(0)

        else:
            raise RuntimeError("cmp指令的参数量错误，共有%d个参数" % len(segment))

    # 设置标志位指令sete 通用形式：sete destination
    elif segment[0] == "sete":
        if len(segment) == 2:
            destination = segment[1]
            addressing_mode = addressing(destination)

            if addressing_mode == AddressingMode.REGISTER:
                if Register_Table['ZF'].get() == 1:
                    Register_Table[destination].insert(1)
                else:
                    Register_Table[destination].insert(0)

            else:
                raise RuntimeError("sete指令的目的操作数错误, %s" % destination)

        else:
            raise RuntimeError("sete指令的参数量错误，共有%d个参数" % len(segment))

    # 设置标志位指令setne 通用形式：setne destination
    elif segment[0] == "setne":
        if len(segment) == 2:
            destination = segment[1]
            addressing_mode = addressing(destination)

            if addressing_mode == AddressingMode.REGISTER:
                if Register_Table['ZF'].get() == 0:
                    Register_Table[destination].insert(1)
                else:
                    Register_Table[destination].insert(0)

            else:
                raise RuntimeError("setne指令的目的操作数错误, %s" % destination)

        else:
            raise RuntimeError("setne指令的参数量错误，共有%d个参数" % len(segment))

    # 设置标志位指令setl 通用形式：setl destination
    elif segment[0] == "setl":
        if len(segment) == 2:
            destination = segment[1]
            addressing_mode = addressing(destination)

            if addressing_mode == AddressingMode.REGISTER:
                if Register_Table['SF'].get() != Register_Table['OF'].get():
                    Register_Table[destination].insert(1)
                else:
                    Register_Table[destination].insert(0)

            else:
                raise RuntimeError("setl指令的目的操作数错误, %s" % destination)

        else:
            raise RuntimeError("setl指令的参数量错误，共有%d个参数" % len(segment))

    # 设置标志位指令setle 通用形式：setle destination
    elif segment[0] == "setle":
        if len(segment) == 2:
            destination = segment[1]
            addressing_mode = addressing(destination)

            if addressing_mode == AddressingMode.REGISTER:
                if Register_Table['ZF'].get() == 1 or Register_Table['SF'].get() != Register_Table['OF'].get():
                    Register_Table[destination].insert(1)
                else:
                    Register_Table[destination].insert(0)

            else:
                raise RuntimeError("setle指令的目的操作数错误, %s" % destination)

        else:
            raise RuntimeError("setle指令的参数量错误，共有%d个参数" % len(segment))

    # movzb指令，用于将一个字节（8位）的无符号整数值零扩展并移动到指定寄存器。
    # movzb destination, source
    # "move zero-extend byte"。
    elif segment[0] == "movzb":
        if len(segment) == 3:

            destination = segment[1][:-1]

            addressing_mode = addressing(destination)

            if addressing_mode == AddressingMode.REGISTER:
                source = segment[2]
                addressing_mode = addressing(source)
                source_value = getValueByAddressing(addressing_mode, source)
                # TODO 0扩展 依照现在版本的模拟程度， 0扩展不需要实现

                Register_Table[destination].insert(source_value)

            else:
                raise RuntimeError("movzb指令的目的操作数错误, %s" % destination)

        else:
            raise RuntimeError("movzb指令的参数量错误，共有%d个参数" % len(segment))

    # movsx指令，用于将一个字节（8位）的有符号整数值符号扩展并移动到指定寄存器。
    # movsx destination, source
    elif segment[0] == "movsx":
        if len(segment) == 5:

            destination = segment[1][:-1]

            addressing_mode = addressing(destination)

            if addressing_mode == AddressingMode.REGISTER:
                source = segment[4]
                addressing_mode = addressing(source)
                if addressing_mode == AddressingMode.MEMORY:
                    source_value = Memory.get(getMemoryAddress(source), 1)
                else:
                    source_value = getValueByAddressing(addressing_mode, source)
                Register_Table[destination].insert(source_value)


            else:
                raise RuntimeError("movsb指令的目的操作数错误, %s" % destination)

        else:
            raise RuntimeError("movsb指令的参数量错误，共有%d个参数" % len(segment))
    # movss指令，用于将一个双字（32位）的单精度浮点数值移动到指定寄存器。
    # movss destination, source
    elif segment[0] == "movss":
        if len(segment) == 3:
            destination = segment[1][:-1]

            addressing_mode = addressing(destination)

            if addressing_mode == AddressingMode.REGISTER:
                source = segment[2]
                addressing_mode = addressing(source)
                source_value = getValueByAddressing(addressing_mode, source)

                Register_Table[destination].insert(source_value)
            else:
                raise RuntimeError("movss指令的目的操作数错误, %s" % destination)

        else:
            raise RuntimeError("movss指令的参数量错误，共有%d个参数" % len(segment))
    # movsd指令，用于将一个双字（32位）的双精度浮点数值移动到指定寄存器。
    elif segment[0] == "movsd":
        if len(segment) == 3:
            destination = segment[1][:-1]

            addressing_mode = addressing(destination)

            if addressing_mode == AddressingMode.REGISTER:
                source = segment[2]
                addressing_mode = addressing(source)
                source_value = getValueByAddressing(addressing_mode, source)

                Register_Table[destination].insert(source_value)
            else:
                raise RuntimeError("movsd指令的目的操作数错误, %s" % destination)

        else:
            raise RuntimeError("movsd指令的参数量错误，共有%d个参数" % len(segment))
    # movsxd指令，用于将一个双字（32位）的符号整数值符号扩展并移动到指定寄存器。
    elif segment[0] == "movsxd":
        if len(segment) == 5:

            destination = segment[1][:-1]

            addressing_mode = addressing(destination)

            if addressing_mode == AddressingMode.REGISTER:
                source = segment[4]
                addressing_mode = addressing(source)
                if addressing_mode == AddressingMode.MEMORY:
                    source_value = Memory.get(getMemoryAddress(source), 4)
                else:
                    source_value = getValueByAddressing(addressing_mode, source)
                # TODO 符号扩展 依照现在版本的模拟程度， 符号扩展不需要实现
                Register_Table[destination].insert(source_value)

            else:
                raise RuntimeError("movsxd指令的目的操作数错误, %s" % destination)

        else:
            raise RuntimeError("movsxd指令的参数量错误，共有%d个参数" % len(segment))

    # mov指令 mov dest src
    # 将ops的数据传给opd
    elif segment[0] == "mov":
        if len(segment) == 3:
            destination = segment[1][:-1]

            dest_addr_mode = addressing(destination)

            source = segment[2]
            src_addr_mode = addressing(source)

            if dest_addr_mode == AddressingMode.REGISTER:
                if src_addr_mode == AddressingMode.MEMORY:
                    register = Register_Table[destination]
                    Memory.get(getMemoryAddress(source), register.size)
                    register.insert(Memory.get(getMemoryAddress(source), register.size))
                else:
                    Register_Table[destination].insert(getValueByAddressing(src_addr_mode, source))
            elif dest_addr_mode == AddressingMode.MEMORY:
                if src_addr_mode == AddressingMode.REGISTER:
                    register = Register_Table[source]
                    Memory.insert(getMemoryAddress(destination), register.get(), register.size)
                else:
                    raise RuntimeError("mov指令的源操作数错误, %s" % source)
            else:
                raise RuntimeError("mov指令的目的操作数错误, %s" % destination)


    # lea指令 lea destination, source
    # 将source的地址计算结果传给destination，而不会访问source的值

    elif segment[0] == "lea":
        if len(segment) == 3:
            op_destination = segment[1][:-1]
            dest_addr_mode = addressing(op_destination)

            op_source = segment[2]
            src_addr_mode = addressing(op_source)

            if not dest_addr_mode == AddressingMode.REGISTER:
                raise RuntimeError("lea指令的目的操作数错误, %s" % op_destination)

            if src_addr_mode == AddressingMode.MEMORY:
                Register_Table[op_destination].insert(getMemoryAddress(op_source))
            else:
                raise RuntimeError("lea指令的源操作数错误, %s" % op_source)

    # and指令，and eax ebx
    # 逻辑与运算,结果赋值给eax
    elif segment[0] == 'and' or segment[0] == 'or':
        if len(segment) == 3:
            op_destination = segment[1][:-1]
            addressing_mode1 = addressing(op_destination)
            destination_value = getValueByAddressing(addressing_mode1, op_destination)

            op_source = segment[2]
            addressing_mode2 = addressing(op_source)
            source_value = getValueByAddressing(addressing_mode2, op_source)

            ret = 0
            if segment[0] == 'and':
                ret = destination_value & source_value
            else:
                ret = destination_value | source_value

            if addressing_mode1 == AddressingMode.REGISTER:
                Register_Table[op_destination].insert(ret)

            elif addressing_mode1 == AddressingMode.MEMORY:
                if addressing_mode2 == AddressingMode.REGISTER:
                    register = Register_Table[op_source]
                    Memory.insert(getMemoryAddress(op_destination), ret, register.size)
                else:
                    raise RuntimeError("and指令的源操作数错误, %s" % op_source)
    elif segment[0] == 'xor':
        if len(segment) == 3:
            op_destination = segment[1][:-1]
            addressing_mode1 = addressing(op_destination)
            destination_value = getValueByAddressing(addressing_mode1, op_destination)

            op_source = segment[2]
            addressing_mode2 = addressing(op_source)
            source_value = getValueByAddressing(addressing_mode2, op_source)

            ret = destination_value ^ source_value

            if addressing_mode1 == AddressingMode.REGISTER:
                Register_Table[op_destination].insert(ret)

            elif addressing_mode1 == AddressingMode.MEMORY:
                if addressing_mode2 == AddressingMode.REGISTER:
                    register = Register_Table[op_source]
                    Memory.insert(getMemoryAddress(op_destination), ret, register.size)
                else:
                    raise RuntimeError("xor指令的源操作数错误, %s" % op_source)
    elif segment[0] == 'not':
        if len(segment) == 2:
            op_destination = segment[1][:-1]
            addressing_mode1 = addressing(op_destination)
            destination_value = getValueByAddressing(addressing_mode1, op_destination)

            ret = ~destination_value

            if addressing_mode1 == AddressingMode.REGISTER:
                Register_Table[op_destination].insert(ret)

            elif addressing_mode1 == AddressingMode.MEMORY:
                raise RuntimeError("not指令的目的操作数错误, %s" % op_destination)
    elif segment[0] == "shl":
        if len(segment) == 3:
            destination = segment[1][:-1]

            addressing_mode = addressing(destination)

            if addressing_mode != AddressingMode.REGISTER:
                raise RuntimeError("shl指令的目的操作数错误, %s" % destination)

            source = segment[2]
            addressing_mode = addressing(source)

            source_value = getValueByAddressing(addressing_mode, source)

            Register_Table[destination].insert(Register_Table[destination].get() << source_value)

        else:
            raise RuntimeError("shl指令的参数量错误，共有%d个参数" % len(segment))
    elif segment[0] == "shr":
        if len(segment) == 3:
            destination = segment[1][:-1]

            addressing_mode = addressing(destination)

            if addressing_mode != AddressingMode.REGISTER:
                raise RuntimeError("shr指令的目的操作数错误, %s" % destination)

            source = segment[2]
            addressing_mode = addressing(source)

            source_value = getValueByAddressing(addressing_mode, source)

            Register_Table[destination].insert(Register_Table[destination].get() >> source_value)
        else:
            raise RuntimeError("shr指令的参数量错误，共有%d个参数" % len(segment))
    elif segment[0] == "sar":
        if len(segment) == 3:
            destination = segment[1][:-1]

            addressing_mode = addressing(destination)

            if addressing_mode != AddressingMode.REGISTER:
                raise RuntimeError("sar指令的目的操作数错误, %s" % destination)

            source = segment[2]
            addressing_mode = addressing(source)

            source_value = getValueByAddressing(addressing_mode, source)

            Register_Table[destination].insert(Register_Table[destination].get() >> source_value)
        else:
            raise RuntimeError("sar指令的参数量错误，共有%d个参数" % len(segment))
    elif segment[0] == "sal":
        if len(segment) == 3:
            destination = segment[1][:-1]

            addressing_mode = addressing(destination)

            if addressing_mode != AddressingMode.REGISTER:
                raise RuntimeError("sal指令的目的操作数错误, %s" % destination)

            source = segment[2]
            addressing_mode = addressing(source)

            source_value = getValueByAddressing(addressing_mode, source)

            Register_Table[destination].insert(Register_Table[destination].get() << source_value)
        else:
            raise RuntimeError("sal指令的参数量错误，共有%d个参数" % len(segment))
    # print指令，调试用。
    elif segment[0] == "print":
        output += "print rax value:" + str(Register_Table['rax'].get()) + "\n"
    elif segment[0] == "jmp":
        if len(segment) == 2:
            label = segment[1]
            if label in glb_func[CURRENT_FUNC].labels:
                RUNNING_COMMAND_LINE_INDEX = glb_func[CURRENT_FUNC].labels[label]
            else:
                raise RuntimeError("未找到标签: %s" % label)
        else:
            raise RuntimeError("jmp指令的参数量错误，共有%d个参数" % len(segment))
    elif segment[0] == "jnz":
        if len(segment) == 2:
            label = segment[1]
            if Register_Table['ZF'].get() == 0:
                if label in glb_func[CURRENT_FUNC].labels:
                    RUNNING_COMMAND_LINE_INDEX = glb_func[CURRENT_FUNC].labels[label]
                else:
                    raise RuntimeError("未找到标签: %s" % label)
        else:
            raise RuntimeError("jnz指令的参数量错误，共有%d个参数" % len(segment))
    elif segment[0] == "je":
        if len(segment) == 2:
            label = segment[1]
            if Register_Table['ZF'].get() == 1:
                if label in glb_func[CURRENT_FUNC].labels:
                    RUNNING_COMMAND_LINE_INDEX = glb_func[CURRENT_FUNC].labels[label]
                else:
                    raise RuntimeError("未找到标签: %s" % label)
        else:
            raise RuntimeError("je指令的参数量错误，共有%d个参数" % len(segment))
    elif segment[0] == "jne":
        if len(segment) == 2:
            label = segment[1]
            if Register_Table['ZF'].get() == 0:
                if label in glb_func[CURRENT_FUNC].labels:
                    RUNNING_COMMAND_LINE_INDEX = glb_func[CURRENT_FUNC].labels[label]
                else:
                    raise RuntimeError("未找到标签: %s" % label)
        else:
            raise RuntimeError("jne指令的参数量错误，共有%d个参数" % len(segment))
    elif segment[0] == "call":
        if len(segment) == 2:
            func_name = segment[1]
            if func_name in glb_func:
                PREV_FUNC.append({'func': CURRENT_FUNC, 'index': RUNNING_COMMAND_LINE_INDEX})
                CURRENT_FUNC = func_name
                RUNNING_COMMAND_LINE_INDEX = glb_func[CURRENT_FUNC].entry
            elif func_name in inset_func:
                if func_name == 'read':
                    if CompileController is not None:
                        addr = getMemoryAddress('[rdi]')
                        Memory.insert(addr, CompileController.request_input(), 8)
                    else:
                        addr = getMemoryAddress('[rdi]')
                        print("请求输入：")
                        userInput = input()
                        try:
                            if userInput.isdigit():
                                Memory.insert(addr, int(userInput), 8)
                            elif userInput[0:2] == '0x':
                                Memory.insert(addr, int(userInput, 16), 8)
                            elif '.' in userInput:
                                Memory.insert(addr, float(userInput), 8)
                            elif 'e' in userInput or 'E' in userInput:
                                Memory.insert(addr, float(userInput), 8)
                            elif 'f' in userInput:
                                Memory.insert(addr, float(userInput), 8)
                            elif 'd' in userInput:
                                Memory.insert(addr, float(userInput), 8)
                            elif userInput[0] == '0':
                                Memory.insert(addr, int(userInput, 8), 8)
                            elif userInput[0] == 'b':
                                Memory.insert(addr, int(userInput, 2), 8)
                            else:
                                Memory.insert(addr, int(userInput), 8)
                        except ValueError:
                            raise RuntimeError("无法识别的输入: %s" % userInput)
                elif func_name == 'write':
                    output += str(Register_Table['rdi'].get()) + '\n'
            else:
                raise RuntimeError("未找到函数: %s" % func_name)
        else:
            raise RuntimeError("call指令的参数量错误，共有%d个参数" % len(segment))
    # ret指令，用于从函数中返回 通用形式：ret
    elif segment[0] == "ret":
        if CURRENT_FUNC == 'main':
            output += "return value:" + str(Register_Table['rax'].get()) + "\n"
            RUNNING_COMMAND_LINE_INDEX = MAX_64BIT_INT
        else:
            return_info = PREV_FUNC.pop()
            CURRENT_FUNC = return_info['func']
            RUNNING_COMMAND_LINE_INDEX = return_info['index']
            # rax = register[register_index_table['rax']]
            # print("return value:", rax)
            # register = return_info['regs']
            # register[register_index_table['rax']]= rax
        # 调试用
    else:
        if not (segment[0] == "" or segment[0][0] == "."):
            # 空指令或标签跳过
            print("无法识别的指令: ", segment[0])


if __name__ == '__main__':
    Register_Table['rax'].insert(12)
    print(Register_Table['rax'].get())
