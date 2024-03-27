<div align="center">
<h1> Pybicc💯</h1>

### 具有图形化界面的类C语言编译器 + 汇编代码解释器


#### version 0.1.7u


[![madewithlove](https://img.shields.io/badge/made_with-%E2%9D%A4-red?style=for-the-badge&labelColor=orange)](https://github.com/TochusC/ai-assistant-teaching-website)

[**简体中文**](./README.md) | [**English**](./docs/en/README.md)


[中国石油大学(华东)](https://upc.edu.cn/)-编译原理课程设计-二组

---

<div align="center">

### 仍在火热施工中🔨...

项目参考自[Chibicc](https://github.com/rui314/chibicc)，感谢[rui314](https://github.com/rui314)的开源项目。

图形化界面使用[PyQt6](https://riverbankcomputing.com/software/pyqt/intro)实现

</div>

</div>

---
未完成版本，缺少编译器和解释器实现。

支持的变量类型：int

支持运算符：+ - * / % == != < <= > >= && || ! = & ^

支持指针、函数定义和函数调用。

支持IF-ELSE语句、解释器仍未实现。

WHILE语句编译器有BUG,

编译器生成结果待进一步优化。

## 项目目标🎯：

---

   实现一个通过Python模仿的类C语言编译器，能够将C语言代码编译为Intel 80x86汇编代码，
   并且能够解释执行汇编代码得出运算结果。同时项目还会提供图形化界面，提供部分集成开发环境（IDE）的功能。

## 代码结构✨：

---

    - main.py           目前的编译器程序入口

    - tokenize.py       词法分析，将源代码转换为链表存储的Token

    - parse.py:         语法分析，将Token转换为抽象语法树

    - codegen.py        语义生成，将抽象语法树转换为汇编代码

    - simulator.py      汇编代码解释器

    - interface.py      图形化界面，尚未与编译器和解释器整合

## 如何运行此项目❓

---

1. 安装[Python](https://www.python.org/), 本项目使用Python3.12.0开发。
2. 安装依赖
    ```shell
    pip install -r requirements.txt
    ```
1. main.py，提供了编译器和解释器使用范例。
    ```shell
    python main.py
    ```
1. interface.py，提供了图形化界面样例，目前图形界面尚未与编译器和解释器整合。

    ```shell
    python interface.py
    ```
   
   

## 输入样例参考👾：

---
    - 7+9*2
    - 3+ (4 / 2)
    - 1 != 2
    - 5 == 3+1 + 4
    - 8 <= 9 * (3 +1)
