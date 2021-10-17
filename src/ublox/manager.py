from .TMODE3 import TMODE3
from .UBloxStreamDEMUX import UBloxStreamDEMUX
from pyubx2 import UBXReader

class UBloxManager:
    def __init__(self, serial, ttl):
        stream_demux = UBloxStreamDEMUX(serial, ttl, serial.timeout)
        self._nmea_stream = stream_demux.NMEAStream()
        self._ubx_stream = stream_demux.UBXStream()
        self._rtcm_stream = stream_demux.RTCMStream()

        # TODO: MUX for writing
        ubr = UBXReader(self._ubx_stream)
        self.TMODE3 = TMODE3(serial, ubr)
    
    def NMEAStream(self):
        return self._nmea_stream
    
    def UBXStream(self):
        return self._ubx_stream
    
    def RTCMStream(self):
        return self._rtcm_stream
