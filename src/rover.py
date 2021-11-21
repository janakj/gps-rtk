#!/usr/bin/env python3
import logging
from threading import Thread
from serial import Serial
from ublox import StreamMuxDemux, UBXSerializer


log = logging.getLogger('rover')


def rtcm_handler(rtcm_stream):
    xbee_stream = Serial("/dev/xbee", 115200, timeout=5)
    while True:
        byte = xbee_stream.read()
        rtcm_stream.write(byte)


def nmea_handler(nmea_stream):
    # create a bluetooth transmitter
    BLUETOOTH_PORT = '/dev/rfcomm0'
    bluetooth_stream = Serial(BLUETOOTH_PORT, 115200, timeout=5)

    # send nmea over bluetooth
    while True:
        byte = nmea_stream.read()
        bluetooth_stream.write(byte)


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
