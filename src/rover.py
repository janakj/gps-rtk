#!/usr/bin/env python3
import logging
from threading import Thread
from serial import Serial
from pyubx2 import UBXReader
from ublox import StreamMuxDemux, UBXSerializer
from bluetooth import BluetoothTransmitter


log = logging.getLogger('rover')


def rtcm_handler(rtcm_stream):
    # TODO:
    xbee_stream = Serial("/dev/xbee", 115200, timeout=5)
    while True:
        byte = xbee_stream.read()
        rtcm_stream.write(byte)


def nmea_handler(nmea_stream):
    # TODO:
    # create a bluetooth transmitter
    BLUETOOTH_PORT = '/dev/rfcomm0'
    log.info(f'Creating Bluetooth transmitter on {BLUETOOTH_PORT}')
    bluetooth = BluetoothTransmitter(BLUETOOTH_PORT)

    # send nmea over bluetooth
    while True:
        msg = nmea_stream.readline()
        msg = msg.strip()
        bluetooth.onNMEA(msg)

def ubx_handler(ubx_stream):
    ubr = UBXReader(ubx_stream)
    while True:
        raw, msg = ubr.read()
        print(msg)


def main():
    # connect to serial port
    PORT = "/dev/gps-uart1"
    BAUDRATE = 460800
    TIMEOUT = 5
    log.info(f'Connecting to serial port {PORT}')
    original_stream = Serial(PORT, BAUDRATE, timeout=TIMEOUT)

    # split serial stream into a stream for each protocol
    log.info(f'Splitting serial stream into a stream for each protocol')
    streams = StreamMuxDemux(original_stream)

    # load configuration
    CONFIG_FILE = open("./config/rover.yml", "r")
    log.info(f'Loading configuration from {CONFIG_FILE}')
    config = UBXSerializer.serialize(CONFIG_FILE)
    streams.UBX.write(config)
    # TODO: verify ubx answer
    ubr = UBXReader(streams.UBX)

    # run UBX thread
    log.info(f'Creating a thread for handling UBX')
    ubx_thread = Thread(target=ubx_handler, args=[streams.UBX])
    ubx_thread.start()

    # run RTCM thread
    log.info(f'Creating a thread for handling RTCM')
    rtcm_thread = Thread(target=rtcm_handler, args=[streams.RTCM])
    rtcm_thread.start()

    # run NMEA thread
    log.info(f'Creating a thread for handling NMEA')
    nmea_thread = Thread(target=nmea_handler, args=[streams.NMEA])
    nmea_thread.start()


if __name__ == '__main__':
    logging.basicConfig(format="%(levelname)s:%(name)s:%(asctime)s:  %(message)s", level=logging.DEBUG)
    main()
