import sys

from cpu.modules import MainDataPath, MainControlUnit
from cpu.utils import SharedMemory

if __name__ == '__main__':
    if len(sys.argv) not in (2, 3):
        print("Usage: main.py <source path> [memory_limit]")
        sys.exit(1)

    with open(sys.argv[1]+'.cmem', 'rb') as f:
        cmem_read = f.read()

    with open(sys.argv[1]+'.mem', 'rb') as f:
        mem_read = f.read()

    mem_size = 32768
    if len(sys.argv) == 3:
        try:
            mem_size = int(sys.argv[2])
        except ValueError:
            print("Unable to parse memory limit, it should be an integer")
            sys.exit(1)

    mem = SharedMemory(mem_size)
    cmem = SharedMemory(mem_size)
    mem.load_to_mem([list(mem_read)])
    cmem.load_to_mem([list(cmem_read)])
    dp = MainDataPath(mem)
    cu = MainControlUnit(dp, cmem)
    for i in range(1000):
        if cu.id.stop:
            break
        cu.id.tick()
        print(f"ac: {dp.b_alu_ac.get_data().hex()} ar: {dp.b_ar.get_data().hex()} pc: {cu.b_pc.get_data().hex()} cr: {cu.b_cmd.get_data().hex()} flags: {dp.b_flg.get_data().hex()}")
    for i in range(14):
        print(chr(dp.ex2.cu.get_data()[-1]), end='')

