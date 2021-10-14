from pyubx2 import UBXMessage

UART1OUTPUT_KEYS = [
    "CFG_UART1OUTPROT_UBX",
    "CFG_UART1OUTPROT_NMEA",
    "CFG_UART1OUTPROT_RTCM3X", 
    "CFG_MSGOUT_RTCM_3X_TYPE1005_UART1"
]

class UART1:
    def __init__ (self, serial, ubx_reader):
        self._serial = serial
        self._ubr = ubx_reader
    
    def configRTCMOutput(self, flag):
        layer = 1 ## RAM

        transaction = 0
        cfgData = [("CFG_UART1OUTPROT_RTCM3X", flag)]
        msg = UBXMessage.config_set(layer, transaction, cfgData)
        self._serial.write(msg.serialize())

        raw_ack, ack = self._ubr.read()

        if ack.identity != 'ACK-ACK':
            raise ValueError("expected 'ACK-ACK' message.")
    
    def configNMEAOutput(self, flag):
        layer = 1 ## RAM

        transaction = 0
        cfgData = [("CFG_UART1OUTPROT_NMEA", flag)]
        msg = UBXMessage.config_set(layer, transaction, cfgData)
        self._serial.write(msg.serialize())

        raw_ack, ack = self._ubr.read()

        if ack.identity != 'ACK-ACK':
            raise ValueError("expected 'ACK-ACK' message.")
    
    def configUBXOutput(self, flag):
        layer = 1 ## RAM

        transaction = 0
        cfgData = [("CFG_UART1OUTPROT_UBX", flag)]
        msg = UBXMessage.config_set(layer, transaction, cfgData)
        self._serial.write(msg.serialize())

        raw_ack, ack = self._ubr.read()

        if ack.identity != 'ACK-ACK':
            raise ValueError("expected 'ACK-ACK' message.")


    def getConfig(self):
        layer = 0 ## RAM

        position = 0
        keys = UART1OUTPUT_KEYS
        req = UBXMessage.config_poll(layer, position, keys)
        self._serial.write(req.serialize())

        raw_rsp, parsed_rsp = self._ubr.read()
        raw_ack, parsed_ack = self._ubr.read()

        if parsed_ack.identity != 'ACK-ACK':
            raise ValueError("expected 'ACK-ACK' message.")

        return parsed_rsp