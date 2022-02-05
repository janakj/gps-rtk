#!/usr/bin/env python3
import sys
import serial
import io
from datetime import datetime, timedelta
from enum import Enum, unique
from threading import Thread, RLock
from queue import Queue, Empty
from time import sleep
from pymitter import EventEmitter
import argparse
import base64

MAX_PAYLOAD_SIZE = 230

# EVENT=0,0 : boot
# EVENT=0,1 : factory reset
# EVENT=1,1 : JOIN succesful
# EVENT=2,2 : retransmission

# AT+PUTXB
# AT+PUTXT
# AT+PUTX

# AT+PCTXB
# AT+PCTXT
# AT+PCTX

# AT+RSSITH
# AT+ADRACK
# AT+CHMAS
# AT+RFPARI
# AT+DEVSTATUS
# AT+UART
# AT+PORT
# AT+MCAST
# AT+DELAY


@unique
class LoRaBand(Enum):
    AS923 = 0
    AU915 = 1
    EU868 = 5
    KR920 = 6
    IN865 = 7
    US915 = 8


@unique
class LoRaMode(Enum):
    ABP  = 0
    OTAA = 1


@unique
class LoRaNetwork(Enum):
    PRIVATE = 0
    PUBLIC  = 1


@unique
class LoRaDataRateEU868(Enum):
    SF12_125 = 0
    SF11_125 = 1
    SF10_125 = 2
    SF9_125  = 3
    SF8_125  = 4
    SF7_125  = 5
    SF7_250  = 6
    FSK_50   = 7


@unique
class LoRaDataRateUS915(Enum):
    SF10_125  = 0
    SF9_125   = 1
    SF8_125   = 2
    SF7_125   = 3
    SF8_500   = 4
    SF12_500  = 8
    SF11_500  = 9
    SF10_500  = 10
    SF9_500   = 11
    SF8_500_2 = 12
    SF7_500   = 13


@unique
class LoRaClass(Enum):
    CLASS_A = 0
    CLASS_B = 1
    CLASS_C = 2


class LoRaModule(EventEmitter):
    def __init__(self, filename, speed=19200, debug=False, on_message=None):
        super().__init__(self)
        self.filename = filename
        self.speed = speed
        self.debug = debug
        self.prev_at = None


    def open(self, timeout=5):
        self.port = serial.Serial(self.filename, self.speed)
        self.port.flushInput()
        self.port.flushOutput()
        self.response = Queue()

        self.lock = RLock()
        self.thread = Thread(target=self.reader)
        self.thread.daemon = True
        self.thread.start()


    def close(self):
        self.port.close()


    def read_line(self):
        line = ''
        while True:
            c = self.port.read(1).decode()
            if len(c) == 0:
                raise Exception('No data')
            if c == '\r' or c == '\n':
                if len(line) == 0:
                    continue
                return line
            line += c


    def reader(self):
        try:
            while True:
                data = self.read_line()
                if self.debug:
                    print('> %s' % data)
                try:
                    if data.startswith('+EVENT'):
                        payload = data[7:]
                        if len(payload) == 0:
                            self.emit('event', [])
                        else:
                            self.emit('event', tuple(map(int, payload.split(','))))
                    elif data.startswith('+ANS'):
                        self.emit('answer', tuple(map(int, data[5:].split(','))))
                    elif data.startswith('+ACK'):
                        self.emit('ack', True)
                    elif data.startswith('+NOACK'):
                        self.emit('ack', False)
                    elif data.startswith('+RECV'):
                        port, size = tuple(map(int, data[6:].split(',')))
                        data = self.port.read(size + 3)
                        self.emit('message', port, data[3:])
                    elif data.startswith('+OK') or data.startswith('+ERR'):
                        self.response.put_nowait(data)
                    else:
                        if self.debug:
                            print('Unsupported message received: %s' % data)
                except Exception as error:
                    print('Ignoring reader thread error: %s' % error)
        finally:
            if self.debug:
                print('Terminating reader thread')


    def at(self, cmd, flush=True):
        # Implement rudimentary AT command throttling. Without this the Murata firmware in the LoRa modem occasionally fails to process AT commands.
        now = datetime.now()
        if self.prev_at is not None:
            if now - self.prev_at < timedelta(milliseconds=100):
                sleep(0.01)
        self.prev_at = now

        if cmd is not None:
            cmd = '+%s' % cmd
        else:
            cmd = ''

        self.port.write(('AT%s\r' % cmd).encode())
        if flush:
            self.port.flush()
        if self.debug:
            print('< AT%s' % cmd)


    def wait_for_reply(self, timeout=None):
        try:
            reply = self.response.get(timeout=timeout)
        except Empty:
            raise TimeoutError('No reply received')
        try:
            if reply.startswith('+ERR'):
                raise Exception('Command failed: %s' % reply)
            elif reply.startswith('+OK'):
                if len(reply) > 3:
                    return reply[4:]
            else:
                raise Exception('Invalid response')

        finally:
            self.response.task_done()


    def invoke(self, cmd, timeout=10):
        with self.lock:
            self.at(cmd)
            return self.wait_for_reply(timeout=timeout)


    def wait_for_event(self, event, timeout=None):
        q = Queue()
        cb = lambda data: q.put_nowait(data)
        self.once(event, cb)
        try:
            data = q.get(timeout=timeout)
            q.task_done()
            return data
        except Empty:
            self.off(event, cb)
            raise TimeoutError('Timed out')


    @property
    def deveui(self):
        return self.invoke('DEVEUI?')

    @deveui.setter
    def deveui(self, val):
        return self.invoke('DEVEUI=%s' % val)

    @property
    def appeui(self):
        return self.invoke('APPEUI?')

    @appeui.setter
    def appeui(self, val):
        return self.invoke('APPEUI=%s' % val)

    @property
    def devaddr(self):
        return self.invoke('DEVADDR?')

    @devaddr.setter
    def devaddr(self, val):
        return self.invoke('DEVADDR=%s' % val)

    @property
    def netid(self):
        return self.invoke('NETID?')

    @netid.setter
    def netid(self, val):
        return self.invoke('NETID=%s' % val)

    @property
    def band(self):
        return LoRaBand(int(self.invoke('BAND?')))

    @band.setter
    def band(self, val):
        return self.invoke('BAND=%d' % val.value)

    @property
    def mode(self):
        return LoRaMode(int(self.invoke('MODE?')))

    @mode.setter
    def mode(self, val):
        return self.invoke('MODE=%d' % val.value)

    @property
    def adr(self):
        return self.invoke('ADR?') == '1'

    @adr.setter
    def adr(self, val):
        return self.invoke('ADR=%d' % (1 if val is True else 0))

    @property
    def dr(self):
        return int(self.invoke('DR?'))

    @dr.setter
    def dr(self, val):
        return self.invoke('DR=%d' % val.value)

    @property
    def nwk(self):
        return LoRaNetwork(int(self.invoke('NWK?')))

    @nwk.setter
    def nwk(self, val):
        return self.invoke('NWK=%d' % val.value)

    @property
    def nwkskey(self):
        return self.invoke('NWKSKEY?')

    @nwkskey.setter
    def nwkskey(self, val):
        return self.invoke('NWKSKEY=%s' % val)

    @property
    def appskey(self):
        return self.invoke('APPSKEY?')

    @appskey.setter
    def appskey(self, val):
        return self.invoke('APPSKEY=%s' % val)

    @property
    def appkey(self):
        return self.invoke('APPKEY?')

    @appkey.setter
    def appkey(self, val):
        return self.invoke('APPKEY=%s' % val)

    @property
    def joindc(self):
        # JOINDC is in the firmware 1.1.06 and higher
        # +ERR=-1 case is there for older firmwares
        # +ERR=-14 case is there for 1.1.06 in case modem has set MODE=0 (ABP)
        # +ERR=-17 case command is not supported in current band
        return self.invoke('JOINDC?')

    @joindc.setter
    def joindc(self, val):
        return self.invoke('JOINDC=%d' % (1 if val is True else 0))

    @property
    def class_(self):
        return LoRaClass(int(self.invoke('CLASS?')))

    @class_.setter
    def class_(self, val):
        return self.invoke('CLASS=%d' % val.value)

    @property
    def rfq(self):
        return map(float, self.invoke('RFQ?').split(','))

    @property
    def ver(self):
        return self.invoke('VER?').split(',')

    @property
    def dev(self):
        return self.invoke('DEV?')

    @property
    def rx2(self):
        return map(int, self.invoke('RX2?').split(','))

    @property
    def rep(self):
        "Unconfirmed retries"
        return int(self.invoke('REP?'))

    @rep.setter
    def rep(self, val):
        "Unconfirmed retries"
        return self.invoke('REP=%d' % val)

    @property
    def rtynum(self):
        "Confirmed retries"
        return int(self.invoke('RTYNUM?'))

    @rtynum.setter
    def rtynum(self, val):
        "Confirmed retries"
        return self.invoke('RTYNUM=%d' % val)

    @property
    def maxeirp(self):
        return int(self.invoke('MAXEIRP?'))

    @maxeirp.setter
    def maxeirp(self, val):
        return self.invoke('MAXEIRP=%d' % val)

    @property
    def rfpower(self):
        return map(int, self.invoke('RFPOWER?').split(','))

    @rfpower.setter
    def rfpower(self, val):
        return self.invoke('MAXEIRP=%d,%d' % (val[0], val[1]))

    @property
    def frmcnt(self):
        "Frame counters, returns [uplink, downlink]"
        return map(int, self.invoke('FRMCNT?').split(','))


    def reset(self):
        '''Initialize the LoRa modem into a known state.

        This method performs reboot, checks that the AT command interface is
        present and can be used.
        '''
        # Send CR in case there is some data in buffers
        self.port.write('\r'.encode())
        self.port.flush()

        # Read any input from the device until we time out
        while True:
            try:
                line = self.response.get(timeout=0.2)
                self.response.task_done()
            except Empty:
                break

        # Reboot the device and wait for it to signal that it has rebooted with
        # an event.
        self.reboot()

        # It seems we need to wait a bit for the modem to initialize after reboot
        sleep(0.1)

        # Invoke empty AT command to make sure the AT command interface is working
        self.invoke(None)

        self.dformat = False

        try:
            self.joindc = False
        except:
            pass


    def reboot(self):
        with self.lock:
            self.invoke('REBOOT')
            self.wait_for_event('event')


    def check_link(self, timeout=10):
        '''Perform a link check.

        Returns a tuple of two integers on success and None if no reply was
        received from the LoRa network. The first element in the tuple
        represents link margin. The second element represents the number of
        gateways that heard the packet.

        None is returned if no response was received from the LoRa network.

        If the operation times out, the function will raise an exception.
        '''
        q = Queue()
        cb = lambda d: q.put_nowait(d)
        self.once('event', cb)
        self.once('answer', cb)
        try:
            with self.lock:
                self.invoke('LNCHECK')
                event = q.get(timeout=timeout)
                if event[1] == 1:
                    rc, margin, count = q.get(timeout=0.2)
                    if rc != 2:
                        raise Exception('Invalid answer code')
                    return (margin, count)
        finally:
            self.off('event', cb)
            self.off('answer', cb)


    def join(self, timeout=60):
        with self.lock:
            self.invoke('JOIN')
            status = self.wait_for_event('event', timeout=timeout)
            if status != (1, 1):
                raise Exception('JOIN failed')


    def send(self, port, data, confirmed=False, timeout=None):
        type = 'C' if confirmed else 'U'
        with self.lock:
            self.at('P%sTX %d,%d' % (type, port, len(data)), flush=False)
            self.port.write(data)
            self.port.write('\r'.encode())
            self.port.flush()
            self.wait_for_reply()
            if confirmed:
                return self.wait_for_event('ack', timeout=timeout)


    def factory_reset(self):
        return self.invoke('FACNEW')




def main():
    parser = argparse.ArgumentParser(description='LoRa driver')
    parser.add_argument('action', type=str, nargs='?', help='Optional action to perform, one of: trx, join, link, session')
    parser.add_argument('--device', type=str, default='/dev/serial0', help='Special filename of the device')
    parser.add_argument('--speed', type=int, default=19200, help='Serial port baud rate')
    parser.add_argument('--debug', action='store_true', help='Enable debugging')
    args = parser.parse_args()

    device = LoRaModule(args.device, args.speed, debug=args.debug)

    device.open()
    device.reset()
    if args.debug:
        print('Found device type %s, firmware %s, DevEUI %s' % (device.dev, device.ver[0], device.deveui))

    device.band   = LoRaBand.US915
    device.nwk    = LoRaNetwork.PUBLIC
    device.class_ = LoRaClass.CLASS_C
    device.dr     = LoRaDataRateUS915.SF7_125
    device.adr    = True
    device.rep    = 1
    device.rtynum = 8

    if args.action == None:
        print('Model=%s' % device.dev)
        print('Firmware=%s' % device.ver[0])
        print('NetID=%s' % device.netid)
        print('DevEUI=%s' % device.deveui)
        print('AppEUI=%s' % device.appeui)
        print('AppKey=%s' % device.appkey)
    elif args.action == 'trx':
        try:
            device.on('message', lambda port, data: print('%d:%s' % (port, base64.b64encode(data).decode())))
            for line in sys.stdin:
                port, confirmed, data = line.rstrip('\n').split(':')
                device.send(int(port), base64.b64decode(data), confirmed=confirmed.lower() == 'c')
        except KeyboardInterrupt:
            pass
    elif args.action == 'join':
        device.mode = LoRaMode.OTAA
        device.join()
    elif args.action == 'link':
        reply = device.check_link()
        print('link margin: %d, gateway count: %d' % reply)
    elif args.action == 'session':
        print('DevAddr=%s' % device.devaddr)
        print('NwkSKey=%s' % device.nwkskey)
        print('AppSKey=%s' % device.appskey)
    else:
        raise Exception('Unsupported action')

    device.close()


if __name__ == '__main__':
    main()
