from .TMODE3 import TMODE3
from pyubx2 import UBXReader

class UBloxManager:
    def __init__(self, serial):
        ubr = UBXReader(serial)
        self.TMODE3 = TMODE3(serial, ubr)
    