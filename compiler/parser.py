import re
from enum import Enum

from utils import WrongSyntaxError


class ParseState(Enum):
    No = 0
    SecInt = 1
    SecText = 2
    SecData = 3


class Parser:
    @classmethod
    def place_series(cls, mem, addr, val, size):
        res = val.to_bytes(size, signed=True)
        for i in range(size):
            mem[addr + i] = res[i]

    @classmethod
    def reg_cmd_factory(cls, have_arg: bool, ar_size: int = 0):
        def reg_cmd(opcode: int, arg: str | None, line: int):
            if have_arg:
                if arg is None:
                    raise WrongSyntaxError(f"Argument not found in line: {line}")
                if arg[0:2] == '0x':
                    true_arg = int.from_bytes(bytes.fromhex(arg[2:]))
                elif arg.isdigit() or (arg[0] == '-' and arg[1:].isdigit()):
                    true_arg = int(arg)
                elif len(arg) == 3 and arg[0] == "'" and arg[-1] == "'":
                    true_arg = ord(arg[1])
                elif arg[0] == "'":
                    raise WrongSyntaxError(
                        f"In line {line}: argument cannot be contain a whitespace or unclosed quotes.")
                else:
                    true_arg = arg
                cls.prog[cls.cur_addr_cmem] = (opcode, true_arg, ar_size)
            else:
                if arg is not None:
                    raise WrongSyntaxError(f"Unknown term found in line: {line}")
                cls.prog[cls.cur_addr_cmem] = (opcode, None, 0)
            cls.cur_addr_cmem += ar_size + 1

        return reg_cmd

    @classmethod
    def parse_cmd(cls, cmd: str, cmd_arg: str | None, line: int) -> None:
        reg_no_arg = cls.reg_cmd_factory(False)
        reg_4_arg = cls.reg_cmd_factory(True, 4)
        reg_2_arg = cls.reg_cmd_factory(True, 2)
        if cmd == 'inc':
            reg_no_arg(0x01, cmd_arg, line)
        elif cmd == 'dec':
            reg_no_arg(0x02, cmd_arg, line)
        elif cmd == "inc4":
            reg_no_arg(0x03, cmd_arg, line)
        elif cmd == 'dec4':
            reg_no_arg(0x04, cmd_arg, line)
        elif cmd == 'inv':
            reg_no_arg(0x05, cmd_arg, line)
        elif cmd == 'neg':
            reg_no_arg(0x06, cmd_arg, line)
        elif cmd == 'halt':
            reg_no_arg(0x07, cmd_arg, line)
        elif cmd == 'ret':
            reg_no_arg(0x08, cmd_arg, line)
        elif cmd == 'ld':
            reg_4_arg(0x40, cmd_arg, line)
        elif cmd == 'add':
            reg_4_arg(0x41, cmd_arg, line)
        elif cmd == 'sub':
            reg_4_arg(0x42, cmd_arg, line)
        elif cmd == 'and':
            reg_4_arg(0x43, cmd_arg, line)
        elif cmd == 'or':
            reg_4_arg(0x44, cmd_arg, line)
        elif cmd == 'xor':
            reg_4_arg(0x45, cmd_arg, line)
        elif cmd == 'shiftl':
            reg_4_arg(0x46, cmd_arg, line)
        elif cmd == 'shiftr':
            reg_4_arg(0x47, cmd_arg, line)
        elif cmd == 'mul':
            reg_4_arg(0x48, cmd_arg, line)
        elif cmd == 'div':
            reg_4_arg(0x49, cmd_arg, line)
        elif cmd == 'rem':
            reg_4_arg(0x4a, cmd_arg, line)
        elif cmd == 'jmp':
            reg_4_arg(0x4b, cmd_arg, line)
        elif cmd == 'jz':
            reg_4_arg(0x4c, cmd_arg, line)
        elif cmd == 'jnz':
            reg_4_arg(0x4d, cmd_arg, line)
        elif cmd == 'jgt':
            reg_4_arg(0x4e, cmd_arg, line)
        elif cmd == 'jlt':
            reg_4_arg(0x4f, cmd_arg, line)
        elif cmd == 'jc':
            reg_4_arg(0x51, cmd_arg, line)
        elif cmd == 'jnc':
            reg_4_arg(0x52, cmd_arg, line)
        elif cmd == 'jv':
            reg_4_arg(0x53, cmd_arg, line)
        elif cmd == 'jnv':
            reg_4_arg(0x54, cmd_arg, line)
        elif cmd == 'ld_a':
            reg_4_arg(0x60, cmd_arg, line)
        elif cmd == 'add_a':
            reg_4_arg(0x61, cmd_arg, line)
        elif cmd == 'sub_a':
            reg_4_arg(0x62, cmd_arg, line)
        elif cmd == 'and_a':
            reg_4_arg(0x63, cmd_arg, line)
        elif cmd == 'or_a':
            reg_4_arg(0x64, cmd_arg, line)
        elif cmd == 'xor_a':
            reg_4_arg(0x65, cmd_arg, line)
        elif cmd == 'shiftl_a':
            reg_4_arg(0x66, cmd_arg, line)
        elif cmd == 'shiftr_a':
            reg_4_arg(0x67, cmd_arg, line)
        elif cmd == 'mul_a':
            reg_4_arg(0x68, cmd_arg, line)
        elif cmd == 'div_a':
            reg_4_arg(0x69, cmd_arg, line)
        elif cmd == 'rem_a':
            reg_4_arg(0x6a, cmd_arg, line)
        elif cmd == 'st':
            reg_4_arg(0x6b, cmd_arg, line)
        elif cmd == 'ld_ind':
            reg_4_arg(0x6c, cmd_arg, line)
        elif cmd == 'st_ind':
            reg_4_arg(0x6d, cmd_arg, line)
        elif cmd == 'jzr':
            reg_2_arg(0x80, cmd_arg, line)
        elif cmd == 'jnzr':
            reg_2_arg(0x81, cmd_arg, line)
        elif cmd == 'jgtr':
            reg_2_arg(0x82, cmd_arg, line)
        elif cmd == 'jltr':
            reg_2_arg(0x83, cmd_arg, line)
        elif cmd == 'jcr':
            reg_2_arg(0x84, cmd_arg, line)
        elif cmd == 'jncr':
            reg_2_arg(0x85, cmd_arg, line)
        elif cmd == 'jvr':
            reg_2_arg(0x86, cmd_arg, line)
        elif cmd == 'jnvr':
            reg_2_arg(0x87, cmd_arg, line)
        elif cmd == 'jr':
            reg_2_arg(0x88, cmd_arg, line)
        elif cmd == 'vld1':
            reg_4_arg(0xf0, cmd_arg, line)
        elif cmd == 'vld2':
            reg_4_arg(0xf1, cmd_arg, line)
        elif cmd == 'vld3':
            reg_4_arg(0xf2, cmd_arg, line)
        elif cmd == 'vst1':
            reg_4_arg(0xf3, cmd_arg, line)
        elif cmd == 'vst2':
            reg_4_arg(0xf4, cmd_arg, line)
        elif cmd == 'vst3':
            reg_4_arg(0xf5, cmd_arg, line)
        elif cmd == 'vadd12':
            reg_no_arg(0xd0, cmd_arg, line)
        elif cmd == 'vsub12':
            reg_no_arg(0xd1, cmd_arg, line)
        elif cmd == 'vmul12':
            reg_no_arg(0xd2, cmd_arg, line)
        elif cmd == 'vdiv12':
            reg_no_arg(0xd3, cmd_arg, line)
        elif cmd == 'vmv31':
            reg_no_arg(0xc1, cmd_arg, line)
        elif cmd == 'vmv32':
            reg_no_arg(0xc2, cmd_arg, line)
        elif cmd == 'vcmp3':
            reg_no_arg(0xca, cmd_arg, line)
        else:
            raise WrongSyntaxError(f"Unknown command found in line: {line}.")

    @classmethod
    def parse_data(cls, mem_type: str, value: list[str]|None, line: int) -> None:
        if value is None:
            raise WrongSyntaxError(f"In line {line}: argument cannot be None.")

        new_vals = []
        for el in value:
            if el[0:2] == '0x':
                new_vals.append(int.from_bytes(bytes.fromhex(el[2:])))
            elif el.isdigit() or (el[0] == '-' and el[1:].isdigit()):
                new_vals.append(int(el))
            elif el[0] == "'" and el[-1] == "'":
                for el2 in el[1:-1]:
                    new_vals.append(ord(el2))
            elif el[0] == "'":
                raise WrongSyntaxError(f"In line {line}: argument cannot be contain a whitespace or unclosed quotes.")
            else:
                new_vals.append(el)

        if mem_type == '.byte':
            for el in new_vals:
                cls.data[cls.cur_addr_mem] = (el, 1)
                cls.cur_addr_mem += 1
        elif mem_type == '.word':
            for el in new_vals:
                cls.data[cls.cur_addr_mem] = (el, 4)
                cls.cur_addr_mem += 4
        else:
            raise WrongSyntaxError(f"Unknown data type find in line {line}.")

    @classmethod
    def parse_asm(cls, text: str) -> (dict[int, int], dict[int,int]):
        #split = text.lower().splitlines()
        split = text.splitlines()
        int_sec = None
        start = None
        cls.state = ParseState.No
        cls.labels = dict()
        cls.prog = dict()
        cls.data = dict()
        cls.cur_addr_mem = 0
        cls.cur_addr_cmem = 10
        for i in range(1, len(split) + 1):
            line = split[i - 1]
            parts = re.split(r"\s+", line)
            if len(parts) == 0:
                continue
            if parts[-1] == '':
                parts = parts[0:-1]
            if len(parts) == 0:
                continue
            if parts[0] == '':
                parts = parts[1:]
            if len(parts) == 0:
                continue
            elif len(parts) > 3 and cls.state != ParseState.SecData:
                raise WrongSyntaxError(f"Too match terms in line {i}.")

            elif parts[0] != '.section' and cls.state == ParseState.No:
                raise WrongSyntaxError(f"No section definition found in line {i}.")

            elif parts[0] == '.section':
                if parts[1] == 'int':
                    cls.state = ParseState.SecInt
                    if int_sec is not None:
                        raise WrongSyntaxError(f"Detected multiple int section definition in line {i}.")
                    int_sec = cls.cur_addr_cmem
                elif parts[1] == 'data':
                    cls.state = ParseState.SecData
                elif parts[1] == 'text':
                    cls.state = ParseState.SecText
                else:
                    raise WrongSyntaxError(f"Unknown section in line {i}.")

            elif parts[0] == '.org':
                if len(parts) != 2:
                    raise WrongSyntaxError(f"Wrong argument of .org in line {i}.")
                if parts[1][0:2] == '0x':
                    val = int.from_bytes(bytes.fromhex(parts[1][2:]))
                else:
                    val = int(parts[1])

                if cls.state == ParseState.SecInt or cls.state == ParseState.SecText:
                    cls.cur_addr_cmem = val
                elif cls.state == ParseState.SecData:
                    cls.cur_addr_mem = val

            elif parts[0][-1] == ':':
                if parts[0][:-1] == 'start':
                    if cls.state == ParseState.SecData:
                        raise WrongSyntaxError(f"Unexpected label 'start' in data section in line {i}.")
                    start = cls.cur_addr_cmem
                if cls.state == ParseState.SecText or cls.state == ParseState.SecInt:
                    cls.labels[parts[0][:-1]] = cls.cur_addr_cmem
                elif cls.state == ParseState.SecData:
                    cls.labels[parts[0][:-1]] = cls.cur_addr_mem

                if len(parts) > 1:
                    if cls.state == ParseState.SecInt or cls.state == ParseState.SecText:
                        Parser.parse_cmd(parts[1], parts[2] if len(parts) > 2 else None, i)
                    elif cls.state == ParseState.SecData:
                        Parser.parse_data(parts[1], parts[2:] if len(parts) > 2 else None, i)

            elif cls.state == ParseState.SecInt or cls.state == ParseState.SecText:
                Parser.parse_cmd(parts[0], parts[1] if len(parts) > 1 else None, i)
            elif cls.state == ParseState.SecData:
                Parser.parse_data(parts[0], parts[1:] if len(parts) > 1 else None, i)

        if start is None:
            raise WrongSyntaxError(f"No 'start' label found.")
        if int_sec is None:
            raise WrongSyntaxError(f"No 'int' section found.")

        res_mem = dict()
        for addr in cls.data:
            (val, size) = cls.data[addr]
            if val is None:
                cls.place_series(res_mem, addr, 0, size)

            if type(val) is int:
                cls.place_series(res_mem, addr, val, size)

            if type(val) is str:
                if val not in cls.labels:
                    raise WrongSyntaxError(f"Unknown label {val}.")
                cls.place_series(res_mem, addr, cls.labels[val], size)

        res_cmem = dict()
        for addr in cls.prog:
            (opcode, arg, size) = cls.prog[addr]
            res_cmem[addr] = opcode.to_bytes(1)[0]
            if type(arg) is int:
                cls.place_series(res_cmem, addr+1, arg, size)
            elif type(arg) is str:
                if arg not in cls.labels:
                    raise WrongSyntaxError(f"Unknown label {arg}.")
                cls.place_series(res_cmem, addr+1, cls.labels[arg], size)
        res_cmem[0] = 0x4B
        cls.place_series(res_cmem, 1, start, 4)
        res_cmem[5] = 0x4B
        cls.place_series(res_cmem, 6, int_sec, 4)
        # print("MEMORY:")
        # print("\n".join([f"{k}: {v}" for k,v in res_mem.items()]))
        # print("PROGRAM:")
        # print("\n".join([f"{k}: {v}" for k,v in res_cmem.items()]))
        return res_cmem, res_mem

    @classmethod
    def preprocessor(cls, txt: str) -> str:
        pre_res = ""
        txt_split = txt.splitlines()
        for l in txt_split:
            try:
                ind = l.index(';')
                pre_res += l[:ind]+"\n"
            except ValueError:
                pre_res += l+"\n"
        txt_split = pre_res.splitlines()

        in_define = False
        define_name = ""
        define_txt = ""
        defines = dict()
        pre_res_2 = ""
        for i in range(len(txt_split)):
            l = txt_split[i]

            l_split = re.split(r"\s+", l)
            if len(l_split) == 0:
                continue
            if l_split[-1] == '':
                l_split = l_split[0:-1]
            if len(l_split) == 0:
                continue
            if l_split[0] == '':
                l_split = l_split[1:]

            if '#define' in l:
                if len(l_split) != 2 or l_split[0] != '#define':
                    WrongSyntaxError(f"Wrong define usage in line {i+1}")
                if in_define:
                    WrongSyntaxError(f"Define in define in line {i + 1}")

                in_define = True
                define_name = l_split[1]

            elif '#enddefine' in l:
                if not in_define:
                    WrongSyntaxError(f"enddefine before define in line {i + 1}")

                if len(l_split) != 1 or l_split[0] != '#enddefine':
                    WrongSyntaxError(f"Wrong enddefine usage in line {i+1}")

                defines[define_name] = define_txt
                in_define = False
                define_txt = ""
                define_name = ""

            elif in_define:
                define_txt += l + "\n"



            else:
                pre_res_2 += l + "\n"
        txt_split = pre_res_2.splitlines()

        res = ""
        for i in range(len(txt_split)):
            l = txt_split[i]

            l_split = re.split(r"\s+", l)
            if len(l_split) == 0:
                continue
            if l_split[-1] == '':
                l_split = l_split[0:-1]
            if len(l_split) == 0:
                continue
            if l_split[0] == '':
                l_split = l_split[1:]

            if l_split[0] in defines:
                def_txt = defines[l_split[0]]
                for i2 in range(1,len(l_split)):
                    def_txt = def_txt.replace(f"${str(i2)}", l_split[i2])
                res += def_txt
            else:
                res += l + "\n"
        return res
