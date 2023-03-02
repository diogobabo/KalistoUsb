import time
from time import sleep

import serial.tools.list_ports
import serial


def string_to_hex(hexa):
    hexa = '0x' + hexa
    an_integer = int(hexa, 16)
    hexa = hex(an_integer)
    return hexa

def convert_to_hex(month, day, year, weekday, hour, minute, second, centisecond):
    hex_month = string_to_hex(hex(month)[2:].zfill(2))
    hex_day = string_to_hex(hex(day)[2:].zfill(2))
    hex_year = string_to_hex(hex(year)[2:].zfill(2))
    hex_weekday = string_to_hex(hex(weekday - 1)[2:].zfill(2))
    hex_hour = string_to_hex(hex(hour)[2:].zfill(2))
    hex_minute = string_to_hex(hex(minute)[2:].zfill(2))
    hex_second = string_to_hex(hex(second)[2:].zfill(2))
    hex_centisecond = string_to_hex(hex(centisecond)[2:].zfill(2))

    return (hex_month, hex_day, hex_year, hex_weekday, hex_hour, hex_minute, hex_second, hex_centisecond)

class Kallisto:
    def __init__(self, port, hwid):
        self.Port = port
        self.hwid = hwid
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

    #3.5 (sensor_name, true/false (enable,disable), time)
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
        self.write([0x05, self.dict[sensor], status, interval])

    #3.3 (sensor_name, true/false (enable,disable))
    def set_stream(self, sensor, status):
        if status:
            status = 0x01
        else:
            status = 0x00

        self.write([0x03, self.dict[sensor], status])

        res = self.read()
        print(res)
        if res != ['0x09', '0x00', '0x0a']:
            return False
        return True

    # 3.7
    def set_rtc(self, month, day, year, weekday, hour, minutes, seconds, centiseconds):
        hex_month, hex_day, hex_year, hex_weekday, hex_hour, hex_minute, hex_second, hex_centisecond = convert_to_hex(month, day, year, weekday, hour, minutes, seconds, centiseconds)
        self.write([0x07, hex_month, hex_day, hex_year, hex_weekday, hex_hour, hex_minute, hex_second, hex_centisecond])
        res = self.read()
        print(res)
        if res != ['0x18','0x00','0x0a']:
            return False
        return True

    # 3.8
    def get_rtc(self):
        self.write([0x08,0x01])
        res = self.read()
        print(res)
        return res


if __name__ == '__main__':

    ports = serial.tools.list_ports.comports()
    possible_ports = {}

    for port, desc, hwid in sorted(ports):
        if "SER" in hwid:
            possible_ports[port] = hwid


    print(possible_ports)
    sensor = Kallisto('/dev/ttyACM0', possible_ports['/dev/ttyACM0'])
    sensor.set_rtc(3, 2, 23, 5, 16, 40, 20, 50)
    #lista = sensor.set_stream('temp', True)