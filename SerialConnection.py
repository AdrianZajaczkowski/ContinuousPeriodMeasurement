from serial.serialutil import SerialException
import serial.tools.list_ports
import serial as sr
from Errors import Errors
from Liblarys import *
import time


class SerialConnection:
    def __init__(self):
        super(SerialConnection, self).__init__()
        self.data = ''
        self.devicesList = []
        self.COM = ''
        self.baudrate = 0
        self.connection = sr.Serial()
        self.ports = []
        self.ierrors = Errors()

    def showDevices(self):
        try:
            self.ports = list(serial.tools.list_ports.comports())
            for port in self.ports:
                self.devicesList.append(port.description)
            return self.devicesList
        except Exception as ex:
            msg = "\n Brak podłączonej płytki lub błytka jest nie widoczna dla urządzenia"
            self.ierrors.message('Błąd', msg)
            if self.ierrors.exec():
                self.ierrors.close()
                self.endConnection()

    def connect(self, device, baudrate):
        try:
            self.baudrate = int(baudrate)
            for port in self.ports:
                if device in port.description:
                    self.COM = port[0]
            self.connection.port = f'{self.COM}'
            self.connection.baudrate = self.baudrate
            self.connection.timeout = None
            self.connection.open()
        except TypeError:
            msg = "\n Brak wybranej płytki lub baundrate.Wybierz ponownie ustawienia płytki"
            self.ierrors.message('Błąd', msg)
            if self.ierrors.exec():
                self.ierrors.close()
                self.endConnection()

    def readValue(self):
        self.value = self.connection.readline(16).lstrip()
        try:
            text = self.value.decode('utf-8')
            print(text)
            if self.value is not None:
                while True:
                    if not '\\n' in str(self.value):
                        tmp = self.connection.readline()
                        if tmp.decode('utf-8'):
                            self.value = (self.value.decode('utf-8') +
                                          tmp.decode('utf-8')).encode('utf-8')
                        print(tmp)
                    else:
                        break

                self.data = float(self.value.decode().strip())
                return self.data
            else:
                raise ValueError
        except SerialException:
            msg = 'Błąd portu USB. Zmień port i zacznij pomiary ponownie'
            self.ierrors.message('Błąd USB', msg)
            if self.ierrors.exec():
                self.endConnection()
                self.ierrors.close()

        except ValueError:
            msg = 'Błąd wartości danych.Wykryto wartość None pochodzącą z podlączonego urządzenia.Sprawdź wartość baundrate'
            self.ierrors.message('Błąd danych', msg)
            if self.ierrors.exec():
                self.endConnection()
                self.ierrors.close()

    def reconnect(self):
        if self.connection.isOpen():
            self.connection.close()
            self.connection.port = f'{self.COM}'
            self.connection.baudrate = self.baudrate
            self.connection.timeout = None
            self.connection.open()

    def __getitem__(self, key):
        return self.data[key]

    def endConnection(self):
        self.connection.close()


'''
app = QApplication(sys.argv)
win = SerialConnection()
win.showDevices()
win.connect("Arduino", "9600")
while True:
    print(win.readValue())
sys.exit(app.exec_())
'''
