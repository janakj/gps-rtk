class UBloxStream():
    def __init__(self, ublox_queue):
        self._ublox_queue = ublox_queue

    def read(self, n=1):
        result = b""
        for i in range(n):
            result += self._ublox_queue.get() 
        return result

    def readline(self):
        byte = self._ublox_queue.get()
        result = byte
        while byte != b'\n':
            byte = self._ublox_queue.get()
            result += byte
        return result
