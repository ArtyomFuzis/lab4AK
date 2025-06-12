from cpu.components import DataBus, Register, MultiPlex, ALU, DeviceControlUnitInput, Latch, DeviceControlUnitOutput, \
    MemoryUnit, SimpleAction, BiAction, InstructionDecoder
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
        self.ar = Register(self.b_alu_out, self.b_ar, 4)

        self.l_ac = self.ac.get_control_latch()
        self.l_ar = self.ar.get_control_latch()

        self.mux = MultiPlex(self.b_alu_choice,self.b_alu_inp2, 4)
        self.mux.bind_inp(0, self.b_cr_arg)
        self.mux.bind_inp(1, self.b_mem_out)
        self.mux.bind_inp(2, self.b_ar)

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

class MainControlUnit:
    def __init__(self, datapath: MainDataPath, cmem: SharedMemory):
        self.dp = datapath
        self.l_cv_call = lambda: None

        self.b_pc_choice = DataBus(1)
        self.b_cr_choice = DataBus(1)
        self.b_pc = DataBus(4)
        self.b_pc_new = DataBus(4)
        self.b_cmd = DataBus(5)
        self.b_cdata = DataBus(5)
        self.b_ra = DataBus(4)
        self.b_cv_nxt = DataBus(4)
        self.b_cv_state = DataBus(1)

        self.ra = Register(self.b_pc, self.b_ra, 4)
        self.pc = Register(self.b_pc_new, self.b_pc, 4)
        self.cr = Register(self.b_cdata, self.b_cmd, 5)

        self.l_ra = self.ra.get_control_latch()
        self.l_pc = self.pc.get_control_latch()
        self.l_cr = self.cr.get_control_latch()

        self.l_cv = Latch(lambda: self.l_cv_call())

        const_0_1 = DataBus(1)
        const_0_1.bind_provider(lambda: (0).to_bytes(1))
        const_0_5 = DataBus(5)
        const_0_5.bind_provider(lambda: (0).to_bytes(5))
        self.cmu = MemoryUnit(const_0_1, self.b_pc, const_0_5, self.b_cdata, cmem, 5)
        self.l_cdata = self.cmu.get_control_latch()

        b_pc_2 = DataBus(4)
        b_pc_1 = DataBus(4)
        b_pc_0 = DataBus(4)
        self.sa_pc_0 = SimpleAction(self.b_pc, b_pc_0, lambda x: (int.from_bytes(x, signed=False)+5).to_bytes(4, signed=False))
        self.sa_pc_1 = SimpleAction(self.b_pc, b_pc_1, lambda x: (int.from_bytes(x, signed=False)+3).to_bytes(4, signed=False))
        self.sa_pc_2 = SimpleAction(self.b_pc, b_pc_2, lambda x: (int.from_bytes(x, signed=False)+1).to_bytes(4, signed=False))

        self.mux_pc = MultiPlex(self.b_pc_choice, self.b_pc_new, 4)
        self.mux_pc.bind_inp(0, b_pc_0)
        self.mux_pc.bind_inp(1, b_pc_1)
        self.mux_pc.bind_inp(2, b_pc_2)
        self.mux_pc.bind_inp(3, self.b_ra)
        self.mux_pc.bind_inp(4, self.dp.b_cr_arg)

        b_cr_arg_0 = DataBus(4)
        b_cr_arg_1 = DataBus(4)

        self.sa_cr_1 = SimpleAction(self.b_cmd, b_cr_arg_1, lambda x: x[1:5])
        self.ba_cr_0 = BiAction(self.b_pc, self.b_cmd,b_cr_arg_0, lambda a,b: (int.from_bytes(a, signed=False)+int.from_bytes(b[1:3], signed=True)).to_bytes(4, signed=False))

        self.mx_cr_arg = MultiPlex(self.b_cr_choice, self.dp.b_cr_arg, 4)
        self.mx_cr_arg.bind_inp(0, b_cr_arg_0)
        self.mx_cr_arg.bind_inp(1, b_cr_arg_1)

        self.id = InstructionDecoder(
            self.l_pc,
            self.l_cdata,
            self.l_cr,
            self.l_ra,
            self.dp.l_data,
            self.dp.l_ac,
            self.dp.l_ar,
            self.l_cv,
            self.b_cmd,
            self.b_pc_choice,
            self.b_cr_choice,
            self.dp.b_alu_choice,
            self.dp.b_alu_op,
            self.dp.b_alu_flag,
            self.dp.b_data_op,
            self.dp.b_int_got,
            self.dp.b_int_allow,
            self.b_cv_nxt,
            self.b_cv_state
        )







