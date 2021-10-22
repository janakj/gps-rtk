from pyubx2 import UBXMessage

class MSG_CONFIG:
    
    def __init__ (self, serial, interface="UART1", ubr):
        self._serial = serial
        self._interface = interface
        self._ubr = ubr
    
    def enableRTCMOutput(self):
        layer = 1 ## RAM
        enable = 1

        transaction = 0
        cfgData = [("CFG_" + self._interface + "OUTPROT_RTCM3X", enable)]
        msg = UBXMessage.config_set(layer, transaction, cfgData)
        self._serial.write(msg.serialize())

        raw_ack, ack = self._ubr.read()

        if ack.identity != 'ACK-ACK':
            raise ValueError("expected 'ACK-ACK' message.")
    
    def disbleRTCMOutput(self):
        layer = 1 ## RAM
        enable = 0

        transaction = 0
        cfgData = [("CFG_" + self._interface + "OUTPROT_RTCM3X", enable)]
        msg = UBXMessage.config_set(layer, transaction, cfgData)
        self._serial.write(msg.serialize())

        raw_ack, ack = self._ubr.read()

        if ack.identity != 'ACK-ACK':
            raise ValueError("expected 'ACK-ACK' message.")

    def enableRTCMMsgOutput(self, msg_type):
        layer = 1 ## RAM
        output_rate = 1

        transaction = 0
        cfgData = [(msg_type, output_rate)]
        msg = UBXMessage.config_set(layer, transaction, cfgData)
        self._serial.write(msg.serialize())

        raw_ack, ack = self._ubr.read()

        if ack.identity != 'ACK-ACK':
            raise ValueError("expected 'ACK-ACK' message.")
    
    def disableRTCMMsgOutput(self, msg_type):
        layer = 1 ## RAM
        output_rate = 0

        transaction = 0
        cfgData = [(msg_type, output_rate)]
        msg = UBXMessage.config_set(layer, transaction, cfgData)
        self._serial.write(msg.serialize())

        raw_ack, ack = self._ubr.read()

        if ack.identity != 'ACK-ACK':
            raise ValueError("expected 'ACK-ACK' message.")
    
    def enableUBXOutput(self):
        layer = 1 ## RAM
        enable = 1

        transaction = 0
        cfgData = [("CFG_" + self._interface + "OUTPROT_UBX", enable)]
        msg = UBXMessage.config_set(layer, transaction, cfgData)
        self._serial.write(msg.serialize())

        raw_ack, ack = self._ubr.read()

        if ack.identity != 'ACK-ACK':
            raise ValueError("expected 'ACK-ACK' message.")

    def enableUBXOutput(self):
        layer = 1 ## RAM
        enable = 0

        transaction = 0
        cfgData = [("CFG_" + self._interface + "OUTPROT_UBX", enable)]
        msg = UBXMessage.config_set(layer, transaction, cfgData)
        self._serial.write(msg.serialize())

        raw_ack, ack = self._ubr.read()

        if ack.identity != 'ACK-ACK':
            raise ValueError("expected 'ACK-ACK' message.")
    
    def enableNMEAOutput(self):
        layer = 1 ## RAM
        enable = 1

        transaction = 0
        cfgData = [("CFG_" + self._interface + "OUTPROT_NMEA", enable)]
        msg = UBXMessage.config_set(layer, transaction, cfgData)
        self._serial.write(msg.serialize())

        raw_ack, ack = self._ubr.read()

        if ack.identity != 'ACK-ACK':
            raise ValueError("expected 'ACK-ACK' message.")
    
    def disbleNMEAOutput(self):
        layer = 1 ## RAM
        enable = 0

        transaction = 0
        cfgData = [("CFG_" + self._interface + "OUTPROT_NMEA", enable)]
        msg = UBXMessage.config_set(layer, transaction, cfgData)
        self._serial.write(msg.serialize())

        raw_ack, ack = self._ubr.read()

        if ack.identity != 'ACK-ACK':
            raise ValueError("expected 'ACK-ACK' message.")
    