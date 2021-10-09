#!/usr/bin/env python3
import logging
import serial
from time import sleep
from ubx import UBXManager
from bluetooth import BluetoothTransmitter

BAUDRATE = 38400
HOST_PORT = '/dev/gps-uart1'
BLUETOOTH_PORT = '/dev/rfcomm0'

log = logging.getLogger('rover')


def main():
    log.info(f'Creating UBX manager on {HOST_PORT}')
    ser = serial.Serial(HOST_PORT, BAUDRATE)
    manager = UBXManager(ser)

    log.info(f'Creating Bluetooth transmitter on {BLUETOOTH_PORT}')
    bluetooth = BluetoothTransmitter(BLUETOOTH_PORT)
    manager.onNMEA = bluetooth.onNMEA

    bluetooth.start()

    log.info('Starting UBX manager')
    manager.start()

    # Keep running until the user presses CTRL-C in the terminal
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        pass
    finally:
        bluetooth.shutdown()

        log.info('Asking UBX manager to terminate')
        manager.shutdown()
        manager.join()
        log.info('UBX manager terminated')

        ser.close()


if __name__ == '__main__':
    logging.basicConfig(format="%(levelname)s:%(name)s:%(asctime)s:  %(message)s", level=logging.DEBUG)
    main()
