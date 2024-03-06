"""
    Intel 80x86 模拟器
    用于模拟汇编代码的执行过程
"""
from enum import Enum

# 系统内存被分为栈和堆两部分，栈存放程序数据，堆存放操作系统。
# memory = [heap + stack]
# 堆位于内存底部，存储地址递增；栈位于内存顶部.存储地址递减
stack = []  # 模拟栈

register = [0 for i in range(64)]  # 模拟寄存器


# 寻址模式
class AddressingMode(Enum):
    IMMEDIATE = 0
    REGISTER = 1
    MEMORY = 2


MAX_64BIT_INT = 0x7FFFFFFFFFFFFFFF

# 寄存器索引表
register_index_table = {
    # 64bit寄存器
    "rax": 0,  # 通常用于存放函数返回值
    "rsp": 1,  # 栈指针，指向栈顶
    "rdi": 2,  # 函数参数1
    "rsi": 3,  # 函数参数2
    "rdx": 4,  # 函数参数3
    "rcx": 5,  # 函数参数4
    "r8": 6,  # 函数参数5
    "r9": 7,  # 函数参数6
    "rbx": 8,  # 好像是用于存储数据
    "rbp": 9,  # 栈基指针，指向栈底
    "r10": 10,  # r10~r15通常用于存放临时变量
    "r11": 11,
    "r12": 12,
    "r13": 13,
    "r14": 14,
    "r15": 15,

    # 32bit寄存器
    "eax": 16,
    "ebx": 17,
    "ecx": 18,
    "edx": 19,
    "esi": 20,
    "edi": 21,
    "esp": 22,
    "ebp": 23,
    "r8d": 24,
    "r9d": 25,
    "r10d": 26,
    "r11d": 27,
    "r12d": 28,
    "r13d": 29,
    "r14d": 30,
    "r15d": 31,

    # 16bit寄存器
    "ax": 32,
    "bx": 33,
    "cx": 34,
    "dx": 35,
    "si": 36,
    "di": 37,
    "sp": 38,
    "bp": 39,
    "r8w": 40,
    "r9w": 41,
    "r10w": 42,
    "r11w": 43,
    "r12w": 44,
    "r13w": 45,
    "r14w": 46,
    "r15w": 47,

    # 8bit寄存器
    "al": 48,
    "bl": 49,
    "cl": 50,
    "dl": 51,
    "sil": 52,
    "dil": 53,
    "spl": 54,
    "bpl": 55,
    "r8b": 56,
    "r9b": 57,
    "r10b": 58,
    "r11b": 59,
    "r12b": 60,
    "r13b": 61,
    "r14b": 62,
    "r15b": 63,
}

result = 0

function_entry_index_table = {}


def error(fmt, *args):
    print("Error at line %d: " % RUNNING_COMMAND_LINE_INDEX, end="")
    print(fmt % args)


# 寻址模式
def addressing(source):
    # 寄存器寻址模式
    if source in register_index_table:
        return AddressingMode.REGISTER, source

    # 内存寻址模式
    elif "[" in source and "]" in source:
        return AddressingMode.MEMORY, source

    # 立即数寻址模式
    elif source.isdigit():
        return AddressingMode.IMMEDIATE, int(source)

    else:
        error("无法识别的源操作数: %s", source)
        return None, None


# TODO
def memoryAddressing(memory_address):
    # 根据内存地址，定位到栈的地址
    return 0


# 根据寻址模式获取操作数的值
def getValueByAddressing(AddressingMode, source):
    if AddressingMode == AddressingMode.IMMEDIATE:
        return source

    elif AddressingMode == AddressingMode.REGISTER:
        register_index = register_index_table[source]
        return register[register_index]

    elif AddressingMode == AddressingMode.MEMORY:
        register_index = register_index_table[source[1:-1]]
        memory_address = register[register_index]
        stack_index = memoryAddressing(memory_address)
        return stack[stack_index]

    else:
        error("无法识别的源操作数: %s", source)
        return None


RUNNING_COMMAND_LINE_INDEX = 0


def run(code):
    global RUNNING_COMMAND_LINE_INDEX

    assembler_commands = code.split("\n")  # 将汇编代码按行分割

    command_line_index = 0

    while command_line_index < len(assembler_commands):
        RUNNING_COMMAND_LINE_INDEX = command_line_index  # 记录当前正在执行的代码行

        command_line = assembler_commands[command_line_index]  # 获取当前行的汇编代码

        command_line_index += 1  # 执行完一行代码后，指针指向下一行, 类似与PC寄存器 # TODO 改为使用PC寄存器进行模拟

        if command_line == "":
            continue
        # 如果以两个空格开头，则是直接运行的命令
        if command_line[0:2] == "  ":
            command = command_line[2:]
            run_command(command)

        # 检查是否是函数入口
        elif command_line[-1] == ":":
            function_name = command_line[:-1]

            # 记录函数入口的行号
            function_entry_index_table[function_name] = RUNNING_COMMAND_LINE_INDEX + 1

            # 如果是main函数，则直接调用
            if function_name == "main":
                RUNNING_COMMAND_LINE_INDEX += 1
                while assembler_commands[RUNNING_COMMAND_LINE_INDEX][0:2] != "  ":
                    command = assembler_commands[RUNNING_COMMAND_LINE_INDEX]

                    run_command(command)
                    RUNNING_COMMAND_LINE_INDEX += 1

                command_line_index = RUNNING_COMMAND_LINE_INDEX

        else:
            # TODO 不太清楚会不会有这种情况
            if command_line != "":
                error("无法识别的汇编代码: %s", command_line)


def run_command(command):
    # print("RUNNING INDEX: %d" % RUNNING_COMMAND_LINE_INDEX, "COMMAND: ", command) # DEBUG USE

    segment = command.split(" ")  # 将每行汇编代码按空格分割
    # push指令:将数据压入栈中 通用形式：push source
    if segment[0] == "push":
        if len(segment) == 2:
            addressing_mode, source = addressing(segment[1])

            if addressing_mode == AddressingMode.IMMEDIATE:  # 立即数寻址模式
                stack.append(source)

            elif addressing_mode == AddressingMode.REGISTER:  # 寄存器寻址模式
                register_index = register_index_table[source]
                stack.append(register[register_index])

            elif addressing_mode == AddressingMode.MEMORY:  # 内存寻址模式
                register_index = register_index_table[source[1:-1]]
                memory_address = register[register_index]
                stack_index = memoryAddressing(memory_address)
                stack.append(stack[stack_index])

        else:
            error("push的参数量错误，共有%d个参数", len(segment))

    # pop指令:将数据从栈中弹出 通用形式：pop destination
    if segment[0] == "pop":
        if len(segment) == 2:
            addressing_mode, destination = addressing(segment[1])

            if addressing_mode == AddressingMode.REGISTER:
                register_index = register_index_table[destination]
                register[register_index] = stack.pop()

            elif addressing_mode == AddressingMode.MEMORY:
                register_index = register_index_table[destination[1:-1]]
                memory_address = register[register_index]
                stack_index = memoryAddressing(memory_address)
                stack[stack_index] = stack.pop()

            else:
                error("pop指令的目的操作数错误, %s", destination)

    # 加法指令add 通用形式：add destination, source
    if segment[0] == "add":
        if len(segment) == 3:
            addressing_mode, destination = addressing(segment[1])

            if addressing_mode != AddressingMode.REGISTER:
                error("add指令的目的操作数错误, %s", destination)

            addressing_mode, source = addressing(segment[2])

            if addressing_mode == AddressingMode.REGISTER:
                register_index = register_index_table[destination]
                register[register_index] += source

            elif addressing_mode == AddressingMode.MEMORY:
                register_index = register_index_table[destination[1:-1]]

                memory_address = register[register_index]
                stack_index = memoryAddressing(memory_address)

                register[register_index] += stack[stack_index]

            elif addressing_mode == AddressingMode.IMMEDIATE:
                register_index = register_index_table[destination]
                register[register_index] += source

            else:
                error("add指令的源操作数错误, %s", source)

        else:
            error("add指令的参数量错误，共有%d个参数", len(segment))

        # 减法指令sub 通用形式：sub destination, source
    if segment[0] == "sub":
        if len(segment) == 3:
            addressing_mode, destination = addressing(segment[1])

            if addressing_mode != AddressingMode.REGISTER:
                error("sub指令的目的操作数错误, %s", destination)

            addressing_mode, source = addressing(segment[2])

            if addressing_mode == AddressingMode.REGISTER:
                register_index = register_index_table[destination]
                register[register_index] -= source

            elif addressing_mode == AddressingMode.MEMORY:
                register_index = register_index_table[destination[1:-1]]
                memory_address = register[register_index]
                stack_index = memoryAddressing(memory_address)
                register[register_index] += register_index

            elif addressing_mode == AddressingMode.IMMEDIATE:
                register_index = register_index_table[destination]
                register[register_index] -= source

            else:
                error("sub指令的源操作数错误, %s", source)

        else:
            error("sub指令的参数量错误，共有%d个参数", len(segment))

    # 整数乘法指令imul 通用形式：mul destination, source
    if segment[0] == "mul":
        if len(segment) == 3:
            addressing_mode, destination = addressing(segment[1])

            if addressing_mode != AddressingMode.REGISTER:
                error("mul指令的目的操作数错误, %s", destination)

            addressing_mode, source = addressing(segment[2])

            if addressing_mode == AddressingMode.REGISTER:
                register_index = register_index_table[destination]
                register[register_index] *= source

            elif addressing_mode == AddressingMode.MEMORY:
                register_index = register_index_table[destination[1:-1]]
                memory_address = register[register_index]
                stack_index = memoryAddressing(memory_address)
                register[register_index] += stack[stack_index]

            elif addressing_mode == AddressingMode.IMMEDIATE:
                register_index = register_index_table[destination]
                register[register_index] *= source

            else:
                error("mul指令的源操作数错误, %s", source)

        else:
            error("mul指令的参数量错误，共有%d个参数", len(segment))

    # 整数除法指令idiv 通用形式：div destination, source
    # idiv指令实现的有些粗糙，可能出现问题
    if segment[0] == "idiv":
        if len(segment) == 2:
            addressing_mode, operand = addressing(segment[1])

            if addressing_mode == AddressingMode.REGISTER:
                register_index = register_index_table[operand]

                rax_index = register_index_table["rax"]
                rdx_index = register_index_table["rdx"]

                register[rax_index] = register[rax_index] // register[register_index]
                register[rdx_index] = register[rax_index] % register[register_index]

            else:
                error("idiv指令的源操作数错误, %s", source)

        else:
            error("idiv指令的参数量错误，共有%d个参数", len(segment))

    # cqo指令, 将rax的值扩展到rdx:rax中
    if segment[0] == "cqo":
        if len(segment) == 1:
            rax_index = register_index_table["rax"]
            rdx_index = register_index_table["rdx"]
            # 将rax的值扩展到rdx:rax中
            # 模拟器还未模拟到如此深度，所以暂时不实现
        else:
            error("cqo指令的参数量错误，共有%d个参数", len(segment))

    # 比较指令cmp 通用形式：cmp operand1 operand2
    if segment[0] == "cmp":
        if len(segment) == 3:
            operand1_addressing_mode, operand1 = addressing(segment[1])
            operand2_addressing_mode, operand2 = addressing(segment[2])
            operand1_value = getValueByAddressing(operand1_addressing_mode, operand1)
            operand2_value = getValueByAddressing(operand2_addressing_mode, operand2)

            cmp_result = operand1_value - operand2_value

            if cmp_result == 0:
                register[register_index_table["ZF"]] = 1
            else:
                register[register_index_table["ZF"]] = 0

            if cmp_result < 0:
                register[register_index_table["SF"]] = 1
            else:
                register[register_index_table["SF"]] = 0

            # TODO 溢出标志位实现不够完善
            if cmp_result > MAX_64BIT_INT or cmp_result < -MAX_64BIT_INT:
                register[register_index_table["OF"]] = 1
            else:
                register[register_index_table["OF"]] = 0

            if cmp_result > 0:
                register[register_index_table["CF"]] = 1
            else:
                register[register_index_table["CF"]] = 0

        else:
            error("cmp指令的参数量错误，共有%d个参数", len(segment))

    # 设置标志位指令sete 通用形式：sete destination
    if segment[0] == "sete":
        if len(segment) == 2:
            addressing_mode, destination = addressing(segment[1])

            if addressing_mode == AddressingMode.REGISTER:
                register_index = register_index_table[destination]
                if register[register_index_table["ZF"]] == 1:
                    register[register_index] = 1
                else:
                    register[register_index] = 0

            else:
                error("sete指令的目的操作数错误, %s", destination)

        else:
            error("sete指令的参数量错误，共有%d个参数", len(segment))

    # 设置标志位指令setne 通用形式：setne destination
    if segment[0] == "setne":
        if len(segment) == 2:
            addressing_mode, destination = addressing(segment[1])

            if addressing_mode == AddressingMode.REGISTER:
                register_index = register_index_table[destination]
                if register[register_index_table["ZF"]] == 0:
                    register[register_index] = 1
                else:
                    register[register_index] = 0

            else:
                error("setne指令的目的操作数错误, %s", destination)

        else:
            error("setne指令的参数量错误，共有%d个参数", len(segment))

    # 设置标志位指令setl 通用形式：setl destination
    if segment[0] == "setl":
        if len(segment) == 2:
            addressing_mode, destination = addressing(segment[1])

            if addressing_mode == AddressingMode.REGISTER:
                register_index = register_index_table[destination]
                if register[register_index_table["SF"]] != register[register_index_table["OF"]]:
                    register[register_index] = 1
                else:
                    register[register_index] = 0

            else:
                error("setl指令的目的操作数错误, %s", destination)

        else:
            error("setl指令的参数量错误，共有%d个参数", len(segment))

    # 设置标志位指令setle 通用形式：setle destination
    if segment[0] == "setle":
        if len(segment) == 2:
            addressing_mode, destination = addressing(segment[1])

            if addressing_mode == AddressingMode.REGISTER:
                register_index = register_index_table[destination]
                if register[register_index_table["ZF"]] == 1 or register[register_index_table["SF"]] != register[
                    register_index_table["OF"]]:
                    register[register_index] = 1
                else:
                    register[register_index] = 0

            else:
                error("setle指令的目的操作数错误, %s", destination)

        else:
            error("setle指令的参数量错误，共有%d个参数", len(segment))

    # movzb指令，用于将一个字节（8位）的无符号整数值零扩展并移动到指定寄存器。movzb 的含义是 "move zero-extend byte"。
    if segment[0] == "movb":
        if len(segment) == 3:
            addressing_mode, destination = addressing(segment[1])

            if addressing_mode == AddressingMode.REGISTER:
                register_index = register_index_table[destination]

                addressing_mode, source = addressing(segment[2])
                source_value = getValueByAddressing(addressing_mode, source)
                # TODO 0扩展 依照现在版本的模拟程度， 0扩展不需要实现

                register[register_index] = source_value

            else:
                error("movb指令的目的操作数错误, %s", destination)

        else:
            error("movb指令的参数量错误，共有%d个参数", len(segment))

    # ret指令，用于从函数中返回 通用形式：ret
    elif segment[0] == "ret":
        print(register[register_index_table["rax"]])
