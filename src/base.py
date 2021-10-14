#!/usr/bin/env python3
import logging
from serial import Serial
from config import loadConfig
from ublox import UBloxManager
from pyubx2 import UBXReader
from ubx import UBXManager

log = logging.getLogger('base')

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
    PORT = config["PORT"]
    TMODE = config["TMODE"]
    OBSERVATION_TIME = int(config["OBSERVATION_TIME"])
    POSITION_ACCURACY = float(config["POSITION_ACCURACY"])
    UART1OUTPUT_ENABLE = int(config["UART1OUTPUT_ENABLE"])
    UART1OUTPUT_DISABLE = int(config["UART1OUTPUT_DISABLE"])

    # connect to serial port
    log.info(f'Connecting to serial port {PORT}')
    stream = Serial(PORT, BAUDRATE, timeout=TIMEOUT)

    # create a ublox manager
    log.info(f'Creating UBloxManager manager on {PORT}')
    manager = UBloxManager(stream)

    # change operation mode 
    log.info(f'Setting {PORT} in {TMODE} mode')
    manager.TMODE3.setMode(TMODE)

    # TODO: setup OBSERVATION_TIME and POSITION_ACCURACY
    # TODO: maybe support Fixed mode?

    # print corrent TMODE 3 config
    log.info("current TMODE3 config:")
    log.info(manager.TMODE3.getConfig())

    # change UART1 output config
    log.info("Enable UART1 RTCM output")
    manager.UART1.configRTCMOutput(UART1OUTPUT_ENABLE)

    log.info("Enable UART1 UBX output")
    manager.UART1.configUBXOutput(UART1OUTPUT_ENABLE)

    log.info("Disable UART1 NMEA output")
    manager.UART1.configNMEAOutput(UART1OUTPUT_DISABLE)
    
    log.info("UART1 output config")
    defaultConfig = manager.UART1.getConfig()
    log.info(defaultConfig)



if __name__ == '__main__':
    logging.basicConfig(format="%(levelname)s:%(name)s:%(asctime)s:  %(message)s", level=logging.DEBUG)
    main()
