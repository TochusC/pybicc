<div align="center">
<img src="docs/static/img/logo.png" style="width: 20%">

<h1> Pybicc💯</h1>

### 具有图形化界面的类C语言编译器 + 汇编代码解释器





[![version](https://img.shields.io/badge/Version-0.2.9u-blue)](https://github.com/TochusC/ai-assistant-teaching-website)
[![course](https://img.shields.io/badge/UPC-CompilerDesign-blue)](https://github.com/TochusC/ai-assistant-teaching-website)

[![madewithlove](https://img.shields.io/badge/made_with-%E2%9D%A4-red?style=for-the-badge&labelColor=orange)](https://github.com/TochusC/ai-assistant-teaching-website)


[**简体中文**](./README.md) | [**English**](./docs/en/README.md)


[中国石油大学(华东)](https://upc.edu.cn/)-编译原理课程设计-二组

![GUI-Preview](docs/static/img/gui-preview.png)

---

<div align="center">

### 仍在火热施工中🔨...

项目参考自[Chibicc](https://github.com/rui314/chibicc)，感谢[rui314](https://github.com/rui314)的开源项目💖。

图形化界面采用Fluent 2设计风格，使用[PyQt6](https://riverbankcomputing.com/software/pyqt/intro)及[PyQt-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)实现🌟。

</div>

</div>

---
支持的变量类型：int, char, short, long, float, double。
支持指针、函数、数组、结构体。

支持整数、字符串、浮点数字面值常量

支持运算符："==", "!=", "<=", ">=", "->", "++", "--", "&&", "||", "*=", "/=", "%=", "+=", "-=", "&=", "^=", "|=", 

支持IF-ELSE, FOR, WHILE语句

## 项目目标🎯：

   实现一个通过Python模仿的类C语言编译器，能够将C语言代码编译为Intel 80x86汇编代码，
   配有解释器,能够解释执行汇编代码得出运算结果。同时项目还提供了图形化界面，提供部分集成开发环境（IDE）的功能。

## 代码结构✨：


    - main.py           编译器程序入口

    - compiler\tokenize.py       词法分析，将源代码转换为链表存储的Token

    - compiler\parse.py:         语法分析，将Token转换为抽象语法树

    - compiler\codegen.py        语义生成，将抽象语法树转换为汇编代码

    - compiler\simulator.py      汇编代码解释器

    - gui\fluent.py      图形化界面入口

## 如何运行此项目❓


1. 安装[Python](https://www.python.org/), 本项目使用Python3.12.0开发。
2. 安装依赖
    ```shell
    pip install -r requirements.txt
    ```
1. main.py，提供了编译器和解释器使用范例。
    ```shell
    python main.py
    ```
1. interface\fluent.py，提供了Pybicc的图形化界面

    ```shell
    python interface\fluent.py
    ```
   
   

## 输入样例参考👾：

```
   int main() { int i=0; int j=0; for (i=0; i<=10; i=i+1) j=i+j; return j; }
```
```
   int main() { int a=3; int z=5; return a+z; }
```
```
   int main() { int x=3;int y=5; *(&x+8)=7; return y; }
```
