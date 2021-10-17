from .TMODE3 import TMODE3
from .UBloxStreamDEMUX import UBloxStreamDEMUX
from pyubx2 import UBXReader

class UBloxManager:
    def __init__(self, serial, ttl):
        stream_demux = UBloxStreamDEMUX(serial, ttl, serial.timeout)
        nmea_stream = stream_demux.NMEAStream()
        ubx_stream = stream_demux.UBXStream()
        rtcm_stream = stream_demux.RTCMStream()

        # TODO: MUX for writing
        ubr = UBXReader(ubx_stream)
        self.TMODE3 = TMODE3(serial, ubr)
    