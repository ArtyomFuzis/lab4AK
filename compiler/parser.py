import re
from enum import Enum

from compiler.utils import WrongSyntaxError

class ParseState(Enum):
    No = 0
    SecInt = 1
    SecText = 2
    SecData = 3

class Parser:
    @staticmethod
    def parse_asm(cls, text: str) -> tuple[list[int],list[int]]:
        split = text.lower().splitlines()
        state = ParseState.No
        for i in range(1,len(split)+1):
            line = split[i-1]
            parts = re.split("\s+", line)
            if len(parts) > 3:
                raise WrongSyntaxError(f"Too match terms in line {i}.")

            if parts[0] != '.section' and state == ParseState.No:
                raise WrongSyntaxError(f"No section definition found in line {i}.")

            if parts[0] == '.section':
                if parts[1] == 'int':
                    state = ParseState.SecInt
                elif parts[1] == 'data':
                    state = ParseState.SecData
                elif parts[1] == 'text':
                    state = ParseState.SecText
                else:
                    raise WrongSyntaxError(f"Unknown section in line {i}.")




