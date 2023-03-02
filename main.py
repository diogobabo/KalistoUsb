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

    def write(self, data):
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
        self.write([0x05, self.dict[sensor], status] + list(interval.to_bytes(4, 'big')))


if __name__ == '__main__':

    ports = serial.tools.list_ports.comports()
    possible_ports = {}
    for port, desc, hwid in sorted(ports):
        if "SER" in hwid:
            possible_ports[port] = hwid

    sensor = Kallisto('COM3', possible_ports['COM3'])
    sensor.set_sensor('eco2', True, 1000)
    lista = sensor.read()
    print(lista)
    time.sleep(1)
    sensor.write([0x0b, 0x01])
    lista = sensor.read()
    print(lista)
    sensor.set_sensor('eco2', False, 1000)
    time.sleep(1)
    sensor.write([0x0b, 0x01])
    time.sleep(1)
    lista = sensor.read()
    print(lista)
