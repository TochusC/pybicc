<div align="center">
<h1> Pybicc💯</h1>

### A C-Like Compiler + Assembly Code Interpreter with Graphical Interface


#### Version 0.1.2 


[![madewithlove](https://img.shields.io/badge/made_with-%E2%9D%A4-red?style=for-the-badge&labelColor=orange)](https://github.com/TochusC/ai-assistant-teaching-website)

[**简体中文**](./README.md) | [**English**](./docs/en/README.md)


[China University of Petroleum (East China)](https://upc.edu.cn/)-Compiler Principle Course Design-Group One

---

<div align="center">

### Still Under Active Development🔨...

Project inspired by [Chibicc](https://github.com/rui314/chibicc), thanks to [rui314](https://github.com/rui314) for the open-source project.

Graphical interface implemented using [PyQt6](https://riverbankcomputing.com/software/pyqt/intro)

</div>

</div>

Currently, only supports mathematical expressions with operators like + - * / ( ) < > == != <= >=.

Does not support floating-point numbers / negative numbers.


## Code Structure✨：

---

    - main.py           Current entry point for the compiler program

    - tokenize.py       Lexical analysis, converts source code into Token stored in a linked list

    - parse.py:         Syntax analysis, converts Token into an abstract syntax tree

    - codegen.py        Semantic generation, converts abstract syntax tree into assembly code

    - simulator.py      Assembly code interpreter

    - interface.py      Graphical interface, not yet integrated with the compiler and interpreter

## How to Run This Project❓

---

1. Install [Python](https://www.python.org/), this project is developed using Python 3.12.0.
2. Install dependencies
    ```shell
    pip install -r requirements.txt
    ```
1. Run main.py, providing examples for the compiler and interpreter
    ```shell
    python main.py
    ```
1. Run interface.py, providing a sample of the graphical interface, currently not integrated with the compiler and interpreter
    ```shell
    python interface.py
    ```
   
   

## Input Examples👾：

---
    - 7+9*2
    - 3+ (4 / 2)
    - 1 != 2
    - 5 == 3+1 + 4
    - 8 <= 9 * (3 +1)
