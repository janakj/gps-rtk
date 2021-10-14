from .TMODE3 import TMODE3
from .UART1 import UART1
from pyubx2 import UBXReader

class UBloxManager:
    def __init__(self, serial):
        ubr = UBXReader(serial)
        self.TMODE3 = TMODE3(serial, ubr)
        self.UART1 = UART1(serial, ubr)
    