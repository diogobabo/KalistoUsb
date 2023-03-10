import time
from time import sleep
import cbor2
import serial.tools.list_ports
import serial


# Auxiliary Functions

# Convert a string to hex
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
        a = time.time()
        while True:
            readOut = self.SerialObj.read()
            if readOut:
                result.append(bytes.hex(readOut, ' '))
            else:
                if len(result) > 0 and result[-1] == '0a':
                    break
                elif len(result) == 0 and time.time() - a > 2:
                    print("Timeout")
                    return False
                elif time.time() - a > 5:
                    print("Timeout")
                    return False
        return result
    

    # 3.1 Set Storage
    # Enables and disables data storage in Kallisto. Each sensor is enabled separately. Sensor ID and Filename must be provided.
    def set_storage(self, sensorID, status, filename):
        if status:
            status = 0x01
        else:
            status = 0x00
        filename = filename.encode('ascii', 'replace')
        self.write([0x01, self.dict[sensorID], status] + list(len(filename).to_bytes(1, 'big')) + [x for x in filename])
        res = self.read()
        print(res)
        if res != ['02', '00', '0a']:
            print("Error")
            return False
        return True

    # 3.2 Get Storage 
    # Requests Kallisto to send data in the file with the provided Filename
    def get_storage(self, filename):
        filename = filename.encode('ascii', 'replace')
        self.write([0x03] + list(len(filename).to_bytes(1, 'big')) + [x for x in filename])
        res = self.read()
        print(res)
        return res



    # 3.3 (sensor_name, true/false (enable,disable))
    def set_stream(self, sensorID, status):
        if status:
            status = 0x01
        else:
            status = 0x00

        self.write([0x03, self.dict[sensorID], status])

        res = self.read()

        if res != ['09', '00', '0a']:
            return False
        if status:
            print("Sensor: " + sensorID + " stream successfully enabled!")
        else:
            print("Sensor: " + sensorID + " stream successfully disabled!")
        return True

    # 3.3 SET Internet Connection TODO

    # 3.5 (sensor_name, true/false (enable,disable), time)
    def set_sensor(self, sensorID, status, interval):
        if status:
            status = 0x01
        else:
            status = 0x00
        if self.dict[sensorID] == 0x01 or self.dict[sensorID] == 0x02 or self.dict[sensorID] == 0x03:
            interval = interval * 1000
        self.write([0x05, self.dict[sensorID], status] + list(interval.to_bytes(4, 'big')))
        res = self.read()
        success = True
        for i in range(len(res)):
            if (i == 0):
                if res[i] != '12':
                    success = False
  
            elif i == 14:
                if res[i] != '0a':
                    success = False
            elif res[i] != '00':
                print("Error Code: " + str(i) + " , Flag " + res[i])
                success = False
            
        if success:
            if status:
                print("Sensor: " + sensorID + " successfully enabled!")
            else:
                print("Sensor: " + sensorID + " successfully disabled!")
        else:
            print("Error setting sensor: " + sensorID)
        return success

        
        
    # 3.6 SET Erase
    # Requests Kallisto to erase file from its default storage method

    # TODO
    def set_erase(self, sensorID, path):
        path = path.encode('ascii', 'replace')
        self.write([0x06, self.dict[sensorID]] + list(len(path).to_bytes(1, 'big')) + [x for x in path])
        res = self.read()
        print(res)
        if res != ['15', '00', '0a']:
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

    # 3.9 GET Battery
    # Requests Kallisto to provide the current Battery state of charge value
    def get_battery(self):
        self.write([0x09, 0x01])
        res = self.read()
        print(res)
        if (res[0] != '1e' or  res[3] != '0a'):
            print("Error getting battery")
            return False
        soc = res[1]
        status = res[2]
        print("Battery: " + str(soc) + "%")
        print("Charging..." if status == '01' else "Not charging...")
        
        return res
    
    # 3.10 GET Storage List
    # Requests Kallisto to provide list of files in the root directory of the default storage method.

    # TODO
    def get_storage_list(self):
        self.write([0x0a, 0x01])
        res = self.read()
        print(res)
        return res
    
    # 3.11 GET Status
    # Requests Kallisto to provide the current status of each sensor. 
    # Including: if the sensor is enabled, if the sensor data is being stored, if the sensor data is being streamed and the current sampling period.

    # TODO
    def get_status(self):
        self.write([0x0b, 0x01])
        res = self.read()
        print(res)
        return res

    # 3.12 SET Calibration

    def set_calibration(self, sensor):
        self.write([0x0c, self.dict[sensor]])
        res = self.read()
        success = True
        for i in range(len(res)):
            if i == 0:
                if res[i] != '27':
                    success = False
            elif i == 14:
                if res[i] != '0a':
                    success = False   
            elif res[i] != '00':
                print("Error calibrating sensor: " + sensor)
                success = False
                
        if success:
            print("Sensor: " + sensor + " successfully calibrated!")
            return True
        else:
            return False
        
    def get_stream(self):
        read = b''
        while True:
            bytesWaiting = sensor.SerialObj.inWaiting()
            if bytesWaiting > 0:
                read = read + sensor.SerialObj.read(bytesWaiting)
                break
        return read
      


if __name__ == '__main__':

    ports = serial.tools.list_ports.comports()
    possible_ports = {}

    for port, desc, hwid in sorted(ports):
        if "SER" in hwid:
            possible_ports[port] = hwid

    sensor = Kallisto('COM3', possible_ports['COM3'])
    sensor.set_sensor('accel', True, 100)
    sensor.set_sensor('accel', False, 100)
    #sensor.set_storage('accel', True, 'test.txt')
    #sensor.set_storage('accel', False, 'test.txt')
    """
    timeleft = time.time() + 3
  
    while True:
        print(sensor.read())
        if timeleft == 0:
            break
        timeleft = timeleft - time.time()
        """


        
        
