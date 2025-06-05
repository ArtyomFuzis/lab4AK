import unittest

from cpu.modules import ExternalDevice1, ExternalDevice2


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
