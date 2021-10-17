class UBloxStream():
    def __init__(self, read_func, write_func):
        self._read = read_func
        self._write = write_func

    def read(self, n=1):
        result = b""
        for i in range(n):
            result += self._read()
        return result

    def readline(self):
        byte = self._read()
        result = byte
        while byte != b'\n':
            byte = self._read()
            result += byte
        return result

    def write(self, data):
        self._write(data)
