from ctypes.wintypes import BYTE

from serial.serialutil import EIGHTBITS, PARITY_EVEN, PARITY_MARK, PARITY_ODD, STOPBITS_ONE, STOPBITS_TWO
from Errors import Errors
from Liblarys import *
import struct
from subprocess import call
from time import sleep


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
        self.F_CPU = 16000000
        self.overflow = 65536

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
            self.connection.port = f'{self.COM}'
            self.connection.baudrate = self.baudrate
            self.connection.timeout = None
            self.connection.rtscts = True
            self.connection.dsrdtr = True
            self.connection.stopbits = STOPBITS_TWO
            # self.connection.parity = PARITY_MARK
            self.connection.bytesize = EIGHTBITS
            print(self.connection.isOpen())
            self.connection.open()

            # self.connectionTest()
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
        call(["devcon.exe", "rescan"])
        sleep(30)

    def calc_checksum(self, data):
        calculated_checksum = 0
        for byte in data:
            calculated_checksum ^= byte
        return calculated_checksum

    def readValue(self):
        try:
            # if (self.connection.inWaiting() > 0):
            # struct <- urzyć i przetestowac
            if self.connection.read() != b'\x10':
                return None
            if self.connection.read() != b'\x02':
                return None
            payload_len = self.connection.read()[0]
            if payload_len != 2:
                # could be other type of packet, but not implemented for now
                return None
            payload = self.connection.read(payload_len)
            checksum = self.connection.read()[0]

            if checksum != self.calc_checksum(payload):
                return None
            if self.connection.read() != b'\x10':
                return None
            if self.connection.read() != b'\x03':
                return None
            unpacked = struct.unpack("<H", payload)

            return unpacked[0]  # tx

        except serial.SerialException as e:
            msg = 'Błąd portu USB. Sprawdź połączenieaa i zacznij pomiary ponownie'
            self.ierrors.message('Błąd USB', msg)
            self.endConnection()
            if self.ierrors.exec():
                self.ierrors.close()
                call(["devcon.exe", "remove", "USB\VID_0D59&PID_0005*"])
                self.rescan()
            return None
        except serial.serialutil.SerialException:
            msg = 'Błąd portu USB. Sprawdź połączenie i zacznij pomiary ponownie'
            self.ierrors.message('Błąd USB', msg)
            if self.ierrors.exec():
                self.ierrors.close()
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

    # def __getitem__(self, key):
    #     return self.second[key]

    def endConnection(self):
        self.connection.close()


# app = QApplication(sys.argv)
# win = SerialConnection()
# win.showDevices()
# win.connect("Arduino Mega", "115200")
# # win.connection.write(b's')
# while True:
#     win.readValue()


# sys.exit(app.exec_())
