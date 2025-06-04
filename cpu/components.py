from typing import Callable

from .utils import WrongImplementationError, ALUOperations


class Latch:

    def __init__(self, callfunc: Callable[[], None]):
        self.__callfunc = callfunc

    def perform(self) -> None:
        self.__callfunc()



class DataBus:
    __provider: Callable[[], bytes]|None

    def __init__(self, size: int):
        self.__provider = None
        self.__size = size

    def get_data(self) -> bytes:
        if self.__provider is None:
            raise WrongImplementationError("Bus not connected")
        data = self.__provider()
        if len(data) != self.__size:
            raise WrongImplementationError("Buffer size: " + str(self.__size) + " does not equals " + str(len(data)))
        return data

    def bind_provider(self, provider: Callable[[], bytes]) -> None:
        if self.__provider is not None:
            raise WrongImplementationError("Bus already connected")
        self.__provider = provider

    def get_size(self) -> int:
        return self.__size


class MemoryUnit:
    __data_arr: bytearray

    def __init__(self, bus_op: DataBus, bus_address: DataBus, bus_in: DataBus, bus_out: DataBus, size: int = 0x500, bus_size: int = 4):

        self.__data_arr = bytearray(size)
        self.__bus_op = bus_op
        self.__bus_address = bus_address
        self.__bus_in = bus_in
        self.__bus_out = bus_out
        self.__size_bus = bus_size
        if self.__bus_address.get_size() != self.__size_bus:
            raise WrongImplementationError("Addr bus size: " + str(self.__bus_address.get_size()) + " does not equals " + str(self.__size_bus))
        if self.__bus_in.get_size() != self.__size_bus:
            raise WrongImplementationError(
                "In bus size: " + str(self.__bus_in.get_size()) + " does not equals " + str(self.__size_bus))
        if self.__bus_out.get_size() != self.__size_bus:
            raise WrongImplementationError(
                "In bus size: " + str(self.__bus_out.get_size()) + " does not equals " + str(self.__size_bus))
        self.__bus_out.bind_provider(self.get_value)
    out_val: bytes

    def get_control_latch(self) -> Latch:
        return Latch(self.__perform_change)

    def __perform_change(self) -> None:
        addr = int.from_bytes(self.__bus_address.get_data())
        op = self.__bus_op.get_data()
        rw = op[0] & 1 != 0
        if rw:
            in_data = self.__bus_in.get_data()
            self.__data_arr[addr:addr+self.__size_bus] = in_data
        else:
           self.out_val = self.__data_arr[addr:addr+self.__size_bus]

    def get_value(self) -> bytes:
        return self.out_val

class Register:
    __value: bytes
    def __init__(self, bus_in: DataBus, bus_out: DataBus, size: int):
        self.__value = bytearray(size)
        self.__bus_in = bus_in
        bus_out.bind_provider(self.get_value)

    def get_value(self) -> bytes:
        return self.__value

    def __update_value(self) -> None:
        self.__value = self.__bus_in.get_data()

    def get_control_latch(self) -> Latch:
        return Latch(self.__update_value)


class MultiPlex:
    __Bindings: dict[int, DataBus]
    def __init__(self, b_ctrl: DataBus, b_out: DataBus, size: int):
        self.__b_ctrl = b_ctrl
        self.__size = size
        self.__Bindings = dict()
        self.b_out = b_out
        self.__data = bytes(self.__size)
        b_out.bind_provider(self.__getvalue)

    def bind_inp(self, code:int, bus: DataBus) -> None:
        self.__Bindings[code] = bus

    def __getvalue(self) -> bytes:
        choice = int.from_bytes(self.__b_ctrl.get_data())
        if choice not in self.__Bindings:
            raise WrongImplementationError("Multiplex choice is not bound: " + str(choice))

        return self.__Bindings[choice].get_data()

class ALU:

    def __init__(self, b_op: DataBus, b_in_1: DataBus, b_in_2: DataBus, b_flg: DataBus, b_out: DataBus):
        self.__b_op = b_op
        self.__b_in_1 = b_in_1
        self.__b_in_2 = b_in_2
        self.operations = {el.value: el for el in ALUOperations}
        self.__out = (0).to_bytes(4)
        self.__flg = (0).to_bytes(2)
        b_flg.bind_provider(self.__get_flg)
        b_out.bind_provider(self.__get_out)

    def __get_flg(self) -> bytes:
        self.perform()
        return self.__flg

    def __get_out(self) -> bytes:
        self.perform()
        return self.__out

    def perform(self):
        op_code_full = int.from_bytes(self.__b_op.get_data())
        op_code_op = op_code_full & 0b00001111
        flg_byte  = op_code_full & 0b00010000 != 0
        flg_inc    = op_code_full & 0b00100000 != 0
        flg_dec    = op_code_full & 0b01000000 != 0
        flg_inv    = op_code_full & 0b10000000 != 0
        operation = self.operations[op_code_op]
        data1 = self.__b_in_1.get_data()
        data2 = self.__b_in_2.get_data()
        op1 = int.from_bytes(data1, signed=True)
        op2 = int.from_bytes(data2, signed=True)
        res = self.perform_operation(operation, op1, op2, False)
        resu = self.perform_operation(operation, op1, op2, True)

        if flg_inc:
            res += 1

        if flg_dec:
            res -= 1

        if flg_inv:
            res = ~res

        if flg_byte:
            c = 0 if (res & 0x100) == 0 else 1
            v = 0 if -128 <= res <= 127 else 1
            res = res & 0xFF
            n = 1 if res > 127 else 0
            z = 0 if res != 0 else 1
        else:
            c = 0 if (resu & 0x100000000) == 0 else 1
            v = 0 if -2147483648 <= res <= 2147483647 else 1
            res = res & 0xFFFFFFFF
            n = 1 if res > 2147483647 else 0
            z = 0 if res != 0 else 1
        self.__flg = int.to_bytes((c << 3) + (v << 2) + (n << 1) + z, 1)
        self.__out = int.to_bytes(res, 4, signed=False)

    def perform_operation(self, operation: ALUOperations, op1e: int, op2e: int, unsigned: bool) -> int:
        if unsigned:
            op1 = (0x100000000+op1e)%0x100000000
            op2 = (0x100000000+op2e)%0x100000000
        else:
            op1 = op1e
            op2 = op2e
        if operation == ALUOperations.Add:
            res = op1 + op2
        elif operation == ALUOperations.Sub:
            if unsigned: res = op1 + 0x100000000-op2
            else: res = op1 - op2
        elif operation == ALUOperations.Mul:
            res = op1 * op2
        elif operation == ALUOperations.Div:
            res = op1 // op2
        elif operation == ALUOperations.Rem:
            res = op1 % op2
        elif operation == ALUOperations.Left:
            res = op1
        elif operation == ALUOperations.Right:
            res = op2
        elif operation == ALUOperations.ShiftL:
            res = op1 << op2
        elif operation == ALUOperations.ShiftR:
            res = op1 >> op2
        elif operation == ALUOperations.And:
            res = op1 & op2
        elif operation == ALUOperations.Or:
            res = op1 | op2
        elif operation == ALUOperations.Xor:
            res = op1 ^ op2
        else:
            raise WrongImplementationError("Operation not implemented ")
        return res












