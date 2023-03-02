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
    hex_month = list(month.to_bytes(1, 'big'))
    hex_day = list(day.to_bytes(1, 'big'))
    hex_year = list(year.to_bytes(1, 'big'))
    hex_weekday = list(weekday.to_bytes(1, 'big'))
    hex_hour = list(hour.to_bytes(1, 'big'))
    hex_minute = list(minute.to_bytes(1, 'big'))
    hex_second = list(second.to_bytes(1, 'big'))
    hex_centisecond = list(centisecond.to_bytes(1, 'big'))

    return hex_month + hex_day + hex_year + hex_weekday + hex_hour + hex_minute + hex_second + hex_centisecond


class Kallisto:
    def __init__(self, port, hwid):
        self.Port = port
        self.hwid = hwid
        self.SerialObj = serial.Serial(port)
        self.SerialObj.timeout = 0.1
        self.dict = {'accel': 0x01, 'gyroscope': 0x02, 'magnet': 0x03, 'temp': 0x04, 'pressure': 0x05, 'humidity': 0x06,
                     'eco2': 0x07, 'tvoc': 0x08, 'light': 0x09, 'bvoc': 0x0a, 'iaq': 0x0b, 'noise': 0x0c, 'micro': 0x0d}

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

    # 3.5 (sensor_name, true/false (enable,disable), time)
    def set_sensor(self, sensor, status, interval):
        if status:
            status = 0x01
        else:
            status = 0x00
        if self.dict[sensor] == 0x01 or self.dict[sensor] == 0x02 or self.dict[sensor] == 0x03:
            interval = interval * 1000
        self.write([0x05, self.dict[sensor], status] + list(interval.to_bytes(4, 'big')))

    # 3.3 (sensor_name, true/false (enable,disable))
    def set_stream(self, sensor, status):
        if status:
            status = 0x01
        else:
            status = 0x00

        self.write([0x03, self.dict[sensor], status])

        res = self.read()
        print(res)
        if res != ['09', '00', '0a']:
            return False
        return True

    # 3.7
    def set_rtc(self, month, day, year, weekday, hour, minutes, seconds, centiseconds):
        self.write([0x07] + convert_to_hex(month, day, year, weekday, hour, minutes, seconds, centiseconds))
        res = self.read()
        if res != ['18', '00', '0a']:
            return False
        return True

    # 3.8
    def get_rtc(self):
        self.write([0x08, 0x01])
        res = self.read()
        return res


if __name__ == '__main__':

    ports = serial.tools.list_ports.comports()
    possible_ports = {}

    for port, desc, hwid in sorted(ports):
        if "SER" in hwid:
            possible_ports[port] = hwid

    sensor = Kallisto('COM3', possible_ports['COM3'])
    sensor.set_sensor('accel', True, 100)
    print(sensor.read())
    timeleft = time.time() + 3
    while True:
        print(sensor.read())
        if timeleft == 0:
            break
        timeleft = timeleft - time.time()
