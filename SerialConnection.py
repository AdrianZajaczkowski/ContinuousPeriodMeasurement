from ctypes.wintypes import BYTE
from Errors import Errors
from Liblarys import *
import struct


class SerialConnection:
    def __init__(self):
        super(SerialConnection, self).__init__()
        self.first = 0
        self.devicesList = []
        self.COM = ''
        self.baudrate = 0
        self.connection = sr.Serial()
        self.ports = []
        self.ierrors = Errors()
        self.F_CPU = 16000000
        self.overflow = 65536

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
            self.connectionTest()
        except TypeError:
            msg = "\n Brak wybranej płytki lub baundrate.Wybierz ponownie ustawienia płytki"
            self.ierrors.message('Błąd', msg)
            if self.ierrors.exec():
                self.ierrors.close()
                self.endConnection()
        except Exception as e:
            msg = "\n Brak podłaczonej płytki. Podłącz płytkę i zacznij ponownie."
            self.ierrors.message('Błąd', msg)
            if self.ierrors.exec():
                self.ierrors.close()
                self.endConnection()

    def connectionTest(self):

        print(self.connection.read(self.connection.inWaiting()))
        '''try:
            if self.connection.inWaiting() > 5:
                pass
            else:
                raise Exception
        except Exception:
            msg = 'Brak połączenia z płytką. Sprawdź połącznenie mikrokontroler - PC.'
            self.ierrors.message('Błąd danych', msg)
            if self.ierrors.exec():
                self.endConnection()
                self.ierrors.close()
'''

    def readValue(self):
        try:
            # if (self.connection.inWaiting() > 0):
            # struct <- urzyć i przetestować
            self.value = self.connection.read(4)

            unpacked_data = struct.unpack("I", self.value)[0]

            self.first, self.second = float(unpacked_data), float(self.first)

            if self.second < self.first:
                #print(f'okres 1 {self.first}')
                #print(f'okres 1 {self.second}')
                # print(f'{self.first-self.second}')
                self.perioid = float((self.first - self.second)+self.overflow
                                     ) * float((1 / self.F_CPU))
                #print(f'okres 1 {self.perioid} ')
            elif self.second > self.first:
                #print(f'okres 2 {self.first}')
                #print(f'okres 2 {self.second}')
                # print(f'{self.first-self.second}')
                self.perioid = (self.first - self.second +
                                self.overflow) * (1 / self.F_CPU)
                #print(f'okres 2 {self.perioid}')
                return float(self.perioid)

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
        return self.second[key]

    def endConnection(self):
        self.connection.close()


'''
app = QApplication(sys.argv)
win = SerialConnection()
win.showDevices()
win.connect("Arduino", "115200")
while True:
    win.readValue()
sys.exit(app.exec_())
'''
