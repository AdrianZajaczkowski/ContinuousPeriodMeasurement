import serial.tools.list_ports
import serial as sr


class SerialConnection:
    def __init__(self):
        super(SerialConnection, self).__init__()
        self.data = []
        self.devicesList = []
        self.COM = 'COM6'
        self.baudrate = '115200'
        self.connection = ''
        self.ports = []
        #self.connect(self.COM, self.baudrate)

    def showDevices(self):
        self.ports = list(serial.tools.list_ports.comports())
        for port in self.ports:
            self.devicesList.append(port.description)
        return self.devicesList

    def connect(self, device, baudrate):
        self.baudrate = baudrate
        for port in self.ports:
            if device in port.description:
                self.COM = port[0]
        self.connection = sr.Serial()
        self.connection.port = f'{self.COM}'
        self.connection.baudrate = self.baudrate
        self.connection.timeout = 10
        self.connection.open()

    def readValue(self):
        # while True:
        self.value = self.connection.readline().strip()
        self.data = list(self.value.decode('utf-8').split(','))
        # print(self.data)
        return self.data

    def __getitem__(self, key):
        return self.data[key]
