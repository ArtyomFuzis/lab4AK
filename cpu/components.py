from typing import Callable

from .utils import WrongImplementationError


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



