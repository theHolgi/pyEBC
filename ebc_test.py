import unittest
from unittest.mock import MagicMock, patch
from ebc import *


class MyTestCase(unittest.TestCase):
   def setUp(self):
      serial.Serial = MagicMock()

   @staticmethod
   def message(data: List[int]) -> bytes:
      crc = reduce(lambda a, b: a ^ b, data)
      return bytes([250] + data + [crc, 248])

   @staticmethod
   def framed(data: bytes) -> bytes:
      crc = reduce(lambda a, b: a ^ b, data)
      return b'\xfa' + data + bytes([crc]) + b'\xf8'

   def mock_send(self, data):
      self.data = data

   def test_convert(self):
      self.assertEqual([15, 100], EBC._i2d(3700))
      self.assertEqual([4, 40], EBC._i2td(10000))

      self.assertEqual(1234, EBC._d2i((5, 34)))
      self.assertEqual(500, EBC._d2ti((0, 50)))

   def test_connect(self):
      e = EBC()
      e.connect()
      e.io.write.assert_called_once_with(self.framed(b'\5\0\0\0\0\0\0'))

   def test_disconnect(self):
      e = EBC()
      e.disconnect()
      e.io.write.assert_called_once_with(self.framed(b'\6\0\0\0\0\0\0'))

   def test_stop(self):
      e = EBC()
      e.stop()
      e.io.write.assert_called_once_with(self.framed(b'\2\0\0\0\0\0\0'))

   def test_measure_r(self):
      e = EBC()
      i = 2000
      e.measure_r(i)
      e.io.write.assert_called_once_with(self.framed(b'\x09' + bytes(EBC._i2td(i)) + b'\0\0\0\0'))

   def test_start_ccv(self):
      e = EBC()
      u, i, i_s = 4000, 10000, 1000
      e.charge(ChargeMode.ccv, u=u, i=i, istop=1000)
      e.io.write.assert_called_once_with(self.framed(b'\x21' + bytes(EBC._i2d(i)) + bytes(EBC._i2td(u)) + bytes(EBC._i2td(i_s))))

   def test_start_dcp(self):
      e = EBC()
      u, p = 3000, 400
      e.charge(ChargeMode.dcp, u=u, p=p)
      e.io.write.assert_called_once_with(self.framed(b'\x11' + bytes(EBC._i2d(p)) + bytes(EBC._i2td(u)) + b'\0\0'))

   def test_start_dcc(self):
      e = EBC()
      u, i = 3000, 20000
      e.charge(ChargeMode.dcc, u=u, i=i)
      e.io.write.assert_called_once_with(self.framed(b'\1' + bytes(EBC._i2td(i)) + bytes(EBC._i2td(u)) + b'\0\0'))

   def test_status_ccv(self):
      e = EBC()
      e._interpret(b'\x0c\x02\x14\x0e\x60\x00\x0a\x00\x00\x02\x14\x01\x78\x00\x32\x09\xc0')
      self.assertEqual(e.curr.mode, ChargeMode.ccv)
      self.assertEqual(e.curr.state, 'active')
      self.assertEqual(e.curr.i, 5000)
      self.assertEqual(e.curr.u, 3456)
      self.assertEqual(e.curr.i_s, 5000)
      self.assertEqual(e.curr.u_s, 3600)

   def test_status_dcp(self):
      e = EBC()
      e._interpret(b'\x0b\x02\x9c\x10\x5b\x00\x21\x00\x00\x00\x19\x01\x99\x00\x00\x09\x77')
      self.assertEqual(e.curr.mode, ChargeMode.dcp)
      self.assertEqual('active', e.curr.state)
      self.assertEqual(6360, e.curr.i)
      self.assertEqual(3931, e.curr.u)
      self.assertEqual(25, e.curr.p_s)
      self.assertEqual(3930, e.curr.u_s)

if __name__ == '__main__':
   unittest.main()
