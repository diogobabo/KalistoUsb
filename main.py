import time
from time import sleep

import serial.tools.list_ports
import serial

class Kallisto:
    def __init__(self, port, hwid):
        self.Port = port
        self.HWID = hwid
        self.SerialObj = serial.Serial(port)
        self.SerialObj.timeout = 0.1
        self.dict = {'accel': 0x01, 'gyroscope': 0x02, 'magnet': 0x03, 'temp': 0x04, 'pressure': 0x05, 'humidity': 0x06, 'eco2': 0x07, 'tvoc': 0x08,'light': 0x09, 'bvoc': 0x0a, 'iaq': 0x0b, 'noise': 0x0c, 'micro': 0x0d}

    def __del__(self):
        self.SerialObj.close()

    def __write(self, data):
        self.SerialObj.write(bytes(data))

    def read(self):
        result = []
        while True:
            readOut = self.SerialObj.read()
            if readOut:
                result.append(bytes.hex(readOut, ' '))
            else:
                break
        return result

    def set_sensor(self, sensor, status, interval):
        if status:
            status = 0x01
        else:
            status = 0x00
        if self.dict[sensor] == 0x01 or self.dict[sensor] == 0x02 or self.dict[sensor] == 0x03:
            interval = interval * 1000
        interval = hex(interval)
        interval = interval[2:]
        size = len(interval)
        if size < 8:
            interval = '0' * (8 - size) + interval
        elif size > 8:
            interval = interval[:8]
        interval = '0x' + interval
        an_integer = int(interval, 16)
        interval = hex(an_integer)
        self.__write([0x05, self.dict[sensor], status, interval])


if __name__ == '__main__':

    ports = serial.tools.list_ports.comports()
    possible_ports = {}
    for port, desc, hwid in sorted(ports):
        if "SER" in hwid:
            possible_ports[port] = hwid

    sensor = Kallisto(port, 'COM3')
    sensor.write([0x0b, 0x01])
    lista = sensor.read()
    print(lista)