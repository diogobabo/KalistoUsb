import serial.tools.list_ports
import serial


if __name__ == '__main__':
    ports = serial.tools.list_ports.comports()
    possible_ports = {}
    for port, desc, hwid in sorted(ports):
        if not port in possible_ports:
            possible_ports[port] = hwid
    for key in possible_ports:
        SerialObj = serial.Serial('COM3')
        SerialObj.baudrate = 9600  # set Baud rate to 9600
        SerialObj.bytesize = 8  # Number of data bits = 8
        SerialObj.parity = 'N'  # No parity
        SerialObj.stopbits = 1
        SerialObj.write(0x0b01)
        s = SerialObj.read()
        print(s)

