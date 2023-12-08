# This is a sample Python script.
import time
from datetime import datetime
from types import SimpleNamespace
from typing import List, Tuple, Iterable, Union

import serial
from functools import reduce
from enum import Enum
from threading import Thread
import logging

logging.basicConfig(level=logging.DEBUG)


class ChargeMode(Enum):
    ccv = 'CCV'  # Charge Constant current/U
    dcc = 'DCC'  # Discharge Constant current
    dcp = 'DCP'  # Discharge Constant power
    r   = 'R'    # Measure R


class Stdoutwriter:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.messages = """fa 02 00 00 10 8e 00 14 00 00 02 14 01 a0 00 64 09 52 f8 
fa 02 00 00 10 8e 00 14 00 00 02 14 01 a0 00 64 09 52 f8 
fa 0c 00 00 10 8e 00 00 00 00 02 14 01 a0 00 96 09 ba f8 
fa 0c 00 8f 10 96 00 00 00 00 02 14 01 a0 00 96 09 2d f8 
fa 0c 00 c3 10 a0 00 01 00 00 02 14 01 a0 00 96 09 56 f8 
fa 0c 00 c8 10 a0 00 02 00 00 02 14 01 a0 00 96 09 5e f8 
fa 0c 00 cc 10 a0 00 03 00 00 02 14 01 a0 00 96 09 5b f8 
fa 0c 00 ce 10 a0 00 05 00 00 02 14 01 a0 00 96 09 5f f8 
fa 0c 00 d1 10 a0 00 06 00 00 02 14 01 a0 00 96 09 43 f8 
fa 0c 00 d2 10 a0 00 07 00 00 02 14 01 a0 00 96 09 41 f8 
fa 0c 00 d4 10 a0 00 08 00 00 02 14 01 a0 00 96 09 48 f8 
fa 0c 00 d6 10 a0 00 09 00 00 02 14 01 a0 00 96 09 4b f8 
fa 0c 00 d7 10 a0 00 0a 00 00 02 14 01 a0 00 96 09 49 f8 
fa 0c 00 d8 10 a0 00 0c 00 00 02 14 01 a0 00 96 09 40 f8 
fa 0c 00 d9 10 a0 00 0d 00 00 02 14 01 a0 00 96 09 40 f8 
fa 0c 00 da 10 a0 00 0e 00 00 02 14 01 a0 00 96 09 40 f8 
fa 0c 00 db 10 a0 00 0f 00 00 02 14 01 a0 00 96 09 40 f8 
fa 0c 00 dc 10 a0 00 10 00 00 02 14 01 a0 00 96 09 58 f8 
fa 0c 00 dd 10 a0 00 12 00 00 02 14 01 a0 00 96 09 5b f8 
fa 0c 00 de 10 a0 00 13 00 00 02 14 01 a0 00 96 09 59 f8 
fa 0c 00 df 10 a0 00 14 00 00 02 14 01 a0 00 96 09 5f f8 
fa 0c 00 df 10 a0 00 15 00 00 02 14 01 a0 00 96 09 5e f8 
fa 0c 00 df 10 a0 00 17 00 00 02 14 01 a0 00 96 09 5c f8 
fa 0c 00 e0 10 a0 00 18 00 00 02 14 01 a0 00 96 09 6c f8 
fa 0c 00 e0 10 a0 00 19 00 00 02 14 01 a0 00 96 09 6d f8 
fa 0c 00 e1 10 a0 00 1a 00 00 02 14 01 a0 00 96 09 6f f8 
fa 0c 00 e1 10 a0 00 1c 00 00 02 14 01 a0 00 96 09 69 f8 
fa 0c 00 e1 10 a0 00 1d 00 00 02 14 01 a0 00 96 09 68 f8 
fa 0c 00 e1 10 a0 00 1e 00 00 02 14 01 a0 00 96 09 6b f8 
fa 0c 00 e1 10 a0 00 1f 00 00 02 14 01 a0 00 96 09 6a f8 
fa 0c 00 e1 10 a0 00 21 00 00 02 14 01 a0 00 96 09 54 f8 
fa 0c 00 e1 10 a0 00 22 00 00 02 14 01 a0 00 96 09 57 f8 
fa 0c 00 e1 10 a0 00 23 00 00 02 14 01 a0 00 96 09 56 f8 
fa 0c 00 e1 10 a0 00 24 00 00 02 14 01 a0 00 96 09 51 f8 
fa 0c 00 e1 10 a0 00 26 00 00 02 14 01 a0 00 96 09 53 f8 
fa 0c 00 e1 10 a0 00 27 00 00 02 14 01 a0 00 96 09 52 f8 
fa 0c 00 e1 10 a0 00 28 00 00 02 14 01 a0 00 96 09 5d f8 
fa 0c 00 e1 10 a0 00 29 00 00 02 14 01 a0 00 96 09 5c f8 
fa 0c 00 e1 10 a0 00 2b 00 00 02 14 01 a0 00 96 09 5e f8 
fa 0c 00 e1 10 a0 00 2c 00 00 02 14 01 a0 00 96 09 59 f8 
fa 0c 00 e1 10 a0 00 2d 00 00 02 14 01 a0 00 96 09 58 f8 
fa 0c 00 e1 10 a0 00 2e 00 00 02 14 01 a0 00 96 09 5b f8 
fa 0c 00 e1 10 a0 00 30 00 00 02 14 01 a0 00 96 09 45 f8 
fa 0c 00 e0 10 a0 00 31 00 00 02 14 01 a0 00 96 09 45 f8 
fa 16 00 df 10 a0 00 32 00 00 02 14 01 a0 00 96 09 77 f8 
fa 02 00 df 10 a0 00 32 00 00 02 14 01 a0 00 96 09 77 f8 
""".split('\n')
        self.dummy_in = b''

    def write(self, data: bytes) -> None:
        self.logger.info(" ".join('{:02x}'.format(b) for b in data))

    def read(self, length: int) -> bytes:
        if len(self.dummy_in) == 0:
            if len(self.messages) == 0:
                time.sleep(10)
                return b''
            else:
                msg = self.messages.pop(0)
                self.dummy_in = bytes(int(c, 16) for c in msg.split())
        time.sleep(0.02)
        reply = self.dummy_in[:length]
        self.dummy_in = self.dummy_in[length:]
        return reply


class EBC:
    def __init__(self, tty: str = '/dev/ttyACM0'):
        if tty == '-':
            self.io = Stdoutwriter()
        else:
            self.io = serial.Serial(port=tty, baudrate=9600)
        self.reader = Thread(target=self.read_func, daemon=True)
        self.curr = SimpleNamespace()
        self.done = True

    def _interpret(self, d: bytes) -> bool:
        if len(d) < 17: return False
        id = int(d[0])
        # First part of message is always the same
        self.curr = SimpleNamespace()
        self.curr.i = self._d2ti(d[1:3])     # mA
        self.curr.u = self._d2i(d[3:5])      # mV
        if id < 10:
            self.curr.state = 'idle'
        elif id < 20:
            self.curr.state = 'active'
        else:
            self.curr.state = 'done'
            self.done = True
        if id in (2, 12, 22):
            self.curr.mode = ChargeMode.ccv
        elif id in (0, 10, 20):
            self.curr.mode = ChargeMode.dcc
        elif id in (1, 11, 21):
            self.curr.mode = ChargeMode.dcp

        self.curr.q = self._d2i(d[5:7])  # mAh
        self.curr.x1 = self._d2i(d[7:9])  # ?
        if self.curr.mode in [ChargeMode.ccv, ChargeMode.dcc]:
            self.curr.i_s = self._d2ti(d[9:11])  # soll mA
        elif self.curr.mode == ChargeMode.dcp:
            self.curr.p_s = self._d2i(d[9:11])     # soll P (W)
        self.curr.u_s = self._d2ti(d[11:13]) # soll mV
        self.curr.x2 = self._d2i(d[13:15])   # ?
        self.curr.t = self._d2i(d[15:17])    # T?

        self.dumpState()
        return True

    def dumpState(self) -> None:
        p = self.curr.i * self.curr.u / 1000000.0
        d = "%s (%s) %imAh / %imWh  %imV / %imA %.2fW" % \
          (self.curr.mode, self.curr.state, self.curr.q,  self.curr.x1, self.curr.u, self.curr.i, p)
        d += " --> "
        if hasattr(self.curr, 'i_s'):
            d += " %imA" % self.curr.i_s
        d += " %imV %i %i" % (self.curr.u_s, self.curr.x1, self.curr.t)
        logging.debug(d)

    def read_func(self):
        logger = logging.getLogger('RX')
        while True:
            # Wait for start
            while True:
                if self.io.read(1) == b'\xfa':
                    break
            datagram = b''
            while True:
                b = self.io.read(1)
                if b == b'\xf8':
                    break
                datagram += b
            logger.info(" ".join('{:02x}'.format(b) for b in datagram))
            self._interpret(datagram)

    def connect(self) -> None:
        # fa 05 00 00 00 00 00 00 05 f8
        self.send((5,0,0,0,0,0,0))
        self.reader.start()

    def disconnect(self) -> None:
        # fa 05 00 00 00 00 00 00 05 f8
        self.send((6,0,0,0,0,0,0))

    def stop(self) -> None:
        # fa 05 00 00 00 00 00 00 05 f8
        self.send((2,0,0,0,0,0,0))
        self.done = True

    def measure_r(self, i:int) -> None:
        # fa 05 00 00 00 00 00 00 05 f8
        self.send([9] + self._i2d(i//10) + [0,0,0,0])

    def send(self, data: Iterable[int]) -> None:
        d = list(data)
        crc = reduce(lambda a, b: a ^ b, d)
        datagram = bytes([250] + d + [crc, 248])
        self.io.write(datagram)

    @staticmethod
    def _i2d(n: int) -> List[int]:
        """Convert value to data"""
        n = n//10
        return [n // 240, n % 240]

    @staticmethod
    def _d2i(d: Union[Tuple[int, int], bytes]) -> int:
        """Convert tuple to value"""
        return d[0] * 240 + d[1]

    @staticmethod
    def _d2ti(d) -> int:
        return 10 * EBC._d2i(d)

    def charge(self, mode: ChargeMode, u: int, i: int, istop: int) -> None:
        # fa 21 02 14 01 78 00 32 7c f8
        self.done = False
        self.begin = datetime.now()
        logging.debug("Start at: " + self.begin.strftime('%X'))
        if mode == ChargeMode.ccv:
            data = [33] + self._i2d(i) + self._i2d(u) + self._i2d(istop)
            self.send(data)

    def wait(self):
        while True:
            time.sleep(1)
            if self.done:
                break
        end = datetime.now()
        logging.debug("Start at: " + end.strftime('%X'))
        logging.debug("Duration: " + str(end-self.begin))


if __name__ == '__main__':
    from argparse import ArgumentParser
    arg = ArgumentParser()
    arg.add_argument('--port', '-p', required=False, default='/dev/ttyACM0')
    args = arg.parse_args()
    e = EBC(tty=args.port)
    e.connect()

    print("Charging..")
    e.charge(ChargeMode.ccv, u=3700, i=5000, istop=500)