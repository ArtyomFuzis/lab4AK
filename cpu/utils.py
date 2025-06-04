from enum import Enum
class WrongImplementationError(Exception):
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
