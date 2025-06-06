import unittest

from cpu.modules import ExternalDevice1, ExternalDevice2, MainDataPath
from cpu.utils import SharedMemory


class IODevicesTestCase(unittest.TestCase):
    def setUp(self):
        self.device_out = ExternalDevice2()
        self.device_in = ExternalDevice1(self.device_out.l_io_out)
        self.device_in.b_io_r_1.bind_provider(self.device_out.b_io_r_2.get_data)
        self.device_out.b_io_d_2.bind_provider(self.device_in.b_io_d_1.get_data)

    def test_simple_io(self):
        self.device_in.cu.post_data((123).to_bytes(4))
        self.assertEqual(123,int.from_bytes(self.device_out.cu.get_data()))

    def test_three_values_io(self):
        self.device_in.cu.post_data((-123).to_bytes(4, signed=True))
        self.assertEqual(-123, int.from_bytes(self.device_out.cu.get_data(), signed=True))
        self.device_in.cu.post_data((145654234).to_bytes(4))
        self.assertEqual(145654234, int.from_bytes(self.device_out.cu.get_data()))
        self.device_in.cu.post_data((0).to_bytes(4))
        self.assertEqual(0, int.from_bytes(self.device_out.cu.get_data()))

    def test_unbind_and_wait(self):
        self.device_in.b_io_r_1.unbind_provider()
        self.device_in.b_io_r_1.bind_provider(lambda: (0).to_bytes(1))
        self.device_in.cu.post_data((11).to_bytes(4, signed=True))
        self.assertEqual(None, self.device_out.cu.get_data())
        self.device_in.cu.post_data((34214).to_bytes(4, signed=True))
        self.assertEqual(None, self.device_out.cu.get_data())
        self.device_in.cu.post_data((8990).to_bytes(4, signed=True))
        self.assertEqual(None, self.device_out.cu.get_data())
        self.device_in.b_io_r_1.unbind_provider()
        self.device_in.b_io_r_1.bind_provider(lambda: (1).to_bytes(1))
        self.device_in.cu.post_data()
        self.device_in.cu.post_data()
        self.assertEqual(11, int.from_bytes(self.device_out.cu.get_data(), signed=True))
        self.assertEqual(34214, int.from_bytes(self.device_out.cu.get_data(), signed=True))
        self.assertEqual(None, self.device_out.cu.get_data())
        self.device_in.cu.post_data()
        self.assertEqual(8990, int.from_bytes(self.device_out.cu.get_data(), signed=True))
        self.assertEqual(None, self.device_out.cu.get_data())
        self.device_in.cu.post_data()
        self.assertEqual(None, self.device_out.cu.get_data())

class MainDataPathTestCase(unittest.TestCase):
    def setUp(self):
        self.mem = SharedMemory()
        self.dp = MainDataPath(self.mem)

        self.b_alu_op = (0).to_bytes(1, signed=False)
        self.b_cr_arg = (0).to_bytes(4, signed=True)
        self.b_data_op = (0).to_bytes(1, signed=False)
        self.b_alu_choice = (0).to_bytes(1, signed=False)
        self.latch_ac = self.dp.l_ac.perform
        self.latch_ar = self.dp.l_ar.perform
        self.latch_data = self.dp.l_data.perform

        self.dp.b_alu_op.bind_provider(lambda: self.b_alu_op)
        self.dp.b_cr_arg.bind_provider(lambda: self.b_cr_arg)
        self.dp.b_data_op.bind_provider(lambda: self.b_data_op)
        self.dp.b_alu_choice.bind_provider(lambda: self.b_alu_choice)


    def test_inc(self):
        self.b_alu_op = (8).to_bytes(1, signed=False)
        self.b_cr_arg = (4567829).to_bytes(4, signed=True)
        self.b_alu_choice = (2).to_bytes(1, signed=False)
        self.latch_ac()
        self.assertEqual(4567829, int.from_bytes(self.dp.b_alu_ac.get_data(), signed=True))

        self.b_alu_op = (12).to_bytes(1, signed=False)
        self.latch_ac()
        self.assertEqual(4567833, int.from_bytes(self.dp.b_alu_ac.get_data(), signed=True))

        self.b_alu_op = (8).to_bytes(1, signed=False)
        self.b_cr_arg = (0x0021).to_bytes(4, signed=True)
        self.b_alu_choice = (2).to_bytes(1, signed=False)
        self.latch_ar()
        self.assertEqual(0x0021, int.from_bytes(self.dp.b_ar.get_data(), signed=False))

        self.b_alu_op = (7).to_bytes(1, signed=False)
        self.b_data_op = (1).to_bytes(1, signed=False)
        self.latch_data()
        self.assertEqual(4567833, int.from_bytes(self.dp.ex2.cu.get_data(), signed=True))

        self.b_alu_op = (0b00100111).to_bytes(1, signed=False)
        self.latch_ac()
        self.assertEqual(4567834, int.from_bytes(self.dp.b_alu_ac.get_data(), signed=True))

        self.b_alu_op = (7).to_bytes(1, signed=False)
        self.b_data_op = (1).to_bytes(1, signed=False)
        self.latch_data()
        self.assertEqual(4567834, int.from_bytes(self.dp.ex2.cu.get_data(), signed=True))

    def load_mem_cr_addr(self, addr: int):
        self.b_alu_op = (8).to_bytes(1, signed=False)
        self.b_cr_arg = addr.to_bytes(4, signed=True)
        self.b_alu_choice = (2).to_bytes(1, signed=False)
        self.latch_ar()
        self.b_data_op = (0).to_bytes(1, signed=False)
        self.latch_data()

    def test_store_plus(self):
        self.mem.arr[0x0050:0x0054] = (0x00000060).to_bytes(4, signed=True)
        self.dp.b_int_allow.bind_provider(lambda: (1 ^ int.from_bytes(self.dp.b_int_got.get_data())).to_bytes(1))
        self.dp.ex1.cu.post_data((4686).to_bytes(4, signed=True))
        self.dp.ex1.cu.post_data((-785432).to_bytes(4, signed=True))

        self.load_mem_cr_addr(0x0020)

        self.b_alu_op = (8).to_bytes(1, signed=False)
        self.b_alu_choice = (1).to_bytes(1, signed=False)
        self.latch_ac()
        self.assertEqual(4686, int.from_bytes(self.dp.b_alu_ac.get_data(), signed=True))

        self.load_mem_cr_addr(0x0050)

        self.b_alu_op = (8).to_bytes(1, signed=False)
        self.b_alu_choice = (1).to_bytes(1, signed=False)
        self.latch_ar()
        self.assertEqual(0x0060, int.from_bytes(self.dp.b_ar.get_data(), signed=True))

        self.b_alu_op = (7).to_bytes(1, signed=False)
        self.b_data_op = (1).to_bytes(1, signed=False)
        self.latch_data()
        self.assertEqual(4686, int.from_bytes(self.mem.arr[0x0060:0x0064] , signed=True))

        self.load_mem_cr_addr(0x0050)

        self.b_alu_op = (14).to_bytes(1, signed=False)
        self.b_alu_choice = (1).to_bytes(1, signed=False)
        self.b_data_op = (1).to_bytes(1, signed=False)
        self.latch_data()
        self.assertEqual(0x0064, int.from_bytes(self.mem.arr[0x0050:0x0054], signed=True))





