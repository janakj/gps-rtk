from pyubx2 import UBXMessage

class MSG:
    
    def __init__ (self, serial, ubr):
        self._serial = serial
        self._ubr = ubr
    
    def _setProtocolStatus(self, protocol, interface, status, layer):

        transaction = 0
        cfgData = [("CFG_" + interface + "OUTPROT_" + protocol, status)]
        msg = UBXMessage.config_set(layer, transaction, cfgData)
        self._serial.write(msg.serialize())

        raw_ack, ack = self._ubr.read()

        if ack.identity != 'ACK-ACK':
            raise ValueError("expected 'ACK-ACK' message.")
    
    def enableRTCM(self, interface):
        # layer: RAM = 1
        self._setProtocolStatus("RTCM3X", interface, layer=1, status=1)
    
    def enableUBX(self, interface):
        # layer: RAM = 1
        self._setProtocolStatus("UBX", interface, layer=1, status=1)

    def enableNMEA(self, interface):
        # layer: RAM = 1
        self._setProtocolStatus("NMEA", interface, layer=1, status=1)

    def disableRTCM(self, interface):
        # layer: RAM = 1
        self._setProtocolStatus("RTCM3X", interface, layer=1, status=0)
    
    def disableUBX(self, interface):
        # layer: RAM = 1
        self._setProtocolStatus("UBX", interface, layer=1, status=0)

    def disableNMEA(self, interface):
        # layer: RAM = 1
        self._setProtocolStatus("NMEA", interface, layer=1, status=0)

    def _setMsgOutputRate(self, msg, output_rate, layer):

        transaction = 0
        cfgData = [(msg, output_rate)]
        msg = UBXMessage.config_set(layer, transaction, cfgData)
        self._serial.write(msg.serialize())

        raw_ack, ack = self._ubr.read()

        if ack.identity != 'ACK-ACK':
            raise ValueError("expected 'ACK-ACK' message.")
    
    def enableMsg(self, msg, output_rate = 1, layer=1):

        if output_rate > 0:
            self._setMsgOutputRate(msg, output_rate, layer)
        else:
            raise ValueError("expected output_rate > 0.")

    def disableMsg(self, msg, layer = 1):

        self._setMsgOutputRate(msg, layer=layer, output_rate=0)

    # def enableRTCMOutput(self):
    #     layer = 1 ## RAM
    #     enable = 1

    #     transaction = 0
    #     cfgData = [("CFG_" + self._interface + "OUTPROT_RTCM3X", enable)]
    #     msg = UBXMessage.config_set(layer, transaction, cfgData)
    #     self._serial.write(msg.serialize())

    #     raw_ack, ack = self._ubr.read()

    #     if ack.identity != 'ACK-ACK':
    #         raise ValueError("expected 'ACK-ACK' message.")
    
    # def disbleRTCMOutput(self):
    #     layer = 1 ## RAM
    #     enable = 0

    #     transaction = 0
    #     cfgData = [("CFG_" + self._interface + "OUTPROT_RTCM3X", enable)]
    #     msg = UBXMessage.config_set(layer, transaction, cfgData)
    #     self._serial.write(msg.serialize())

    #     raw_ack, ack = self._ubr.read()

    #     if ack.identity != 'ACK-ACK':
    #         raise ValueError("expected 'ACK-ACK' message.")

    # def enableRTCMMsgOutput(self, msg_type):
    #     layer = 1 ## RAM
    #     output_rate = 1

    #     transaction = 0
    #     cfgData = [(msg_type, output_rate)]
    #     msg = UBXMessage.config_set(layer, transaction, cfgData)
    #     self._serial.write(msg.serialize())

    #     raw_ack, ack = self._ubr.read()

    #     if ack.identity != 'ACK-ACK':
    #         raise ValueError("expected 'ACK-ACK' message.")
    
    # def disableRTCMMsgOutput(self, msg_type):
    #     layer = 1 ## RAM
    #     output_rate = 0

    #     transaction = 0
    #     cfgData = [(msg_type, output_rate)]
    #     msg = UBXMessage.config_set(layer, transaction, cfgData)
    #     self._serial.write(msg.serialize())

    #     raw_ack, ack = self._ubr.read()

    #     if ack.identity != 'ACK-ACK':
    #         raise ValueError("expected 'ACK-ACK' message.")
    
    # def enableUBXOutput(self):
    #     layer = 1 ## RAM
    #     enable = 1

    #     transaction = 0
    #     cfgData = [("CFG_" + self._interface + "OUTPROT_UBX", enable)]
    #     msg = UBXMessage.config_set(layer, transaction, cfgData)
    #     self._serial.write(msg.serialize())

    #     raw_ack, ack = self._ubr.read()

    #     if ack.identity != 'ACK-ACK':
    #         raise ValueError("expected 'ACK-ACK' message.")

    # def enableUBXOutput(self):
    #     layer = 1 ## RAM
    #     enable = 0

    #     transaction = 0
    #     cfgData = [("CFG_" + self._interface + "OUTPROT_UBX", enable)]
    #     msg = UBXMessage.config_set(layer, transaction, cfgData)
    #     self._serial.write(msg.serialize())

    #     raw_ack, ack = self._ubr.read()

    #     if ack.identity != 'ACK-ACK':
    #         raise ValueError("expected 'ACK-ACK' message.")
    
    # def enableNMEAOutput(self):
    #     layer = 1 ## RAM
    #     enable = 1

    #     transaction = 0
    #     cfgData = [("CFG_" + self._interface + "OUTPROT_NMEA", enable)]
    #     msg = UBXMessage.config_set(layer, transaction, cfgData)
    #     self._serial.write(msg.serialize())

    #     raw_ack, ack = self._ubr.read()

    #     if ack.identity != 'ACK-ACK':
    #         raise ValueError("expected 'ACK-ACK' message.")
    
    # def disbleNMEAOutput(self):
    #     layer = 1 ## RAM
    #     enable = 0

    #     transaction = 0
    #     cfgData = [("CFG_" + self._interface + "OUTPROT_NMEA", enable)]
    #     msg = UBXMessage.config_set(layer, transaction, cfgData)
    #     self._serial.write(msg.serialize())

    #     raw_ack, ack = self._ubr.read()

    #     if ack.identity != 'ACK-ACK':
    #         raise ValueError("expected 'ACK-ACK' message.")
    