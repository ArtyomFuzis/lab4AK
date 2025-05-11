from abstractions import *
from utils import WrongImplementationError


class StateLatch(Latch):

    def __init__(self):
        self.__state = False

    def change_state(self, state: bool) -> None:
        self.__state = state

    def get_state(self) -> bool:
        return self.__state


class TrapControlLatch(ControlLatch):
    bind: LogicalElement | None

    def __init__(self):
        self.__state = False
        self.bind = None

    def bind_ctrl(self, element: LogicalElement) -> None:
        self.bind = element

    def change_state(self, state: bool) -> None:
        self.__state = state
        if state and self.bind is not None:
            self.bind.perform_change()
            self.__state = False

    def get_state(self) -> bool:
        return self.__state


class DataBus:
    __buffer: bytes

    def __init__(self, size):
        self.__buffer = bytes(size)

    def get_data(self) -> bytes:
        return self.__buffer

    def post_data(self, data: bytes):
        if len(data) != len(self.__buffer):
            raise WrongImplementationError("Buffer size: " + str(len(self.__buffer)) + " does not equals " + str(len(data)))
        self.__buffer = data

class MemoryUnit(LogicalElement):
    __data_arr: bytearray

    def __init__(self, ctrl_latch: ControlLatch, rw_latch: StateLatch, bus_addr: DataBus, bus_in: DataBus, bus_out: DataBus, size: int = 32768):
        super().__init__(ctrl_latch)
        self.__data_arr = bytearray(size)
        self.__rw_latch = rw_latch
        self.__bus_addr = bus_addr
        self.__bus_in = bus_in
        self.__bus_out = bus_out


    def perform_change(self) -> None:
        addr = int.from_bytes(self.__bus_addr.get_data())
        mode = self.__rw_latch.get_state()
        if mode:
            in_data = self.__bus_in.get_data()
            self.__data_arr[addr:addr+len(in_data)] = in_data
        else:
            bus_len = len(self.__bus_out.get_data())
            self.__bus_out.post_data(self.__data_arr[addr:addr+bus_len])
