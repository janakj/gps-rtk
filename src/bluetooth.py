#
# This file implements a simple Bluetooth transmitter that transmits NMEA
# messages over a Bluetooth serial connection.
#
import logging
import serial
from queue import Queue, Full, Empty
from threading import Thread


log = logging.getLogger(__name__)


# def compute_NMEA_checksum(data):
#     v = 0
#     for c in data:
#         # v = v ^ ord(c)
#         v = v ^ c
#     return '{:02X}'.format(v)


def wrap(data):
    # csum = compute_NMEA_checksum(data)
    #return data + b'*' + csum.encode('utf-8') + b'\r\n'
    # return f'${data}*{csum}\r\n'
    return data + b'\r\n'

class BluetoothTransmitter(Thread):
    def __init__(self, port, queue_size=64, write_timeout=1):
        self.write_timeout = write_timeout
        self.port_filename = port
        self.queue = Queue(maxsize=queue_size)
        self.port = None
        self.shutting_down = False
        Thread.__init__(self)


    def _open_port(self):
        if self.port is not None:
            raise Exception('Serial port is already open')

        try:
            log.debug(f'Opening port {self.port_filename}')
            self.port = serial.Serial(self.port_filename, exclusive=True, write_timeout=self.write_timeout)
        except Exception as e:
            log.debug(f'Open error: {e}')


    def _close_port(self):
        if self.port is None:
            raise Exception('Serial port is not open')

        log.debug(f'Closing port {self.port_filename}')

        try:
            self.port.reset_input_buffer()
            self.port.reset_output_buffer()
        except:
            pass

        try:
            self.port.close()
        except Exception as e:
            log.debug(f'close error: {e}')
        finally:
            self.port = None


    def _flush_queue(self):
        while True:
            try:
                self.queue.get(block=False)
                self.queue.task_done()
            except Empty:
                break


    def _send(self, msg):
        if self.port is None:
            self._open_port()

        if self.port is None:
            self._flush_queue()
            return

        try:
            self.port.write(msg)
        except Exception as e:
            log.debug(f'Write error: {e.__context__ if e.__context__ else e}')
            self._close_port()
            self._flush_queue()


    def run(self):
        log.info('Starting Bluetooth transmitter')
        try:
            while True:
                if self.shutting_down:
                    break

                data = self.queue.get()
                try:
                    if data is None:
                        break
                    self._send(wrap(data))
                finally:
                    self.queue.task_done()
        finally:
            log.debug('Bluetooth trasmitter is terminating')
            if self.port:
                self._close_port()



    def onNMEA(self, data):
        try:
            self.queue.put(data, block=False)
        except Full:
            log.warning('Bluetooth transmitter queue is full')


    def shutdown(self):
        log.info('Asking Bluetooth trasmitter to terminate')

        self.shutting_down = True
        self.queue.put(None, block=False)

        # Wait for the thread to terminate
        self.join()
        log.info('Bluetooth transmitter terminated')
