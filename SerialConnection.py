from Errors import Errors
from Liblarys import *


class SerialConnection:
    def __init__(self):
        super(SerialConnection, self).__init__()
        self.next = 0
        self.devicesList = []
        self.COM = ''
        self.baudrate = 0
        self.connection = None
        self.ports = []
        self.ierrors = Errors()

    def showDevices(self):
        self.ports = list(serial.tools.list_ports.comports())
        try:
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
            self.connection = sr.Serial()
            self.baudrate = int(baudrate)
            for port in self.ports:
                if device in port.description:
                    self.COM = port[0]
                    print(self.COM)
            self.connection.port = f'{self.COM}'
            self.connection.baudrate = self.baudrate
            # self.connection.bytesize = EIGHTBITS
            # self.connection.stopbits = STOPBITS_ONE
            # self.connection.parity = "N"
            # # self.connection.dsrdtr = True
            # self.connection.timeout = 0
            print(self.connection.isOpen())
            self.connection.close()
            self.connection.open()

        except TypeError as ty:
            msg = "\n Brak wybranej płytki lub baundrate.Wybierz ponownie ustawienia płytki"
            self.ierrors.message('Błąd', msg)
            if self.ierrors.exec():
                self.ierrors.close()
                self.endConnection()
        except Exception as e:
            msg = "\n Brak podłaczonej płytki. Podłącz płytkę i zacznij ponownie."
            self.ierrors.message('Błąd', e)
            if self.ierrors.exec():
                self.ierrors.close()
                self.endConnection()

    def rescan(self):
        sleep(3)
        call(["devcon.exe", "rescan"])

    def calc_checksum(self, data):
        calculated_checksum = 0
        for byte in data:
            calculated_checksum ^= byte
        return calculated_checksum

    def readValue(self):
        try:

            headerByte = self.connection.read(1)

            if (headerByte == b'\x03'):
                payload = self.connection.read(2)

                value = struct.unpack('<H', payload)[0]
                return value
            return None

        except serial.SerialException as e:
            msg = 'Błąd portu USB. Sprawdź połączenie i zacznij pomiary ponownie'
            self.ierrors.message('Błąd USB', msg)
            self.endConnection()
            if self.ierrors.exec():
                self.ierrors.close()
                call(["devcon.exe", "remove", "USB\VID_0D59&PID_0005*"])
                self.rescan()
                self.endConnection()

        except serial.serialutil.SerialException:
            msg = 'Błąd portu USB. Sprawdź połączenie i zacznij pomiary ponownie'
            self.ierrors.message('Błąd USB', msg)
            if self.ierrors.exec():
                self.ierrors.close()
                call(["devcon.exe", "remove", "USB\VID_0D59&PID_0005*"])
                self.rescan()
                self.endConnection()

        except ValueError:
            msg = 'Błąd wartości danych.Wykryto wartość None pochodzącą z podlączonego urządzenia.Sprawdź wartość baundrate'
            self.ierrors.message('Błąd danych', msg)
            if self.ierrors.exec():
                self.ierrors.close()
                self.endConnection()

    def reconnect(self):
        if self.connection.isOpen():
            self.connection.close()
            self.connection.port = f'{self.COM}'
            self.connection.baudrate = self.baudrate
            self.connection.timeout = None
            self.connection.open()

    def endConnection(self):
        # self.connection.write(b'k')

        self.connection.flush()
        self.connection.close()


# app = QApplication(sys.argv)
# win = SerialConnection()
# win.showDevices()
# win.connect("Arduino Mega", "115200")
# win.connection.write(b's')
# while True:
#     a = win.readValue()
#     print(a)


# sys.exit(app.exec_())
