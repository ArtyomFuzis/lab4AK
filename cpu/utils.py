from enum import Enum
class WrongImplementationError(Exception):
    pass

class ForbiddenAddress(Exception):
    pass

class ALUOperations(Enum):
    Add = 0
    Sub = 1
    ShiftL = 2
    ShiftR = 3
    Div = 4
    Mul = 5
    Rem = 6
    Left = 7
    Right = 8
    And = 9
    Or = 10
    Xor = 11
    Inc4 = 12
    Dec4 = 13
    Inc4r = 14
    Dec4r = 15

class SharedMemory:
    def __init__(self, mem_size:int = 0x10000):
        self.arr = bytearray(mem_size)

class CUState(Enum):
    Start = 0
    Run = 1
    Finish = 2
