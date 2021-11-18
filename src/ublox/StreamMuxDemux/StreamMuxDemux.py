from .UBloxReaderDEMUX import UBloxReaderDEMUX
from .UBloxWriterMUX import UBloxWriterMUX
from .UBloxStream import UBloxStream


class StreamMuxDemux:
    def __init__(self, serial, ttl=1):
        readerDEMUX = UBloxReaderDEMUX(serial, ttl, serial.timeout)
        writerMUX = UBloxWriterMUX(serial)
        self._nmea = UBloxStream(readerDEMUX.readNMEA, writerMUX.writeNMEA)
        self._ubx = UBloxStream(readerDEMUX.readUBX, writerMUX.writeUBX)
        self._rtcm = UBloxStream(readerDEMUX.readRTCM, writerMUX.writeRTCM)

    @property
    def UBX(self):
        return self._ubx

    @property
    def NMEA(self):
        return self._nmea

    @property
    def RTCM(self):
        return self._rtcm
