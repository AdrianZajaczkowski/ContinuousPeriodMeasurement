import serial.tools.list_ports
import serial as sr


class SerialConnection:
    def __init__(self):
        super(SerialConnection, self).__init__()
        self.data = []
        self.devicesList = []
        self.COM = ''
        self.baudrate = 0
        self.connection = ''
        self.ports = []

    def showDevices(self):
        self.ports = list(serial.tools.list_ports.comports())
        for port in self.ports:
            self.devicesList.append(port.description)
        return self.devicesList

    def connect(self, device, baudrate):
        self.baudrate = int(baudrate)
        for port in self.ports:
            if device in port.description:
                self.COM = port[0]
        self.connection = sr.Serial()
        self.connection.port = f'{self.COM}'
        self.connection.baudrate = self.baudrate
        self.connection.timeout = 1
        self.connection.open()

    def readValue(self):

        self.value = self.connection.readline()
        self.data = int(self.value)

        return self.data

    def __getitem__(self, key):
        return self.data[key]

    def endConnection(self):
        self.connection.flush()
        self.connection.close()


'''ser = SerialConnection()
ser.showDevices()
ser.connect("Arduino", 500000)

while True:
    val = ser.readValue()
    print(val)
'''
