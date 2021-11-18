#!/usr/bin/env python3
import logging
from threading import Thread
from serial import Serial
from pyubx2 import UBXReader
from ublox import StreamMuxDemux, UBXSerializer


log = logging.getLogger('base')


def rtcm_handler(rtcm_stream):
    # TODO:
    xbee_stream = Serial("/dev/xbee", 115200, timeout=5)
    while True:
        byte = rtcm_stream.read()
        xbee_stream.write(byte)

def nmea_handler(nmea_stream):
    while True:
        print(nmea_stream.readline())
        
def ubx_handler(ubx_stream):
    ubr = UBXReader(ubx_stream)
    while True:
        raw, msg = ubr.read()
        print(msg)
        

def main():
    # connect to serial port
    PORT = "/dev/cu.usbserial-A50285BI"
    BAUDRATE = 460800
    TIMEOUT = 5
    log.info(f'Connecting to serial port {PORT}')
    original_stream = Serial(PORT, BAUDRATE, timeout=TIMEOUT)

    # split serial stream into a stream for each protocol
    log.info(f'Splitting serial stream into a stream for each protocol')
    streams = StreamMuxDemux(original_stream)

    # load configuration
    CONFIG_FILE = "./config/base.yml"
    log.info(f'Loading configuration from {CONFIG_FILE}')
    config = UBXSerializer.serialize(open(CONFIG_FILE, "r"))
    streams.UBX.write(config)
    # TODO: verify ubx answer
    # ubr = UBXReader(streams.UBX)

    # run UBX thread
    log.info(f'Creating a thread for handling UBX')
    ubx_thread = Thread(target=ubx_handler, args=[streams.UBX])
    ubx_thread.start()

    # run NMEA thread
    log.info(f'Creating a thread for handling NMEA')
    nmea_thread = Thread(target=nmea_handler, args=[streams.NMEA])
    nmea_thread.start()

    # run RTCM thread
    log.info(f'Creating a thread for handling RTCM')
    rtcm_thread = Thread(target=rtcm_handler, args=[streams.RTCM])
    rtcm_thread.start()



if __name__ == '__main__':
    logging.basicConfig(format="%(levelname)s:%(name)s:%(asctime)s:  %(message)s", level=logging.DEBUG)
    main()
