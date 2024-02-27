import logging
import sys
from ast import literal_eval

from isa import Opcode, Word, write_code
from machine import DataPath


def translate(text):
    code = []

    # словарь с объявленными метками и их адресами
    labels = {}

    # словарь с обращениями к еще не объявленным меткам
    references = {}

    for line in text.splitlines():
        label, instr = parse_line(line)

        if label:
            define_label(code, labels, references, label)

        # разбиение инструкции на опкод и операнд
        terms = instr.split(None, 1)
        if len(terms) == 0:
            continue

        if terms[0] == "string":
            # особый макрос - pascal строка
            define_string(code, terms)
            continue

        opcode = Opcode(terms[0].strip())
        operand = 0 if len(terms) <= 1 else terms[1].strip()

        try:
            # операнд - число
            operand = int(operand)
        except ValueError:
            # операнд - метка
            operand = use_label(code, labels, references, operand)

        instr = Word(opcode, operand)
        code.append(instr)

    for label in references.keys():
        logging.warning(f"метка `{label}` не объявлена")

    return code


def parse_line(line):
    # игнорируем комментарии
    line = line.split(";", 1)[0]

    # разделяем метку и инструкцию
    label = None
    instr = line
    if ":" in line:
        label, instr = line.split(":", 1)

    return label, instr


def define_label(code, labels, references, label):
    label = label.strip()
    assert label not in labels, f"метка с именем {label} уже объявлена"  # noqa: RUF001
    labels[label] = len(code)
    if label in references:
        # обновляем адреса в инструкциях до объявления
        for idx in references[label]:
            code[idx] = Word(code[idx].opcode, labels[label])
        del references[label]


def define_string(code, terms):
    string = literal_eval(terms[1])
    code.append(Word(Opcode.DATA, len(string)))
    for char in string:
        code.append(Word(Opcode.DATA, ord(char)))


def use_label(code, labels, references, label):
    if label == "IN":
        # особая метка IN - хардкод адрес на устройство ввода
        return DataPath.IN_ADDR
    if label == "OUT":
        return DataPath.OUT_ADDR
    if label in labels:
        # уже объявленная метка
        return labels[label]

    # еще не объявленная метка
    if label not in references:
        references[label] = []
    references[label].append(len(code))
    return 0


def main(source, target):
    """Функция запуска транслятора. Параметры -- исходный и целевой файлы."""
    with open(source, encoding="utf-8") as f:
        source = f.read()

    code = translate(source)

    write_code(code, target)
    print("source LoC:", len(source.split("\n")), "code instr:", len(code))


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: translator.py <input_file> <target_file>"
    _, source, target = sys.argv
    main(source, target)
