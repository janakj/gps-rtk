from threading import Thread

from .UBloxQueue import UBloxQueue

class UBloxReaderDEMUX:
    def __init__(self, serial, ttl, timeout, onError=None):
        self._serial = serial

        self._nmea_q = UBloxQueue(ttl, timeout)
        self._ubx_q = UBloxQueue(ttl, timeout)
        self._rtcm_q = UBloxQueue(ttl, timeout)

        self._onError = onError

        self._reader_thread = Thread(target=self._read_to_queue)
        self._reader_thread.daemon = True
        self._reader_thread.start()

    def _read_to_queue(self):
        ser = self._serial

        while True:
            frame = [ser.read()]

            """ NMEA """
            if frame[0] == b"$":
                frame.append(ser.readline())

                """ entire message """
                msg = b"".join(frame)
                
                """ add msg to NMEA queue"""
                for byte in msg:
                    self._nmea_q.put(byte.to_bytes(1, 'big'))

                # done
                continue


            """ UBX """
            if frame[0] == b"\xb5":
                frame.append(ser.read())
                if frame[1] == b"\x62":
                    frame.append(ser.read())                # class
                    frame.append(ser.read())                # id
                    length_bytes = ser.read(2)              # length
                    frame.append(length_bytes)

                    length = int.from_bytes(length_bytes, byteorder='little', signed=False)
                    frame.append(ser.read(length))          # payload
                    frame.append(ser.read())                # CK_A
                    frame.append(ser.read())                # CK_B
                    
                    """ entire message """
                    msg = b"".join(frame)

                    """ add msg to UBX queue"""
                    for byte in msg:
                        self._ubx_q.put(byte.to_bytes(1, 'little'))

                    # done
                    continue

            
            """ RTCM """
            if frame[0] == b"\xD3":
                frame.append(ser.read())                    # byte 2
                frame.append(ser.read())                    # byte 3

                num1 = int.from_bytes(frame[1], byteorder='little', signed=False)
                num2 = int.from_bytes(frame[2], byteorder='little', signed=False)
                length = ((num1 & 0b00000011) << 8) + num2
                frame.append(ser.read(length))              # payload
                frame.append(ser.read(3))                   # parity

                """ entire message """
                msg = b"".join(frame)

                """ add msg to UBX queue"""
                for byte in msg:
                    self._rtcm_q.put(byte.to_bytes(1, 'little'))

                # done
                continue

            
            """ error """
            if self._onError:
                data = b"".join(frame)
                self._onError(data)
    

    
    def readNMEA(self):
        return self._nmea_q.get()

    def readUBX(self):
        return self._ubx_q.get()

    def readRTCM(self):
        return self._rtcm_q.get()
