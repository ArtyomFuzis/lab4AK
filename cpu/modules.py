from cpu.components import DataBus, Register, MultiPlex, ALU, DeviceControlUnitInput, Latch, DeviceControlUnitOutput, \
    MemoryUnit
from cpu.utils import SharedMemory


class ExternalDevice1:
    def __init__(self, l_io_in: Latch):
        self.l_io_in = l_io_in
        self.b_io_d_1 = DataBus(4)
        self.b_io_r_1 = DataBus(1)
        self.b_to_reg = DataBus(4)
        self.data1 = Register(self.b_to_reg, self.b_io_d_1, 4)
        self.l_reg = self.data1.get_control_latch()
        self.cu = DeviceControlUnitInput(self.b_to_reg, self.l_reg, self.b_io_r_1, self.l_io_in)

class ExternalDevice2:
    def __init__(self):
        self.b_io_d_2 = DataBus(4)
        self.b_io_r_2 = DataBus(1)
        self.b_from_reg = DataBus(4)
        self.data2 = Register(self.b_io_d_2, self.b_from_reg, 4)
        self.l_reg = self.data2.get_control_latch()
        self.cu = DeviceControlUnitOutput(self.b_from_reg, self.l_reg, self.b_io_r_2)
        self.l_io_out = self.cu.get_control_latch()

class MainDataPath:
    def __init__(self, mem: SharedMemory):
        self.b_alu_ac = DataBus(4)
        self.b_alu_op = DataBus(1)
        self.b_alu_inp2 = DataBus(4)
        self.b_alu_flag = DataBus(1)
        self.b_alu_out = DataBus(4)
        self.b_alu_choice = DataBus(1)
        self.b_ar = DataBus(4)
        self.b_mem_out = DataBus(4)
        self.b_cr_arg = DataBus(4)
        self.b_data_op = DataBus(1)

        self.ac = Register(self.b_alu_out, self.b_alu_ac, 4)
        self.l_ac = self.ac.get_control_latch()
        self.ar = Register(self.b_alu_out, self.b_ar, 4)

        self.l_ar = self.ar.get_control_latch()
        self.mux = MultiPlex(self.b_alu_choice,self.b_alu_inp2, 4)
        self.mux.bind_inp(0, self.b_ar)
        self.mux.bind_inp(1, self.b_mem_out)
        self.mux.bind_inp(2, self.b_cr_arg)

        self.alu = ALU(self.b_alu_op, self.b_alu_ac, self.b_alu_inp2, self.b_alu_flag, self.b_alu_out)

        self.mu = MemoryUnit(self.b_data_op, self.b_ar, self.b_alu_out, self.b_mem_out, mem)
        self.l_data = self.mu.get_control_latch()

        self.ex1 = ExternalDevice1(self.mu.get_input_latch())
        self.ex2 = ExternalDevice2()
        self.mu.bind_input_io(self.ex1.b_io_d_1, self.ex1.b_io_r_1)
        self.mu.bind_output_io(self.ex2.b_io_d_2, self.ex2.b_io_r_2, self.ex2.l_io_out)

        self.b_int_got = DataBus(1)
        self.b_int_allow = DataBus(1)
        self.mu.bind_int_buses(self.b_int_got, self.b_int_allow)




