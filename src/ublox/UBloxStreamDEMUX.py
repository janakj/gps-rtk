from threading import Thread

from .UBloxQueue import UBloxQueue
from .UBloxStream import UBloxStream

class UBloxStreamDEMUX:
    def __init__(self, serial, ttl, timeout):
        self._serial = serial

        self._nmea_q = UBloxQueue(ttl, timeout)
        self._nmea_stream = UBloxStream(self._nmea_q)

        self._ubx_q = UBloxQueue(ttl, timeout)
        self._ubx_stream = UBloxStream(self._ubx_q)

        self._rtcm_q = UBloxQueue(ttl, timeout)
        self._rtcm_stream = UBloxStream(self._rtcm_q)

        reader_thread = Thread(target=self._read_to_queue)
        reader_thread.start()

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
            # print("error", frame)

    def NMEAStream(self):
        return self._nmea_stream

    def UBXStream(self):
        return self._ubx_stream

    def RTCMStream(self):
        return self._rtcm_stream
