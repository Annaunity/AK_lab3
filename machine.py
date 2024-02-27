import logging
import sys

from isa import Opcode, Word, read_code


class DataPath:
    IN_ADDR = 1000
    OUT_ADDR = 1001

    def __init__(self, memory, input_buffer):
        self.memory = memory
        self.input_buffer = input_buffer
        self.output_buffer = []
        self.data = Word(Opcode.DATA, 0)
        self.instr = Word(Opcode.HLT, 0)
        self.ip = 0
        self.acc = 0
        self.addr = 0

    def signal_latch_instr(self):
        """Защелкнуть регистр инструкции из регистра данных"""
        self.instr = self.data
        assert self.instr.opcode is not Opcode.DATA, "бинарное кодирование инструкций не реализовано"

    def signal_incr_ip(self):
        "Инкрементировать IP"
        self.ip += 1

    def signal_latch_ip(self):
        "Защелкнуть в IP операнд инструкции"
        self.ip = self.instr.operand

    def signal_latch_addr(self, sel):
        "Защелкнуть регистр адреса исходя из селектора. Возможные варианты: `ip`, `operand`, `data`"
        if sel == "ip":
            self.addr = self.ip
        elif sel == "operand":
            self.addr = self.instr.operand
        elif sel == "data":
            assert self.data.opcode is Opcode.DATA, "бинарное кодирование инструкций не реализовано"
            self.addr = self.data.operand
        assert (
            self.addr == self.IN_ADDR or self.addr == self.OUT_ADDR or 0 <= self.addr < len(self.memory)
        ), f"адрес за пределами памяти: {self.addr}"

    def signal_mem_read(self):
        """Прочесть слово из памяти. Неявно защелкивает регистр данных"""
        if self.addr == self.IN_ADDR:
            if len(self.input_buffer) == 0:
                raise EOFError()
            self.data = Word(Opcode.DATA, ord(self.input_buffer.pop(0)))
        else:
            self.data = self.memory[self.addr]

    def signal_mem_write(self):
        """Записать слово в память"""
        assert self.data.opcode is Opcode.DATA, "бинарное кодирование инструкций не реализовано"
        if self.addr == self.OUT_ADDR:
            self.output_buffer.append(chr(self.data.operand))
        else:
            self.memory[self.addr] = self.data

    def signal_latch_data(self):
        "Защелкнуть регистр данных из аккумулятора"
        self.data = Word(Opcode.DATA, self.acc)

    def signal_latch_acc(self, alu_sub=False):
        "Защелкнуть аккумулятор суммой или разностью аккумулятора с регистром данных"
        assert self.data.opcode is Opcode.DATA, "бинарное кодирование инструкций не реализовано"
        if alu_sub:
            self.acc -= self.data.operand
        else:
            self.acc += self.data.operand

    def signal_clear_acc(self):
        """Очистить аккумулятор"""
        self.acc = 0

    def opcode(self):
        return self.instr.opcode

    def acc_is_zero(self):
        return self.acc == 0

    def acc_is_negative(self):
        return self.acc < 0


class ControlUnit:
    """Управляющее устройство.

    Симуляция с точностью до инструкции, поэтому TickCounter, присутствующий на схеме, здесь не используется."""

    def __init__(self, data_path):
        self._instr = 0
        self.data_path = data_path

    def next(self):
        """Выполнить следующую инструкцию. Возвращает `True` до тех пор, пока машина не остановится"""
        self._instr += 1
        self.data_path.signal_latch_addr("ip")
        self.data_path.signal_incr_ip()
        self.data_path.signal_mem_read()
        self.data_path.signal_latch_instr()

        match self.data_path.opcode():
            case Opcode.LD:
                self.data_path.signal_clear_acc()
                self.data_path.signal_latch_addr("operand")
                self.data_path.signal_mem_read()
                self.data_path.signal_latch_acc()
            case Opcode.ST:
                self.data_path.signal_latch_addr("operand")
                self.data_path.signal_latch_data()
                self.data_path.signal_mem_write()
            case Opcode.LDI:
                self.data_path.signal_clear_acc()
                self.data_path.signal_latch_addr("operand")
                self.data_path.signal_mem_read()
                self.data_path.signal_latch_addr("data")
                self.data_path.signal_mem_read()
                self.data_path.signal_latch_acc()
            case Opcode.STI:
                self.data_path.signal_latch_addr("operand")
                self.data_path.signal_mem_read()
                self.data_path.signal_latch_addr("data")
                self.data_path.signal_latch_data()
                self.data_path.signal_mem_write()
            case Opcode.CLR:
                self.data_path.signal_clear_acc()
            case Opcode.ADD:
                self.data_path.signal_latch_addr("operand")
                self.data_path.signal_mem_read()  # здесь не нужен latch_data, т.к. mem_read неявно защелкивает регистр данных
                self.data_path.signal_latch_acc()
            case Opcode.SUB:
                self.data_path.signal_latch_addr("operand")
                self.data_path.signal_mem_read()
                self.data_path.signal_latch_acc(alu_sub=True)
            case Opcode.JZ:
                if self.data_path.acc_is_zero():
                    self.data_path.signal_latch_ip()
            case Opcode.JNZ:
                if not self.data_path.acc_is_zero():
                    self.data_path.signal_latch_ip()
            case Opcode.JS:
                if self.data_path.acc_is_negative():
                    self.data_path.signal_latch_ip()
            case Opcode.JNS:
                if not self.data_path.acc_is_negative():
                    self.data_path.signal_latch_ip()
            case Opcode.JMP:
                self.data_path.signal_latch_ip()
            case Opcode.HLT:
                return False

        return True

    def __repr__(self):
        """Вернуть строковое представление состояния процессора."""
        data_repr = f"{self.data_path.data.operand:8}"
        if self.data_path.data.opcode is not Opcode.DATA:
            data_repr = " (instr)"

        return (
            f"{self._instr:4}. "
            f"IP: {self.data_path.ip:4} "
            f"ADDR: {self.data_path.addr:4} "
            f"DATA: {data_repr} "
            f"ACC: {self.data_path.acc:8}; "
            f"{self.data_path.instr}"
        )


def simulation(memory, input_buffer):
    data_path = DataPath(memory, input_buffer)
    control_unit = ControlUnit(data_path)

    try:
        while control_unit.next():
            logging.debug("%s", control_unit)
    except EOFError:
        pass
    logging.debug("%s", control_unit)

    output = "".join(data_path.output_buffer)
    logging.info("output_buffer: %s", repr(output))


def main(code_file, input_file):
    code = read_code(code_file)
    with open(input_file, encoding="utf-8") as file:
        input_text = file.read()
        input_buffer = []
        for char in input_text:
            input_buffer.append(char)

    simulation(code, input_buffer)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    assert len(sys.argv) == 3, "Wrong arguments: machine.py <code_file> <input_file>"
    _, code_file, input_file = sys.argv
    main(code_file, input_file)
