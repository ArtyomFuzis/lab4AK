import unittest

from cpu.components import DataBus, MemoryUnit, Latch, Register, MultiPlex, ALU


class MemoryUnitTestCase(unittest.TestCase):
    def setUp(self):
        b_ar = DataBus(4)
        b_mem_out = DataBus(4)
        b_data_op = DataBus(1)
        b_alu_out = DataBus(4)
        data_memory_unit = MemoryUnit(b_data_op, b_ar, b_alu_out, b_mem_out)
        l_ctrl = data_memory_unit.get_control_latch()
        self.exec = l_ctrl.perform
        self.perf = lambda: b_mem_out.get_data()
        self.addr = (0).to_bytes(4)
        self.inp = (0).to_bytes(4)
        self.op = (0).to_bytes(1)
        b_ar.bind_provider(lambda: self.addr)
        b_alu_out.bind_provider(lambda: self.inp)
        b_data_op.bind_provider(lambda: self.op)


    def test_rw(self):
        self.addr = (215).to_bytes(4)
        self.op = (1).to_bytes(1)
        self.inp = (1023).to_bytes(4)
        self.exec()
        self.op = (0).to_bytes(1)
        self.exec()
        self.assertEqual(1023, int.from_bytes(self.perf()))
        self.addr = (216).to_bytes(4)
        self.exec()
        self.assertEqual( 261888, int.from_bytes(self.perf()))

    def test_zero(self):
        self.exec()
        self.assertEqual(0, int.from_bytes(self.perf()))

class RegisterTestCase(unittest.TestCase):
    def setUp(self):
        b_alu_out = DataBus(4)
        b_alu_ac = DataBus(4)
        ac = Register(b_alu_out, b_alu_ac,4)
        l_ctrl = ac.get_control_latch()
        self.exec = l_ctrl.perform
        self.inp = (0).to_bytes(4)
        b_alu_out.bind_provider(lambda: self.inp)
        self.perf = lambda: b_alu_ac.get_data()

    def test_rw(self):
        self.inp = (-8956432).to_bytes(4,signed = True)
        self.exec()
        self.assertEqual(-8956432, int.from_bytes(self.perf(), signed=True))

    def test_zero(self):
        self.exec()
        self.assertEqual(0, int.from_bytes(self.perf(), signed=True))

class MultiPlexTestCase(unittest.TestCase):
    def setUp(self):
        b_alu_choice = DataBus(2)
        b_alu_inp2 = DataBus(4)
        b_ar = DataBus(4)
        b_mem_out = DataBus(4)
        b_cr_arg = DataBus(4)
        mx = MultiPlex(b_alu_choice, b_alu_inp2, 4)
        self.inp1 = (125).to_bytes(4,signed = True)
        self.inp2 = (-125).to_bytes(4,signed = True)
        self.inp3 = (145656).to_bytes(4,signed = True)
        self.choice = (0).to_bytes(2)
        self.perf = b_alu_inp2.get_data
        b_ar.bind_provider(lambda: self.inp1)
        b_mem_out.bind_provider(lambda: self.inp2)
        b_cr_arg.bind_provider(lambda: self.inp3)
        b_alu_choice.bind_provider(lambda: self.choice)
        mx.bind_inp(0, b_ar)
        mx.bind_inp(1, b_mem_out)
        mx.bind_inp(2, b_cr_arg)

    def test_choice0(self):
        self.choice = (0).to_bytes(2)
        self.assertEqual(125, int.from_bytes(self.perf(), signed=True))

    def test_choice1(self):
        self.choice = (1).to_bytes(2)
        self.assertEqual(-125, int.from_bytes(self.perf(),signed=True))

    def test_choice2(self):
        self.choice = (2).to_bytes(2)
        self.assertEqual(145656, int.from_bytes(self.perf(), signed=True))

    def test_change(self):
        self.inp1 = (5).to_bytes(4,signed = True)
        self.inp2 = (9).to_bytes(4,signed = True)
        self.choice = (0).to_bytes(2)
        self.assertEqual(5, int.from_bytes(self.perf(), signed=True))
        self.choice = (1).to_bytes(2)
        self.assertEqual(9, int.from_bytes(self.perf(), signed=True))

class ALUTestCase(unittest.TestCase):

    def setUp(self):
        b_alu_ac = DataBus(4)
        b_alu_inp2 = DataBus(4)
        b_alu_op = DataBus(1)
        b_alu_flag = DataBus(1)
        b_alu_out = DataBus(4)
        ALU(b_alu_op, b_alu_ac, b_alu_inp2, b_alu_flag, b_alu_out)
        self.inp1 = (1025).to_bytes(4,signed = True)
        self.inp2 = (-333).to_bytes(4, signed=True)
        self.op = (0b00000000).to_bytes(4, signed=True)
        b_alu_ac.bind_provider(lambda: self.inp1)
        b_alu_inp2.bind_provider(lambda: self.inp2)
        b_alu_op.bind_provider(lambda: self.op)
        self.perf = lambda: (int.from_bytes(b_alu_out.get_data(), signed=True), int.from_bytes(b_alu_flag.get_data()))

    def test_add(self):
        self.inp1 = (5).to_bytes(4,signed = True)
        self.inp2 = (-2).to_bytes(4,signed = True)
        self.op = (0b00000000).to_bytes(1)
        res = self.perf()
        self.assertEqual(0b1000, res[1])
        self.assertEqual(3, res[0])

    def test_add_neg(self):
        self.inp1 = (5).to_bytes(4, signed=True)
        self.inp2 = (36).to_bytes(4, signed=True)
        self.op = (0b11000000).to_bytes(1)
        res = self.perf()
        self.assertEqual(0b0010, res[1])
        self.assertEqual(-41, res[0])

    def test_add_over(self):
        self.inp1 = (2147483647).to_bytes(4, signed=True)
        self.inp2 = (2).to_bytes(4, signed=True)
        self.op = (0b00000000).to_bytes(1)
        res = self.perf()
        self.assertEqual(0b0110, res[1])
        self.assertEqual(-2147483647, res[0])

    def test_sub(self):
        self.inp1 = (-1).to_bytes(4, signed=True)
        self.inp2 = (50).to_bytes(4, signed=True)
        self.op = (0b00000001).to_bytes(1)
        res = self.perf()
        self.assertEqual(0b1010, res[1])
        self.assertEqual(-51, res[0])

    def test_sub_zero(self):
        self.inp1 = (-1).to_bytes(4, signed=True)
        self.inp2 = (-1).to_bytes(4, signed=True)
        self.op = (0b00000001).to_bytes(1)
        res = self.perf()
        self.assertEqual(0b1001, res[1])
        self.assertEqual(0, res[0])

    def test_mul(self):
        self.inp1 = (32543).to_bytes(4, signed=True)
        self.inp2 = (567).to_bytes(4, signed=True)
        self.op = (0b00000101).to_bytes(1)
        res = self.perf()
        self.assertEqual(0b0000, res[1])
        self.assertEqual(18451881, res[0])

    def test_mul_over(self):
        self.inp1 = (32543).to_bytes(4, signed=True)
        self.inp2 = (567000).to_bytes(4, signed=True)
        self.op = (0b00000101).to_bytes(1)
        res = self.perf()
        self.assertEqual(0b0100, res[1])
        self.assertEqual(1272011816, res[0])

    def test_rem(self):
        self.inp1 = (151515).to_bytes(4, signed=True)
        self.inp2 = (23).to_bytes(4, signed=True)
        self.op = (0b00000110).to_bytes(1)
        res = self.perf()
        self.assertEqual(0b0000, res[1])
        self.assertEqual(14, res[0])

    def test_div(self):
        self.inp1 = (151515).to_bytes(4, signed=True)
        self.inp2 = (23).to_bytes(4, signed=True)
        self.op = (0b00000100).to_bytes(1)
        res = self.perf()
        self.assertEqual(0b0000, res[1])
        self.assertEqual(6587, res[0])

    def test_div_neg_vals(self):
        self.inp1 = (-151515).to_bytes(4, signed=True)
        self.inp2 = (-24).to_bytes(4, signed=True)
        self.op = (0b00000100).to_bytes(1)
        res = self.perf()
        self.assertEqual(0b0000, res[1])
        self.assertEqual(6313, res[0])

    def test_left(self):
        self.inp1 = (-151515).to_bytes(4, signed=True)
        self.inp2 = (-24).to_bytes(4, signed=True)
        self.op = (0b00000111).to_bytes(1)
        res = self.perf()
        self.assertEqual(0b0010, res[1])
        self.assertEqual(-151515, res[0])

    def test_right(self):
        self.inp1 = (-151515).to_bytes(4, signed=True)
        self.inp2 = (-24).to_bytes(4, signed=True)
        self.op = (0b00001000).to_bytes(1)
        res = self.perf()
        self.assertEqual(0b0010, res[1])
        self.assertEqual(-24, res[0])

    def test_right_flags(self):
        self.inp1 = (-151515).to_bytes(4, signed=True)
        self.inp2 = (-24).to_bytes(4, signed=True)
        self.op = (0b11101000).to_bytes(1)
        res = self.perf()
        self.assertEqual(0b0000, res[1])
        self.assertEqual(23, res[0])

    def test_shift_l_simple(self):
        self.inp1 = (2).to_bytes(4, signed=True)
        self.inp2 = (2).to_bytes(4, signed=True)
        self.op = (0b00000010).to_bytes(1)
        res = self.perf()
        self.assertEqual(0b0000, res[1])
        self.assertEqual(8, res[0])


    def test_shift_l_neg(self):
        self.inp1 = (-18).to_bytes(4, signed=True)
        self.inp2 = (5).to_bytes(4, signed=True)
        self.op = (0b00000010).to_bytes(1)
        res = self.perf()
        self.assertEqual(0b1010, res[1])
        self.assertEqual(-576, res[0])

    def test_shift_r_simple(self):
        self.inp1 = (128).to_bytes(4, signed=True)
        self.inp2 = (5).to_bytes(4, signed=True)
        self.op = (0b00000011).to_bytes(1)
        res = self.perf()
        self.assertEqual(0b0000, res[1])
        self.assertEqual(4, res[0])

    def test_shift_r_neg(self):
        self.inp1 = (-100).to_bytes(4, signed=True)
        self.inp2 = (5).to_bytes(4, signed=True)
        self.op = (0b00000011).to_bytes(1)
        res = self.perf()
        self.assertEqual(0b0010, res[1])
        self.assertEqual(-4, res[0])

    def test_and(self):
        self.inp1 = (-1895).to_bytes(4, signed=True)
        self.inp2 = (41535).to_bytes(4, signed=True)
        self.op = (0b00001001).to_bytes(1)
        res = self.perf()
        self.assertEqual(0b0000, res[1])
        self.assertEqual(40985, res[0])

    def test_or(self):
        self.inp1 = (-1895).to_bytes(4, signed=True)
        self.inp2 = (41535).to_bytes(4, signed=True)
        self.op = (0b00001010).to_bytes(1)
        res = self.perf()
        self.assertEqual(0b0010, res[1])
        self.assertEqual(-1345, res[0])

    def test_xor(self):
        self.inp1 = (-1895).to_bytes(4, signed=True)
        self.inp2 = (41535).to_bytes(4, signed=True)
        self.op = (0b00001011).to_bytes(1)
        res = self.perf()
        self.assertEqual(0b0010, res[1])
        self.assertEqual(-42330, res[0])












