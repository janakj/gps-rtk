#!/usr/bin/env python3
import logging
from serial import Serial
from config import loadConfig
from ublox import UBloxManager
from threading import Thread

log = logging.getLogger('base')


def base_rtcm_handler(rtcm_stream):
    xbee_stream = Serial("/dev/xbee", 115200, timeout=5)
    while True:
        byte = rtcm_stream.read()
        xbee_stream.write(byte)


def main():
    # load base station config
    config_file = './config.cfg'
    log.info(f'Loading configuration from {config_file}')
    all_config = loadConfig(config_file)
    config = all_config["base"]

    # get constants from config
    DEBUG = bool(config["DEBUG"])
    BAUDRATE = int(config["BAUDRATE"])
    TIMEOUT = int(config["TIMEOUT"])  
    STREAM_TTL = int(config["STREAM_TTL"])  
    PORT = config["PORT"]
    TMODE = config["TMODE"]
    OBSERVATION_TIME = int(config["OBSERVATION_TIME"])
    POSITION_ACCURACY = float(config["POSITION_ACCURACY"])

    # connect to serial port
    log.info(f'Connecting to serial port {PORT}')
    stream = Serial(PORT, BAUDRATE, timeout=TIMEOUT)

    # create a ublox manager
    log.info(f'Creating UBloxManager manager on {PORT}')
    manager = UBloxManager(stream, STREAM_TTL)

    # set in fixed position (will be changed to survey-in mode)
    log.info(f'Setting {PORT} in fixed position mode')
    manager.TMODE3.enableFixedPositionLLH(40.8074954, -73.9618238, 16.82, 0.5)

    manager.MSG.enableRTCM(interface="UART1")
    manager.MSG.enableMsg(msg="CFG_MSGOUT_RTCM_3X_TYPE1074_UART1")
    manager.MSG.disableMsg(msg="CFG_MSGOUT_RTCM_3X_TYPE1074_UART1")
    manager.MSG.enableMsg(msg="CFG_MSGOUT_RTCM_3X_TYPE1124_UART1")

    # run RTCM thread
    rtcm_thread = Thread(target=base_rtcm_handler, args=[manager.getRTCMStream()])
    rtcm_thread.start()

    # manually get nmea stream
    # nmea_stream = manager.getNMEAStream()
    # while True:
    #     print(nmea_stream.readline())


if __name__ == '__main__':
    logging.basicConfig(format="%(levelname)s:%(name)s:%(asctime)s:  %(message)s", level=logging.DEBUG)
    main()