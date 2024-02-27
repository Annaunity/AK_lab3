import json
from collections import namedtuple
from enum import Enum


class Opcode(str, Enum):
    LD = "ld"
    ST = "st"
    LDI = "ldi"
    STI = "sti"

    CLR = "clr"
    ADD = "add"
    SUB = "sub"

    JZ = "jz"
    JNZ = "jnz"
    JS = "js"
    JNS = "jns"
    JMP = "jmp"
    HLT = "hlt"

    DATA = "data"

    def __str__(self):
        return str(self.value)


class Word(namedtuple("Word", "opcode operand")):
    def __repr__(self):
        return f"{self.opcode} {self.operand}"


def write_code(instrs, filename):
    """Записать машинный код в файл."""
    with open(filename, "w", encoding="utf-8") as file:
        # Почему не: `file.write(json.dumps(code, indent=4))`?
        # Чтобы одна инструкция была на одну строку.
        buf = []
        for instr in instrs:
            buf.append(json.dumps(instr._asdict()))
        file.write("[" + ",\n ".join(buf) + "]")


def read_code(filename):
    """Прочесть машинный код из файла."""
    with open(filename, encoding="utf-8") as file:
        code = json.loads(file.read())

    instrs = []

    for instr in code:
        opcode = Opcode(instr["opcode"])
        operand = int(instr["operand"])
        instrs.append(Word(opcode, operand))

    return instrs
