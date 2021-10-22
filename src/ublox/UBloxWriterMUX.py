from queue import Queue
from threading import Thread

class UBloxWriterMUX:
    def __init__(self, serial):
        self._serial = serial
        self._q = Queue()

        self._writer_thread = Thread(target=self._write_from_queue)
        self._writer_thread.daemon = True
        self._writer_thread.start()

    def _write_from_queue(self):
        while True:
            msg = self._q.get()
            self._serial.write(msg)

    def writeNMEA(self, data):
        self._q.put(data)

    def writeUBX(self, data):
        self._q.put(data)

    def writeRTCM(self, data):
        self._q.put(data)
