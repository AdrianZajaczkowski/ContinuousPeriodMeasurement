from Errors import Errors
from Liblarys import *


class SerialConnection(QtWidgets.QWidget):
    def __init__(self):
        super(SerialConnection, self).__init__()
        self.next = 0
        self.devicesList = []
        self.COM = ''
        self.baudrate = 0
        self.connection = None
        self.ports = []
        self.storage = []
        self.ierrors = Errors()
        self.timer = QtCore.QTimer()
        self.tmp, self.value = 0, 1

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
        print(f'aaaaa{device}')
        print(f'bbbb{baudrate}')
        try:
            self.connection = sr.Serial()
            self.baudrate = int(baudrate)
            for port in self.ports:
                if device in port.description:
                    self.COM = port[0]
                    print(self.COM)
            self.connection.port = f'{self.COM}'
            self.connection.baudrate = self.baudrate
            # self.connection = sr.Serial(port=self.COM, baudrate=self.baudrate)
            # self.connection.bytesize = EIGHTBITS
            # self.connection.stopbits = STOPBITS_ONE
            # self.connection.parity = "N"
            # # self.connection.dsrdtr = True
            # self.connection.timeout = 1
            print(self.connection.isOpen())
            # self.connection.flush()
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

            # arr = [None, None, None]

            start = self.connection.read(2)
            startseq = struct.unpack('<H',  start)[0]
            if startseq == 2:
                first = self.connection.read(2)
                NxValue = struct.unpack('<H',  first)[0]

                end = self.connection.read(2)
                endValue = struct.unpack('<H',  end)[0]
                if endValue == 3:

                    # self.storage.append(NxValue)

                    if NxValue >= 1300000:
                        pass
                    else:
                        return NxValue

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

    def start(self):
        sleep(1)
        x = 's'
        self.connection.write(bytes(x, 'utf-8'))

    def test2(self, x):
        print(" serial conenction get data:")
        print(x)

    def endConnection(self):
        sleep(1)
        self.connection.write(bytes('k', 'utf-8'))
        sleep(1)
        self.connection.flushOutput()
        self.connection.close()


# app = QApplication(sys.argv)
# win = SerialConnection()
# win.showDevices()
# win.connect("Arduino Mega", "38400")
# win.start()

# csvs = pd.DataFrame()
# path_s = r'D:\\MeansurePerioid\\wyniki pomiarów\\'
# title = "testowypomiar4.csv"
# csvs.to_csv(Path(path_s+title), index=False, sep=';')


# def currTime():
#     return time.time_ns() / (10 ** 9)


# def csvWrite(row):

#     with open(f'{path_s+title}', 'a+', newline='') as file:
#         writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_NONE)
#         writer.writerow(row)
#         file.close()


# win.start()
# row = []
# i = 0


# def test():
#     global i
#     row = win.readValue()
#     if row is not None:
#         now = datetime.now()
#         time = now.strftime("%H:%M:%S")
#         freq = 1/(row*(1/(16000000)))
#         l = [time, row, freq]
#         if row:
#             csvWrite(l)
#         print(row)
#         i += 1
#     else:  # przeklej do klasy plot
#         pass


# def testsa1():
#     row.append(win.readValue())


# # while True:
# #     print(win.readValue())
# timer = QtCore.QTimer()
# # timer1 = QtCore.QTimer()
# timer.timeout.connect(test)
# timer.start()
# # timer1.timeout.connect(testsa)
# # timer1.start(1)
# sys.exit(app.exec_())
