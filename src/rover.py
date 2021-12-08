#!/usr/bin/env python3
import logging
from threading import Thread
from time import sleep
from serial import Serial
from ublox import StreamMuxDemux, UBXSerializer, StreamMuxDemuxError
from pyubx2.ubxreader import UBXReader


log = logging.getLogger('rover')
REPLUG_WAIT_TIME = 3


def rtcm_handler(rtcm_stream):
    xbee_stream = None
    while True:
        try:
            xbee_stream = Serial("/dev/xbee", 115200, timeout=5)
            while True:
                byte = xbee_stream.read()
                rtcm_stream.write(byte)

        except StreamMuxDemuxError as e:
            log.error(e)
            rtcm_stream.owner.close()
            return
        
        except Exception as e:
            log.error(e)
            if xbee_stream:
                xbee_stream.close()
            sleep(REPLUG_WAIT_TIME)



def nmea_handler(nmea_stream):
    bluetooth_stream = None
    while True:
        try:
            bluetooth_stream = Serial('/dev/rfcomm0', 115200, timeout=5)
            while True:
                byte = nmea_stream.read()
                bluetooth_stream.write(byte)

        except StreamMuxDemuxError as e:
            log.error(e)
            nmea_stream.owner.close()
            return

        except Exception as e:
            log.error(e)
            if bluetooth_stream:
                bluetooth_stream.close()
            sleep(REPLUG_WAIT_TIME)


def ubx_handler(ubx_stream):
    while True:
        try:
            ubr = UBXReader(ubx_stream)
            raw, msg = ubr.read()
            log.info(msg)

        except StreamMuxDemuxError as e:
            log.error(e)
            ubx_stream.owner.close()
            return

        # TODO: except parse errors

        except Exception as e:
            log.error(e)
            # sleep(REPLUG_WAIT_TIME)


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

    # run UBX thread
    log.info(f'Creating a thread for handling UBX')
    ubx_thread = Thread(target=ubx_handler, daemon=True, args=[streams.UBX])
    ubx_thread.start()

    # run RTCM thread
    log.info(f'Creating a thread for handling RTCM')
    rtcm_thread = Thread(target=rtcm_handler, daemon=True, args=[streams.RTCM])
    rtcm_thread.start()

    # run NMEA thread
    log.info(f'Creating a thread for handling NMEA')
    nmea_thread = Thread(target=nmea_handler, daemon=True, args=[streams.NMEA])
    nmea_thread.start()

    # cleanup
    ubx_thread.join()
    rtcm_thread.join()
    nmea_thread.join()
    streams.close()
    original_stream.close()


if __name__ == '__main__':
    logging.basicConfig(format="%(levelname)s:%(name)s:%(asctime)s:  %(message)s", level=logging.DEBUG)

    while True:
        try:
            main()
        except Exception as e:
            log.error(e)
        sleep(REPLUG_WAIT_TIME)
