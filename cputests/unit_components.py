import unittest

from cpu.components import DataBus, MemoryUnit, Latch, Register, MultiPlex


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








