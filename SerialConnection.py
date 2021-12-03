from serial.serialutil import SerialException
import serial.tools.list_ports
import serial as sr
from Errors import Errors
from Liblarys import *


class SerialConnection:
    def __init__(self):
        super(SerialConnection, self).__init__()
        self.data = []
        self.devicesList = []
        self.COM = ''
        self.baudrate = 0
        self.connection = sr.Serial()
        self.ports = []
        self.ierrors = Errors()

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
        self.connection.port = f'{self.COM}'
        self.connection.baudrate = self.baudrate
        self.connection.timeout = 1
        self.connection.open()

    def readValue(self):
        self.value = self.connection.readline().lstrip()
        try:
            if self.value is not None:
                self.data = float(self.value)
                return self.data
            else:
                raise ValueError
        except SerialException:
            msg = 'Błąd portu USB. Zmień port i zacznij pomiary ponownie'
            self.ierrors.message('Błąd USB', msg)
            if self.ierrors.exec():
                self.endConnection()
                self.ierrors.close()
            else:
                pass
        except ValueError:
            pass

    def reconnect(self):
        if self.connection.isOpen():
            self.connection.close()
            self.connection.port = f'{self.COM}'
            self.connection.baudrate = self.baudrate
            self.connection.timeout = 1
            self.connection.open()

    def __getitem__(self, key):
        return self.data[key]

    def endConnection(self):
        self.connection.flush()
        self.connection.close()


'''
app = QApplication(sys.argv)
win = SerialConnection()
win.showDevices()
win.connect("Arduino", "115200")
while True:
    print(win.readValue())
sys.exit(app.exec_())
'''
