from .TMODE3 import TMODE3
from .MSG import MSG

from .UBloxReaderDEMUX import UBloxReaderDEMUX
from .UBloxWriterMUX import UBloxWriterMUX
from .UBloxStream import UBloxStream

from pyubx2 import UBXReader

class UBloxManager:
    def __init__(self, serial, ttl):
        # split serial streams into separate stream for each protocol
        readerDEMUX = UBloxReaderDEMUX(serial, ttl, serial.timeout)
        writerMUX = UBloxWriterMUX(serial)
        self._nmea_stream = UBloxStream(readerDEMUX.readNMEA, writerMUX.writeNMEA)
        self._ubx_stream = UBloxStream(readerDEMUX.readUBX, writerMUX.writeUBX)
        self._rtcm_stream = UBloxStream(readerDEMUX.readRTCM, writerMUX.writeRTCM)

        # UBX reader
        ubr = UBXReader(self._ubx_stream)

        # TMODE3
        self.TMODE3 = TMODE3(self._ubx_stream, ubr)
    
        # MSG
        self.MSG = MSG(self._ubx_stream, ubr)
    
    def getNMEAStream(self):
        return self._nmea_stream
    
    def getUBXStream(self):
        return self._ubx_stream
    
    def getRTCMStream(self):
        return self._rtcm_stream
