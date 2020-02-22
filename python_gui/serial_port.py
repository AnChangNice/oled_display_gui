import serial
import serial.tools.list_ports


class SerialPort(object):

    def __init__(self, port, baudrate):
        try:
            self.serial = serial.Serial(port, baudrate)
        except Exception:
            print("Serial Port '%s' Open False！" % (port))

    @classmethod
    def getDeviceList(self):
        deviceNames = []
        portList = list(serial.tools.list_ports.comports())
        for port in portList:
            deviceNames.append((port.description, port.device))
        return deviceNames

    def open(self, port, baudrate):
        try:
            self.serial = serial.Serial(port, baudrate, write_timeout=0)
        except Exception:
            print("Serial Port '%s' Open False！" % (port))

    def close(self):
        if not self.serial.closed:
            self.serial.close()

    def send(self, data):
        self.serial.write(data)


if __name__ == '__main__':
    portList = SerialPort.getDeviceList()
    for port in portList:
        print(port)