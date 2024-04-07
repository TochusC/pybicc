"""
    Intel 80x86 模拟器
    用于模拟汇编代码的执行过程
"""
import struct
from enum import Enum

MEMORY_SIZE = 1024

# 系统内存被分为栈和堆两部分，栈存放程序数据，堆存放操作系统。
# memory = [heap + stack]
# 堆位于内存底部，存储地址递增；栈位于内存顶部.存储地址递减

memory = [0 for t in range(MEMORY_SIZE)]  # 模拟内存


# 寻址模式
class AddressingMode(Enum):
    IMMEDIATE = 0
    REGISTER = 1
    MEMORY = 2


MAX_64BIT_INT = 0x7FFFFFFFFFFFFFFF

# 寄存器索引表
register = {
    # 64bit寄存器
    "rax": 0,  # 通常用于存放函数返回值
    "rsp": 0,  # 栈指针，指向栈顶，
    "rbp": 0,  # 栈基指针，指向栈底

    "rdi": 0,  # 函数参数1
    "rsi": 0,  # 函数参数2
    "rdx": 0,  # 函数参数3
    "rcx": 0,  # 函数参数4
    "r8": 0,  # 函数参数5
    "r9": 0,  # 函数参数6
    "rbx": 0,  # 好像是用于存储数据
    "r10": 0,  # r10~r15通常用于存放临时变量
    "r11": 0,
    "r12": 0,
    "r13": 0,
    "r14": 0,
    "r15": 0,

    # 32bit寄存器
    "eax": 0,
    "ebx": 0,
    "ecx": 0,
    "edx": 0,
    "esi": 0,
    "edi": 0,
    "esp": 0,
    "ebp": 0,
    "r8d": 0,
    "r9d": 0,
    "r10d": 0,
    "r11d": 0,
    "r12d": 0,
    "r13d": 0,
    "r14d": 0,
    "r15d": 0,

    # 16bit寄存器
    "ax": 0,
    "bx": 0,
    "cx": 0,
    "dx": 0,
    "si": 0,
    "di": 0,
    "sp": 0,
    "bp": 0,
    "r8w": 0,
    "r9w": 0,
    "r10w": 0,
    "r11w": 0,
    "r12w": 0,
    "r13w": 0,
    "r14w": 0,
    "r15w": 0,

    # 8bit寄存器
    "al": 0,
    "bl": 0,
    "cl": 0,
    "dl": 0,
    "sil": 0,
    "dil": 0,
    "spl": 0,
    "bpl": 0,
    "r8b": 0,
    "r9b": 0,
    "r10b": 0,
    "r11b": 0,
    "r12b": 0,
    "r13b": 0,
    "r14b": 0,
    "r15b": 0,

    # 标志寄存器
    "CF": 0,  # 进位标志
    "ZF": 0,  # 零标志
    "SF": 0,  # 符号标志
    "OF": 0,  # 溢出标志

    # 浮点寄存器
    "xmm0": 0,
}

output = ''

function_entry_index_table = {}


# 确定寻址模式
def addressing(source):
    """
    根据源操作数（source）的形式，确认源操作数的寻址模式
    :param source: 需要确定寻址模式的源操作数
    :return AddressingMode:  枚举类型的寻址模式
    """
    # 寄存器寻址模式
    if source in register:
        return AddressingMode.REGISTER

    # 内存寻址模式
    elif "[" in source and "]" in source:
        return AddressingMode.MEMORY

    # 立即数寻址模式
    else:
        return AddressingMode.IMMEDIATE


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
            return register[root.val]
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
            try:
                return ieee754_to_float(source)
            except Exception:
                try:
                    return ieee754_to_double(source)
                except Exception:
                    raise RuntimeError("无法识别的立即数: %s" % source)

    elif AddressingMode == AddressingMode.REGISTER:
        return register[source]

    elif AddressingMode == AddressingMode.MEMORY:
        return memory[getMemoryAddress(source)]
    else:
        raise RuntimeError("无法识别的源操作数: %s" % source)


RUNNING_COMMAND_LINE_INDEX = 0
CURRENT_FUNC = 'main'
PREV_FUNC = []


class Func:
    def __init__(self):
        self.labels = {}
        self.entry = None
        self.ret = None


class Vars:
    def __init__(self, name):
        self.pos = 0
        self.name = name


glb_vars = {}
glb_func = {}

glb_vars_size = 0

current_var = Vars('')


def enterDataSegment(command_line_index, assembly_commands):
    global current_var, glb_vars_size, glb_vars

    while command_line_index < len(assembly_commands):
        command_line = assembly_commands[command_line_index]  # 获取当前行的汇编代码
        command_line_index += 1

        command_line = command_line.strip()  # 去掉行首行尾的空格

        if command_line == '.text':
            return command_line_index

        elif command_line[-1] == ':':
            current_var = Vars(command_line[:-1])
            current_var.pos = glb_vars_size
            glb_vars[command_line[:-1]] = current_var

        elif command_line[0:5] == '.zero':
            command_segment = command_line.split(" ")
            glb_vars_size += int(command_segment[1])

        elif command_line[0:5] == '.byte':
            command_segment = command_line.split(" ")
            memory[glb_vars_size] = int(command_segment[1])
            glb_vars_size += 1


def run(code):
    """
      解释执行汇编代码
      :param code: 要执行的汇编代码
      :return: Nothing?
    """
    global output
    global glb_vars, glb_func
    global CURRENT_FUNC, RUNNING_COMMAND_LINE_INDEX

    output = ''

    assembly_commands = code.split("\n")  # 将汇编代码按行分割

    command_line_index = 0

    while command_line_index < len(assembly_commands):
        command_line = assembly_commands[command_line_index]  # 获取当前行的汇编代码

        command_line_index += 1  # 执行完一行代码后，指针指向下一行, 类似与PC寄存器 # TODO 改为使用PC寄存器进行模拟

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
    global output
    global CURRENT_FUNC, RUNNING_COMMAND_LINE_INDEX, PREV_FUNC
    # print("RUNNING INDEX: %d" % RUNNING_COMMAND_LINE_INDEX, "COMMAND: ", command) # DEBUG USE

    segment = command.split(" ")  # 将每行汇编代码按空格分割
    # push指令:将数据压入栈中 通用形式：push source
    if segment[0] == "push":
        if len(segment) == 2:
            source = segment[1]

            addressing_mode = addressing(source)

            source_value = getValueByAddressing(addressing_mode, source)

            register['rsp'] -= 8
            stack_top = register['rsp']
            memory[stack_top] = source_value
        elif len(segment) == 3:
            if segment[1] == 'offset':
                var_name = segment[2]

                register['rsp'] -= 8
                stack_top = register['rsp']
                memory[stack_top] = glb_vars[var_name].pos

        else:
            raise RuntimeError("push的参数量错误，共有%d个参数" % len(segment))

    # pop指令:将数据从栈中弹出 通用形式：pop destination
    elif segment[0] == "pop":
        if len(segment) == 2:
            destination = segment[1]
            addressing_mode = addressing(destination)

            if addressing_mode == AddressingMode.REGISTER:
                register_index = register[destination]

                stack_top = register['rsp']
                # print("top index:", stack_top)
                register[destination] = memory[stack_top]
                register['rsp'] += 8


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

            register[destination] += source_value

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

            register[destination] -= source_value

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

            register[destination] *= source_value

        else:
            raise RuntimeError("imul指令的参数量错误，共有%d个参数" % len(segment))

    # 整数除法指令idiv 通用形式：div operand
    # idiv指令实现的有些粗糙，可能出现问题
    elif segment[0] == "idiv":
        if len(segment) == 2:
            operand = segment[1]
            addressing_mode = addressing(operand)

            if addressing_mode == AddressingMode.REGISTER:
                register['rax'] = register['rax'] // register['operand']
                register['rdx'] = register['rax'] % register['operand']

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
                register['ZF'] = 1
            else:
                register['ZF'] = 0

            if cmp_result < 0:
                register['SF'] = 1
            else:
                register['SF'] = 0

            # TODO 溢出标志位实现不够完善
            if cmp_result > MAX_64BIT_INT or cmp_result < -MAX_64BIT_INT:
                register['OF'] = 1
            else:
                register['OF'] = 0

            if cmp_result > 0:
                register['CF'] = 1
            else:
                register['CF'] = 0

        else:
            raise RuntimeError("cmp指令的参数量错误，共有%d个参数" % len(segment))

    # 设置标志位指令sete 通用形式：sete destination
    elif segment[0] == "sete":
        if len(segment) == 2:
            destination = segment[1]
            addressing_mode = addressing(destination)

            if addressing_mode == AddressingMode.REGISTER:
                if register['ZF'] == 1:
                    register[destination] = 1
                else:
                    register[destination] = 0

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
                if register['ZF'] == 0:
                    register[destination] = 1
                else:
                    register[destination] = 0

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
                if register['SF'] != register['OF']:
                    register[destination] = 1
                else:
                    register[destination] = 0

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
                if register['ZF'] == 1 or register['SF'] != register['OF']:
                    register[destination] = 1
                else:
                    register[destination] = 0

            else:
                raise RuntimeError("setle指令的目的操作数错误, %s" % destination)

        else:
            raise RuntimeError("setle指令的参数量错误，共有%d个参数" % len(segment))

    # movzb指令，用于将一个字节（8位）的无符号整数值零扩展并移动到指定寄存器。
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

                register[destination] = source_value

            else:
                raise RuntimeError("movzb指令的目的操作数错误, %s" % destination)

        else:
            raise RuntimeError("movzb指令的参数量错误，共有%d个参数" % len(segment))

    # movsx指令，用于将一个字节（8位）的有符号整数值符号扩展并移动到指定寄存器。
    elif segment[0] == "movsx":
        if len(segment) == 5:

            destination = segment[1][:-1]

            addressing_mode = addressing(destination)

            if addressing_mode == AddressingMode.REGISTER:
                source = segment[4]
                addressing_mode = addressing(source)
                source_value = getValueByAddressing(addressing_mode, source)
                # TODO 符号扩展 依照现在版本的模拟程度， 符号扩展不需要实现

                register[destination] = source_value

            else:
                raise RuntimeError("movsb指令的目的操作数错误, %s" % destination)

        else:
            raise RuntimeError("movsb指令的参数量错误，共有%d个参数" % len(segment))
    # movss指令，用于将一个双字（32位）的单精度浮点数值移动到指定寄存器。
    elif segment[0] == "movss":
        if len(segment) == 3:
            destination = segment[1][:-1]

            addressing_mode = addressing(destination)

            if addressing_mode == AddressingMode.REGISTER:
                source = segment[2]
                addressing_mode = addressing(source)
                source_value = getValueByAddressing(addressing_mode, source)

                register[destination] = source_value

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

                register[destination] = source_value

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
                source_value = getValueByAddressing(addressing_mode, source)
                # TODO 符号扩展 依照现在版本的模拟程度， 符号扩展不需要实现
                register[destination] = source_value

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
                register[destination] = getValueByAddressing(src_addr_mode, source)
            elif dest_addr_mode == AddressingMode.MEMORY:
                memory[getMemoryAddress(destination)] = getValueByAddressing(src_addr_mode, source)
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
                register[op_destination] = getMemoryAddress(op_source)
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
                register[op_destination] = ret

            elif addressing_mode1 == AddressingMode.MEMORY:
                memory[getMemoryAddress(op_destination)] = ret
    # print指令，调试用。
    elif segment[0] == "print":
        output += "print rax value:" + str(register['rax']) + "\n"
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
            if register['ZF'] == 0:
                if label in glb_func[CURRENT_FUNC].labels:
                    RUNNING_COMMAND_LINE_INDEX = glb_func[CURRENT_FUNC].labels[label]
                else:
                    raise RuntimeError("未找到标签: %s" % label)
        else:
            raise RuntimeError("jnz指令的参数量错误，共有%d个参数" % len(segment))
    elif segment[0] == "je":
        if len(segment) == 2:
            label = segment[1]
            if register['ZF'] == 1:
                if label in glb_func[CURRENT_FUNC].labels:
                    RUNNING_COMMAND_LINE_INDEX = glb_func[CURRENT_FUNC].labels[label]
                else:
                    raise RuntimeError("未找到标签: %s" % label)
        else:
            raise RuntimeError("je指令的参数量错误，共有%d个参数" % len(segment))
    elif segment[0] == "jne":
        if len(segment) == 2:
            label = segment[1]
            if register['ZF'] == 0:
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
            else:
                raise RuntimeError("未找到函数: %s" % func_name)
        else:
            raise RuntimeError("call指令的参数量错误，共有%d个参数" % len(segment))
    # ret指令，用于从函数中返回 通用形式：ret
    elif segment[0] == "ret":
        if CURRENT_FUNC == 'main':
            output += "return value:" + str(register['rax']) + "\n"
            RUNNING_COMMAND_LINE_INDEX = MAX_64BIT_INT
        else:
            return_info = PREV_FUNC.pop()
            CURRENT_FUNC = return_info['func']
            RUNNING_COMMAND_LINE_INDEX = return_info['index']
    # 调试用
    else:
        if not (segment[0] == "" or segment[0][0] == "."):
            # 空指令或标签跳过
            print("无法识别的指令: ", segment[0])
