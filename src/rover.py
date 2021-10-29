#!/usr/bin/env python3
import logging
from serial import Serial
from time import sleep
from config import loadConfig
from ublox import UBloxManager
from threading import Thread

from bluetooth import BluetoothTransmitter

BAUDRATE = 38400
HOST_PORT = '/dev/gps-uart1'
BLUETOOTH_PORT = '/dev/rfcomm0'

log = logging.getLogger('rover')


def rover_rtcm_handler(rtcm_stream):
    xbee_stream = Serial("/dev/xbee", 115200, timeout=5)
    while True:
        byte = xbee_stream.read()
        rtcm_stream.write(byte)

def rover_nmea_handler(nmea_stream, bluetooth):
    while True: # Could be wrong to read line by line
        msg = nmea_stream.readline()
        msg = msg.strip()
        bluetooth.onNMEA(msg)


def main():
    # load rover config
    config_file = './config.cfg'
    log.info(f'Loading configuration from {config_file}')
    all_config = loadConfig(config_file)
    config = all_config["rover"]

    # get constants from config
    DEBUG = bool(config["DEBUG"])
    BAUDRATE = int(config["BAUDRATE"])
    TIMEOUT = int(config["TIMEOUT"])  
    STREAM_TTL = int(config["STREAM_TTL"])  
    PORT = config["PORT"]

    # connect to serial port
    log.info(f'Connecting to serial port {PORT}')
    stream = Serial(PORT, BAUDRATE, timeout=TIMEOUT)

    # create a ublox manager
    log.info(f'Creating UBloxManager manager on {PORT}')
    manager = UBloxManager(stream, STREAM_TTL)

    # disable TMODE3
    log.info(f'Disabling TMODE3 on {PORT}')
    manager.TMODE3.disable()

    # enable NMEA
    log.info(f'Enable NMEA on {PORT}')
    manager.MSG.enableNMEA(interface="UART1") # NMEA messages are enabled by default

    # run rover's RTCM handler thread
    rtcm_thread = Thread(target=rover_rtcm_handler, args=[manager.getRTCMStream()])
    rtcm_thread.start()

    nmea_stream = manager.getNMEAStream()
    # while True:
    #     print(nmea_stream.readline())

    log.info(f'Creating Bluetooth transmitter on {BLUETOOTH_PORT}')
    bluetooth = BluetoothTransmitter(BLUETOOTH_PORT)

    nmea_thread = Thread(target=rover_nmea_handler, args=[nmea_stream, bluetooth])
    nmea_thread.start()

    bluetooth.start()
    
    # manager.onNMEA = bluetooth.onNMEA # This is a pyUBX manager, which is no longer used in our code

    # log.info('Starting UBX manager')
    # manager.start()

    # # Keep running until the user presses CTRL-C in the terminal
    # try:
    #     while True:
    #         sleep(10)
    # except KeyboardInterrupt:
    #     pass
    # finally:
    #     bluetooth.shutdown()

    #     log.info('Asking UBX manager to terminate')
    #     manager.shutdown()
    #     manager.join()
    #     log.info('UBX manager terminated')

    #     ser.close()


if __name__ == '__main__':
    logging.basicConfig(format="%(levelname)s:%(name)s:%(asctime)s:  %(message)s", level=logging.DEBUG)
    main()
