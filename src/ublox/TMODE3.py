from pyubx2 import UBXMessage
from pyubx2 import UBX_CONFIG_DATABASE

class TMODE3:
    keys = {
        "CFG_TMODE_MODE": {0:"DISABLED", 1:"SURVEY_IN", 2:"FIXED"},
        "CFG_TMODE_POS_TYPE": {0:"ECEF", 1:"LLH"},
        "CFG_TMODE_ECEF_X": {},
        "CFG_TMODE_ECEF_Y": {},
        "CFG_TMODE_ECEF_Z": {},

        "CFG_TMODE_ECEF_X_HP": {},
        "CFG_TMODE_ECEF_Y_HP": {},
        "CFG_TMODE_ECEF_Z_HP": {},

        "CFG_TMODE_LAT": {},
        "CFG_TMODE_LON": {},
        "CFG_TMODE_HEIGHT": {},

        "CFG_TMODE_LAT_HP": {},
        "CFG_TMODE_LON_HP": {},
        "CFG_TMODE_HEIGHT_HP": {},

        "CFG_TMODE_FIXED_POS_ACC": {},

        "CFG_TMODE_SVIN_MIN_DUR": {},
        "CFG_TMODE_SVIN_ACC_LIMIT":  {}
    }

    def __init__(self, stream, ubx_reader):
        self._stream = stream
        self._ubr = ubx_reader

    def _pretty_config_result(self, resp):
        result = {}
        for k in self.keys:
            resp_val = getattr(resp, k)
            values_map = self.keys[k]
            if resp_val in values_map:
                result[k] = values_map[resp_val]
            else:
                result[k] = resp_val
        return result

    def _setKey(self, data, layer="RAM", transaction=0x00):
        memory_layer_to_code = {
            "RAM": 1,
            "BBR": 2,
            "Flash": 4,
        }
        layer = memory_layer_to_code[layer]
        req = UBXMessage.config_set(layer, transaction, data)
        self._stream.write(req.serialize())

        raw_ack, ack = self._ubr.read()
        if ack.identity != 'ACK-ACK':
            raise ValueError("expected 'ACK-ACK' message.")

    def _meter_to_cm_and_hp(self, meters):
        cm = int(meters * 1e2)
        tenth_mm = int(int(meters * 1e4) - 1e2 * cm)
        meters_after = (tenth_mm + 1e2 * cm)/1e4
        max_err = 1e-5
        if abs(meters - meters_after) > max_err:
            raise ValueError(f"unsupported precision in {meters}.")
        return cm, tenth_mm

    def _degree_to_tenmillionth_deg_and_hp(self, degrees):
        tenmillionth_deg = int(degrees * 1e7)
        billionth_deg = int(int(degrees * 1e9) - 1e2 * tenmillionth_deg)
        degrees_after = (billionth_deg + 1e2 * tenmillionth_deg)/1e9
        max_err = 1e-5
        if abs(degrees - degrees_after) > max_err:
            raise ValueError(f"unsupported precision in {degrees}.")
        return tenmillionth_deg, billionth_deg

    def getConfig(self, layer="RAM"):
        """
        Get configuration from Time Mode 3 
        :param str layer: memory layer --> RAM, BBR, Flash, Default
        :return: TMode3Config{}
        :rtype: dict
        """
        
        # get code for memory layer
        memory_layer_to_code = {
            "RAM": 0,
            "BBR": 1,
            "Flash": 2,
            "Default": 7
        }
        layer_data = memory_layer_to_code[layer]

        # default position 
        position_data = 0x00

        # get code for keys
        keys_data = [UBX_CONFIG_DATABASE[k][0] for k in self.keys]

        # send ubx message
        req = UBXMessage.config_poll(layer_data, position_data, keys_data)
        self._stream.write(req.serialize())
    
        # read ubx response
        raw_resp, resp = self._ubr.read()
        raw_ack, ack = self._ubr.read()

        # verify response
        if ack.identity != 'ACK-ACK':
            raise ValueError("expected 'ACK-ACK' message.")
        fields = [k for k in self.keys]
        for f in fields:
            if hasattr(resp, f) == False:
                raise ValueError(f"expected {f} attribute.")

        # return pretty result
        return self._pretty_config_result(resp)

    def enableSurveyIn(self, time, accuracy, layer="RAM"):
        # units:
        #   time -> seconds
        #   accuracy -> 0.1 mm  ==> mm
        data = [
            (UBX_CONFIG_DATABASE["CFG_TMODE_MODE"][0], 1), 
            (UBX_CONFIG_DATABASE["CFG_TMODE_SVIN_MIN_DUR"][0], time), 
            (UBX_CONFIG_DATABASE["CFG_TMODE_SVIN_ACC_LIMIT"][0], accuracy), 
        ]
        return self._setKey(data, layer)

    def enableFixedPositionECEF(self, x, y, z, acc, layer="RAM"):
        x_cm, x_hp = self._meter_to_cm_and_hp(x)
        z_cm, y_hp = self._meter_to_cm_and_hp(y)
        y_cm, z_hp = self._meter_to_cm_and_hp(z)
        acc_cm, acc_hp = self._meter_to_cm_and_hp(acc)

        data = [
            # enable fixed mode
            (UBX_CONFIG_DATABASE["CFG_TMODE_MODE"][0], 2), 

            # set position type to ECEF
            (UBX_CONFIG_DATABASE["CFG_TMODE_POS_TYPE"][0], 0),

            # set x
            (UBX_CONFIG_DATABASE["CFG_TMODE_ECEF_X"][0], x_cm),
            (UBX_CONFIG_DATABASE["CFG_TMODE_ECEF_X_HP"][0], x_hp),

            # set y
            (UBX_CONFIG_DATABASE["CFG_TMODE_ECEF_Y"][0], y_cm),
            (UBX_CONFIG_DATABASE["CFG_TMODE_ECEF_Y_HP"][0], y_hp),

            # set z
            (UBX_CONFIG_DATABASE["CFG_TMODE_ECEF_Z"][0], z_cm),
            (UBX_CONFIG_DATABASE["CFG_TMODE_ECEF_Z_HP"][0], z_hp),

            # set accuracy
            (UBX_CONFIG_DATABASE["CFG_TMODE_FIXED_POS_ACC"][0], acc_hp + 100*acc_cm), 
        ]
        return self._setKey(data, layer)

    def enableFixedPositionLLH(self, lat, lon, height, acc, layer="RAM"):
        lat_tenmillionth_deg, lat_hp = self._degree_to_tenmillionth_deg_and_hp(lat)
        lon_tenmillionth_deg, lon_hp = self._degree_to_tenmillionth_deg_and_hp(lon)
        height_cm, height_hp = self._meter_to_cm_and_hp(height)
        acc_cm, acc_hp = self._meter_to_cm_and_hp(acc)

        data = [
            # enable fixed mode
            (UBX_CONFIG_DATABASE["CFG_TMODE_MODE"][0], 2), 

            # set position type to LLH
            (UBX_CONFIG_DATABASE["CFG_TMODE_POS_TYPE"][0], 1),

            # set lat
            (UBX_CONFIG_DATABASE["CFG_TMODE_LAT"][0], lat_tenmillionth_deg),
            (UBX_CONFIG_DATABASE["CFG_TMODE_LAT_HP"][0], lat_hp),

            # set lon
            (UBX_CONFIG_DATABASE["CFG_TMODE_LON"][0], lon_tenmillionth_deg),
            (UBX_CONFIG_DATABASE["CFG_TMODE_LON_HP"][0], lon_hp),

            # set height
            (UBX_CONFIG_DATABASE["CFG_TMODE_HEIGHT"][0], height_cm),
            (UBX_CONFIG_DATABASE["CFG_TMODE_HEIGHT_HP"][0], height_hp),

            # set accuracy
            (UBX_CONFIG_DATABASE["CFG_TMODE_FIXED_POS_ACC"][0], acc_hp + 100*acc_cm), 
        ]
        return self._setKey(data, layer)

    def disable(self, layer="RAM"):
        data = [
            (UBX_CONFIG_DATABASE["CFG_TMODE_MODE"][0], 0), 
        ]
        return self._setKey(data, layer)

    def setCoordinateSystem(self, coordinate_system="ECEF", layer="RAM"):
        coordinate_system_to_code = {
            "ECEF": 0,
            "LLH": 1,
        }
        data = [
            (UBX_CONFIG_DATABASE["CFG_TMODE_POS_TYPE"][0], 
                coordinate_system_to_code[coordinate_system])
        ]
        return self._setKey(data, layer)
