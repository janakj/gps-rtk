from pyubx2 import UBX_CONFIG_DATABASE

class UBXKey:
    def __init__(self, name, values_map):
        self._id = UBX_CONFIG_DATABASE[name][0]
        self._name = name
        self._values_map = values_map

        pretty = name.replace("CFG_TMODE_", "")
        self._pretty_name = pretty
    
    def getID(self):
        return self._id
    
    def getName(self):
        return self._name
    
    def getPrettyName(self):
        return self._pretty_name

    def map(self, val):
        if val in self._values_map:
            return self._values_map[val]
        return val
