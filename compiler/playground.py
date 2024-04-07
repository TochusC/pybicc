import struct


def float_to_ieee754(f):
    # 将浮点数转换为IEEE 754格式的二进制表示（32位）
    packed = struct.pack('>f', f)
    # 只取前4个字节（32位），即4个十六进制数
    hex_representation = ''.join(f'{byte:02x}' for byte in packed[:4])
    return hex_representation


def double_to_ieee754(num):
    # 将浮点数转换为 64 位 IEEE 754 格式的字节序列
    ieee754_bytes = struct.pack('>d', num)
    # 将字节序列转换为十六进制表示
    ieee754_hex = ''.join(f'{byte:02X}' for byte in ieee754_bytes)
    return ieee754_hex


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


# 测试
num = 3.14
ieee754_hex = float_to_ieee754(num)
print("IEEE 754 格式的十六进制表示:", ieee754_hex)
value = ieee754_to_float(ieee754_hex)
print("还原后的浮点数:", value)
