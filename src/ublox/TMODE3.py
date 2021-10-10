from .UBXKey import UBXKey
from pyubx2 import UBXMessage

TMODE3_KEYS = {        
    UBXKey("CFG_TMODE_MODE", {0:"DISABLED", 1:"SURVEY_IN", 2:"FIXED"}),
    UBXKey("CFG_TMODE_POS_TYPE", {0:"ECEF", 1:"LLH"}),

    UBXKey("CFG_TMODE_ECEF_X", {}),
    UBXKey("CFG_TMODE_ECEF_Y", {}),
    UBXKey("CFG_TMODE_ECEF_Z", {}),

    UBXKey("CFG_TMODE_ECEF_X_HP", {}),
    UBXKey("CFG_TMODE_ECEF_Y_HP", {}),
    UBXKey("CFG_TMODE_ECEF_Z_HP", {}),

    UBXKey("CFG_TMODE_LAT", {}),
    UBXKey("CFG_TMODE_LON", {}),
    UBXKey("CFG_TMODE_HEIGHT", {}),

    UBXKey("CFG_TMODE_LAT_HP", {}),
    UBXKey("CFG_TMODE_LON_HP", {}),
    UBXKey("CFG_TMODE_HEIGHT_HP", {}),

    UBXKey("CFG_TMODE_FIXED_POS_ACC", {}),
    UBXKey("CFG_TMODE_SVIN_MIN_DUR", {}),
    UBXKey("CFG_TMODE_SVIN_ACC_LIMIT",  {})
}


class TMODE3:
    def __init__(self, serial, ubx_reader):
        self._serial = serial
        self._ubr = ubx_reader

    def _setKey(self, cfgData, layer="RAM", transaction=0x00):
        memory_layer_to_code = {
            "RAM": 1,
            "BBR": 2,
            "Flash": 4,
        }
        layer = memory_layer_to_code[layer]
        req = UBXMessage.config_set(layer, transaction, cfgData)
        self._serial.write(req.serialize())

        raw_ack, ack = self._ubr.read()
        if ack.identity != 'ACK-ACK':
            raise ValueError("expected 'ACK-ACK' message.")


    def getConfig(self, layer="RAM", coordinate_system="ECEF"):
        """
        Get configuration from Time Mode 3 
        :param str layer: memory layer --> RAM, BBR, Flash, Default
        :param str coordinate_system: coordinate system --> ECEF, LLH
        :return: TMode3Config[]
        :rtype: list
        """
        
        memory_layer_to_code = {
            "RAM": 0,
            "BBR": 1,
            "Flash": 2,
            "Default": 7
        }

        layer = memory_layer_to_code[layer]
        position = 0x00
        keys = [k.getID() for k in TMODE3_KEYS]
        req = UBXMessage.config_poll(layer, position, keys)
        self._serial.write(req.serialize())
    
        raw_resp, resp = self._ubr.read()
        raw_ack, ack = self._ubr.read()

        # verify response
        if ack.identity != 'ACK-ACK':
            raise ValueError("expected 'ACK-ACK' message.")
        fields = [k.getName() for k in TMODE3_KEYS]
        for f in fields:
            if hasattr(resp, 'CFG_TMODE_MODE') == False:
                raise ValueError("expected 'CFG_TMODE_MODE' attribute.")

        # parse result
        result = {k.getPrettyName(): k.map(getattr(resp, k.getName())) for k in TMODE3_KEYS}

        # filter result
        ignore = []
        if result["POS_TYPE"] == "ECEF":
            ignore = ["LAT", "LAT_HP", "LON", "LON_HP", "HEIGHT", "HEIGHT_HP"]
        else:
            ignore = ["ECEF_X", "ECEF_X_HP", "ECEF_Y", "ECEF_Y_HP", "ECEF_Z", "ECEF_Z_HP"]
        for k in ignore:
            del result[k]

        return result

    def setMode(self, mode, layer="RAM"):
        mode_to_code = {
            "DISABLED": 0,
            "SURVEY_IN": 1,
            "FIXED": 2,
        }
        key = [key for key in TMODE3_KEYS if key.getName() == "CFG_TMODE_MODE"][0]
        cfgData = [(key.getID(), mode_to_code[mode])]
        return self._setKey(cfgData, layer)
        

    def coordinate_system(self, coordinate_system="ECEF", layer="RAM"):
        coordinate_system_to_code = {
            "ECEF": 0,
            "LLH": 1,
        }
        key = [key for key in TMODE3_KEYS if key.getName() == "CFG_TMODE_POS_TYPE"][0]
        cfgData = [(key.getID(), coordinate_system_to_code[coordinate_system])]
        return self._setKey(cfgData, layer)
