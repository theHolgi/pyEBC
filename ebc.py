#!/usr/bin/env python3
import re
import time
from datetime import datetime
from typing import List, Tuple, Iterable, Union, Callable

import serial
from functools import reduce
from enum import Enum
from threading import Thread, Event
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

        self.messages = [ ]
        with open("testdata.txt") as f:
            for line in f.readlines():
                if m := re.match(r"([\d:]+)\s+IRP_MJ_READ\s+UP\s+STATUS_SUCCESS\s+(.+)", line):
                    self.messages.append(m.groups())
        self.dummy_in = b''
        self.timestamp = datetime.strptime(self.messages[0][0], "%X")

    def write(self, data: bytes) -> None:
        self.logger.info(" ".join('{:02x}'.format(b) for b in data))

    def read(self, length: int) -> bytes:
        if len(self.dummy_in) == 0:
            if len(self.messages) == 0:
                time.sleep(10)
                return b''
            else:
                ts, msg = self.messages.pop(0)
                self.dummy_in = bytes(int(c, 16) for c in msg.split())
                self.timestamp = datetime.strptime(ts, "%X")
        time.sleep(0.02)
        reply = self.dummy_in[:length]
        self.dummy_in = self.dummy_in[length:]
        return reply

    def gettimestamp(self) -> datetime:
        return self.timestamp

class StateChecker:
    def __init__(self):
        self.state = 0

    def check(self, d: bytes) -> bool:
        ...

class RTestChecker(StateChecker):
    r = 0

    def check(self, d: bytes) -> bool:
        # id = int(d[0])
        if self.state == 0:  # 1st -> pre
            pass
        elif self.state == 1:
            i, u = EBC._d2i(d[1:3]), EBC._d2i(d[5:7])
            self.r = (u * 1000) / i
        elif self.state == 2:
            return True
        self.state += 1
        return False

    def result(self) -> float:
        return self.r


class ChargeChecker(StateChecker):
    def check(self, d: bytes) -> bool:
        if self.state == 0:
            if not (20 <= int(d[0]) <= 22 or 0 <= int(d[0]) <= 2):
                self.state += 1
            return False
        else:
            return 20 <= int(d[0]) <= 22 or 0 <= int(d[0]) <= 2


class EbcStatus:
    def __init__(self):
       self.u = 0
       self.i = 0
       self.q = 0
       self.p = 0
       self.u_s = 0
       self.i_s = 0
       self.p_s = 0

    def update_ist(self, u: int, i: int, q: int) -> None:
       self.u = u
       self.i = i
       self.q = q
       self.p = self.i * self.u / 1000

    def update_target(self, u: int, i: int=None, p: int=None) -> None:
       self.u_s = u
       self.i_s = i
       self.p_s = p


class EBC_Keepalive:
    def __init__(self, send_func):
        self.send_func = send_func
        self.pause = Event()
        self.keepalivetask = Thread(target=self.keepalive_func, daemon=True)
        self.hbcnt = 0

    def start(self) -> None:
        self.hbcnt = 0
        self.pause.clear()

    def stop(self) -> None:
        self.pause.set()

    def keepalive_func(self):
        while True:
            if not self.pause.is_set():
                self.send_func([10] + EBC._i2d(self.hbcnt) + [0, 0, 0, 0])
                self.hbcnt += 1
            time.sleep(60)


class EBC:
    models = {5: "EBC-A05", 6: "EBC-A10H", 9: "EBC-A20"}

    def __init__(self, tty: str = '/dev/ttyACM0'):
        if tty == '-':
            self.io = Stdoutwriter()
            self.gettimestamp = self.io.gettimestamp
        else:
            self.io = serial.Serial(port=tty, baudrate=9600, parity=serial.PARITY_EVEN, rtscts=True)
            self.gettimestamp = datetime.now
        self.keepalive = EBC_Keepalive(self.send)
        self.readertask = Thread(target=self.read_func, daemon=True)
        self.curr = EbcStatus()
        self.done = True
        self.last_rx = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.condition = None
        self.handler = None
        self.is_connected = False

    def set_eventhandler(self, cb = Callable[[EbcStatus], None]):
        self.handler = cb

    def set_checker(self, c: StateChecker) -> None:
        self.condition = c

    def _interpret(self, d: bytes) -> bool:
        if len(d) < 17: return False
        now = self.gettimestamp()
        id = int(d[0])
        # First part of message is always the same
        self.curr.update_ist(i=self._d2ti(d[1:3]), u=self._d2i(d[3:5]), q=self._d2i(d[5:7]))  # mA, mV, mAh
        if id < 10:
            self.curr.state = 'idle'
        elif id < 20:
            self.curr.state = 'active'
        elif id < 30:
            self.curr.state = 'done'
        if id in (2, 12, 22):
            self.curr.mode = ChargeMode.ccv
        elif id in (0, 10, 20):
            self.curr.mode = ChargeMode.dcc
        elif id in (1, 11, 21):
            self.curr.mode = ChargeMode.dcp

        self.curr.x1 = self._d2i(d[7:9])  # ?
        if id < 30:  # Ignore high messages with unknown upper payload
            if self.curr.mode in [ChargeMode.ccv, ChargeMode.dcc]:
                self.curr.update_target(u=self._d2ti(d[11:13]), i=self._d2ti(d[9:11]))  # soll mV, mA
            elif self.curr.mode == ChargeMode.dcp:
                self.curr.update_target(u=self._d2ti(d[11:13]), p=self._d2i(d[9:11]))     # soll mV, W
            self.curr.x2 = self._d2i(d[13:15])   # ?
        self.curr.model = self.models[int(d[15])]

        if self.last_rx is None:
            self.curr.qw = 0
        else:
            dT = now - self.last_rx
            dQ = self.curr.p * dT.total_seconds() / 3600
            self.curr.qw += dQ
        self.last_rx = now
        self.dumpState()
        if self.handler is not None:
            self.handler(self.curr)
        return True

    def dumpState(self) -> None:
        p = self.curr.i * self.curr.u / 1000000.0
        d = f"{self.curr.model} {self.curr.mode if self.curr.state == 'active' else 'idle'} {self.curr.q}mAh / {self.curr.qw:.0f}mWh  {self.curr.u}mV / {self.curr.i}mA {p:.2f}W"
        d += " --> "
        if hasattr(self.curr, 'i_s'):
            d += " %imA" % self.curr.i_s
        d += " %imV %i" % (self.curr.u_s, self.curr.x1)
        logging.debug(d)

    def read_func(self):
        logger = logging.getLogger('RX')
        self.last_rx = None
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
            if self.condition is not None:
                if self.condition.check(datagram):
                    self.logger.info("DONE!")
                    self.done = True

    def connect(self) -> None:
        # fa 05 00 00 00 00 00 00 05 f8
        self.send((5,0,0,0,0,0,0))
        self.readertask.start()
        self.is_connected = True

    def disconnect(self) -> None:
        # fa 05 00 00 00 00 00 00 05 f8
        self.send((6,0,0,0,0,0,0))
        self.is_connected = False

    def stop(self) -> None:
        # fa 05 00 00 00 00 00 00 05 f8
        self.keepalive.stop()
        self.send((2,0,0,0,0,0,0))
        self.done = True

    def measure_r(self, i:int) -> int:
        # fa 09 00 64 00 00 00 00 6d f8
        self.begin = self.gettimestamp()
        self.send([9] + self._i2td(i) + [0, 0, 0, 0])
        self.set_checker(RTestChecker())
        self.wait()
        return self.condition.result()

    def send(self, data: Iterable[int]) -> None:
        d = list(data)
        crc = reduce(lambda a, b: a ^ b, d)
        datagram = bytes([250] + d + [crc, 248])
        logger = logging.getLogger('TX')
        logger.debug(" ".join('{:02x}'.format(b) for b in datagram))
        self.io.write(datagram)

    @staticmethod
    def _i2d(n: int) -> List[int]:
        """Convert value to data"""
        return [n // 240, n % 240]

    @staticmethod
    def _i2td(n: int) -> List[int]:
        return EBC._i2d(n//10)
        
    @staticmethod
    def _d2i(d: Union[Tuple[int, int], bytes]) -> int:
        """Convert tuple to value"""
        return d[0] * 240 + d[1]

    @staticmethod
    def _d2ti(d) -> int:
        return 10 * EBC._d2i(d)

    def charge(self, mode: ChargeMode, u: int, i: int = None, istop: int = None, p: int = None) -> None:
        # fa 21 02 14 01 78 00 32 7c f8
        self.done = False
        self.begin = self.gettimestamp()
        self.curr.state = "init"
        logging.debug("Start at: " + self.begin.strftime('%X'))
        if mode == ChargeMode.ccv:
            if i is None or u is None or istop is None:
                raise ValueError("Required parameters for CCV charge; U, I, ISTOP")
            data = [33] + self._i2d(i) + self._i2td(u) + self._i2td(istop)
            self.send(data)
        if mode == ChargeMode.dcp:
            if p is None and i is not None:
                p = u * i // 1000
            if u is None or p is None:
                raise ValueError("Required parameters for CP discharge; U, P or I")
            data = [17] + self._i2d(p) + self._i2td(u) + self._i2d(0)
            self.send(data)
        if mode == ChargeMode.dcc:
            if u is None or i is None:
                raise ValueError("Required parameters for CC discharge; U, I")
            data = [1] + self._i2td(i) + self._i2td(u) + self._i2d(0)
            self.send(data)
        self.keepalive.start()
        self.set_checker(ChargeChecker())

    def wait(self) -> None:
        self.done = False
        while True:
            time.sleep(5)
            if self.done:
                break
        end = self.gettimestamp()
        logging.debug("Start at: " + end.strftime('%X'))
        logging.debug("Duration: " + str(end - self.begin))


if __name__ == '__main__':
    from argparse import ArgumentParser
    arg = ArgumentParser()
    arg.add_argument('--port', '-p', required=False, default='/dev/ttyACM0')
    args = arg.parse_args()
    e = EBC(tty=args.port)
    e.connect()

    print("Charging..")
    e.charge(ChargeMode.ccv, u=3700, i=5000, istop=500)
