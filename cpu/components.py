import queue
from typing import Callable

from .utils import WrongImplementationError, ALUOperations, ForbiddenAddress


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

    def unbind_provider(self) -> None:
        self.__provider = None

    def get_size(self) -> int:
        return self.__size


class MemoryUnit:
    __data_arr: bytearray
    __io_in_data: DataBus
    __io_in_r: DataBus
    __io_out_data: DataBus
    __io_out_r: DataBus
    __io_out_l: Latch
    __b_inp_got: DataBus
    __b_inp_allow: DataBus
    __input_data: bytes|None
    __out_io_val: bytes

    def __init__(self, bus_op: DataBus, bus_address: DataBus, bus_in: DataBus, bus_out: DataBus, size: int = 0x10000, bus_size: int = 4):
        self.__data_arr = bytearray(size)
        self.__bus_op = bus_op
        self.__bus_address = bus_address
        self.__bus_in = bus_in
        self.__bus_out = bus_out
        self.__size_bus = bus_size
        self.__io_mode = False
        self.__inp_got = False
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
        if self.__io_mode and (0x0020-self.__size_bus+1) <= addr <= 0x001F:
            raise ForbiddenAddress(f"Unable to use address: {addr} because it can touch i/o ports")
        if rw:
            if self.__io_mode and addr == 0x0020:
                raise ForbiddenAddress("Input port can't be used for output")
            elif self.__io_mode and addr == 0x0021:
                self.__out_io_val = self.__input_data
                self.__io_out_l.perform()
            else:
                in_data = self.__bus_in.get_data()
                self.__data_arr[addr:addr+self.__size_bus] = in_data
        else:
           if self.__io_mode and addr == 0x0021:
               raise ForbiddenAddress("Output port can't be used for input")
           elif self.__io_mode and addr == 0x0020:
               self.out_val = self.__input_data
               self.__input_data = None
           else:
            self.out_val = self.__data_arr[addr:addr+self.__size_bus]

    def get_value(self) -> bytes:
        return self.out_val

    def __io_in_state(self) -> bytes:
        return self.__b_inp_allow.get_data()

    def __init_int(self):
        in_data = self.__io_in_data.get_data()
        self.__input_data = in_data
        self.__inp_got = True

    def __get_int_state(self) -> bytes:
        if self.__inp_got:
            return (1).to_bytes(1)
        else:
            return (0).to_bytes(1)

    def __get_io_output_value(self) -> bytes:
        return self.__out_io_val

    def bind_input_io(self, b_data: DataBus, b_ready: DataBus) -> Latch:
        self.__io_mode = True
        self.__io_in_data = b_data
        self.__io_in_r = b_ready
        self.__io_in_r.bind_provider(self.__io_in_state)
        return Latch(self.__init_int)

    def bind_int_buses(self, b_int_got: DataBus, b_int_allow: DataBus) -> None:
        self.__b_inp_got = b_int_got
        self.__b_inp_allow = b_int_allow
        self.__b_inp_got.bind_provider(self.__get_int_state)

    def bind_output_io(self, b_data: DataBus, b_ready: DataBus, l_out: Latch) -> None:
        self.__io_mode = True
        self.__io_out_data = b_data
        self.__io_out_r = b_ready
        self.__io_out_data.bind_provider(self.__get_io_output_value)
        self.__io_out_l = l_out


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

class DeviceControlUnitInput:
    __data: bytes|None
    def __init__(self, b_to_reg: DataBus, l_reg: Latch, b_io_r: DataBus, l_io_in: Latch):
        self.__b_to_reg = b_to_reg
        self.__l_reg = l_reg
        self.__b_io_r = b_io_r
        self.__l_io_in = l_io_in
        self.__b_to_reg.bind_provider(self.__get_data_to_reg)
        self.input_queue = queue.Queue()

    def __get_data_to_reg(self) -> bytes:
        return self.__data

    def post_data(self, data: bytes|None = None) -> None:
        if data is not None:
            self.input_queue.put(data)
        if int.from_bytes(self.__b_io_r.get_data()) != 1:
            return
        if self.input_queue.empty():
            return
        self.__data = self.input_queue.get()
        self.__l_reg.perform()
        self.__l_io_in.perform()

class DeviceControlUnitOutput:

    def __init__(self, b_from_reg: DataBus, l_reg: Latch, b_io_r: DataBus):
        self.__b_from_reg = b_from_reg
        self.__l_reg = l_reg
        self.__b_io_r = b_io_r
        self.__b_io_r.bind_provider(self.__get_ready)
        self.output_queue = queue.Queue()

    def __get_ready(self) -> bytes:
        return (1).to_bytes(1, signed=False)

    def __load_data(self):
        self.__l_reg.perform()
        self.output_queue.put(self.__b_from_reg.get_data())

    def get_control_latch(self) -> Latch:
        return Latch(self.__load_data)

    def get_data(self) -> bytes|None:
        if self.output_queue.empty():
            return None
        else:
            return self.output_queue.get()

















