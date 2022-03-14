from multiprocessing.sharedctypes import Value
from Errors import Errors
from TimePrompt import TimePrompt
from libraries import *
import re


class SerialConnection(QtWidgets.QWidget):
    def __init__(self):
        super(SerialConnection, self).__init__()
        self.devicesList = []
        self.COM = ''
        self.baudrate = 0
        self.connection = None
        self.ports = []
        self.storage = []
        self.lastValue = 0
        self.overflow = 0xFFFF
        self.ierrors = Errors()
        self.timePopUp = None
        self.timer = QtCore.QTimer()
        self.tmp, self.value = 0, 1
        self.title = ''
        self.flag = ''
        self.config = ''
        self.path = ''
        self.chooise = ''

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

    def monit(self, popupObj):
        self.timePopUp = popupObj

    def connect(self, device, baudrate, tenderness):
        try:
            if isinstance(tenderness, str):
                tenderness = float(tenderness)
            else:
                raise ValueError

            self.connection = sr.Serial()
            self.baudrate = int(baudrate)
            for port in self.ports:
                if device in port.description:
                    self.COM = port[0]
                    print(self.COM)
            self.connection.port = f'{self.COM}'
            self.connection.baudrate = self.baudrate
            self.connection.bytesize = serial.EIGHTBITS
            self.connection.stopbits = serial.STOPBITS_ONE
            self.connection.parity = serial.PARITY_NONE
            self.connection.timeout = None
            self.config = {"timestamp": ["Device", "Port", "Baudrate", "Tenderness"],
                           "Ni": [device, self.connection.port, self.connection.baudrate, tenderness], }
            print(self.connection.isOpen())
            self.connection.close()
            self.connection.open()

        except ValueError as value:
            value = "\n Niepoprawna wartość czułości. Wybierz ponownie. Jesli jest zmiennoprzecinkowa wykorzystaj kropkę \" . \" "
            self.ierrors.message('Błąd', value)
            if self.ierrors.exec():
                self.ierrors.close()
                self.endConnection()
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
        time.sleep(3)
        call(["devcon.exe", "rescan"])

    # def calc_checksum(self, data):
    #     calculated_checksum = 0
    #     for byte in data:
    #         calculated_checksum ^= byte
    #     return calculated_checksum

    def writers(self, row):
        with open(f'{self.path}RAW {self.title}.csv', 'a+', newline="") as fd:
            writer = csv.writer(fd, delimiter=';', quoting=csv.QUOTE_NONE)
            writer.writerow(row)

    def createCsv(self):    # metoda do stworzenia określonego pliku csv
        title_file = f"RAW {self.title}.csv"
        self.path = r'D:\\MeansurePerioid\\wyniki pomiarów\\'
        if not Path(self.path+self.title).is_file():
            headers = ["timestamp", "Ni"]
            sf = pd.DataFrame(self.config, columns=headers)
            sf.to_csv(Path(self.path+title_file), encoding='utf-8-sig',
                      index=False, sep=';', header=headers,)

    def validTime(self, amountOfSeconds):
        time.sleep(amountOfSeconds)
        self.flag = False

    def meansureRange(self, chooise, filename):
        self.title = filename
        self.chooise = chooise
        self.createCsv()
        time.sleep(0.5)
        listOfTime = re.split(r'(\D+)', chooise)
        if listOfTime[1].strip() == 's':
            self.readValue(int(listOfTime[0]))
        if listOfTime[1].strip() == 'min':
            self.readValue(int(listOfTime[0])*60)
        if listOfTime[1].strip() == 'h':
            self.readValue(int(listOfTime[0])*3600)

    def readValue(self, timeOfExecution):
        self.flag = True
        thread1 = threading.Thread(
            target=self.validTime, args=(timeOfExecution,))
        thread1.start()
        try:
            while self.flag:

                now = datetime.now()
                timeNow = now.strftime("%H:%M:%S")
                raw = self.connection.read(2)

                Ni = struct.unpack('<H',  raw)[0]
                valueDifference = Ni - self.lastValue
                if valueDifference < 0:
                    valueDifference += self.overflow

                self.storage = [timeNow, valueDifference]
                self.writers(self.storage)
                self.lastValue = Ni
            time.sleep(1)
            self.timePopUp.message(msg='Koniec Pomiaru')
            if self.timePopUp.exec():
                pass
                # self.close()

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
            # self.connection.port = f'{self.COM}'
            # self.connection.baudrate = self.baudrate
            # self.connection.timeout = None
            self.connection.open()

    def endConnection(self):
        time.sleep(1)
        self.connection.flushOutput()
        time.sleep(1)
        self.connection.close()


# app = QApplication(sys.argv)
# win = SerialConnection()
# win.showDevices()
# # win.connect("USB Serial", "9600")
# # win.connect("Arduino Uno", "19200")
# win.connect("USB", "1000000", '1')
# # win.start()

# # win.meansureRange('5 s', 'rraas')


# # path_s = r'D:\\MeansurePerioid\\wyniki pomiarów\\testyUNO\\'
# # # title = "arduinomega12.csv"
# # title = "arduinoTEST6.csv"  # sprawdz algorytm dla 2 i Nx

# # csvs.to_csv(Path(path_s+title), index=False, sep=';')


# # def currTime():
# #     return time.time_ns() / (10 ** 9)


# # def csvWrite(row):

# #     with open(f'{path_s+title}', 'a+', newline='') as file:
# #         writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_NONE)
# #         writer.writerow(row)
# #         file.close()


# # list = ["timestamp", "Ni", "Nx", "tx", "t", "f"]
# # # csvWrite(list)
# # win.start()

# # i = 0
# # t = 0


# # def test():
# #     global t
# #     row = win.readValue()
# #     print(f"odczytano{row}")
# #     if row is not None:
# #         now = datetime.now()
# #         time = now.strftime("%H:%M:%S")
# #         # tg = row[0]*(1/(16000000))
# #         # t += tg
# #         # freq = 1/(row[0]*(1/(16000000)))
# #         l = [time, row]
# #         if row:
# #             csvWrite(l)

# #     else:  # przeklej do klasy plot
# #         pass


# # def testsa1():
# #     a = win.readValue()
# #     print(a)


# # testsa1()
# # while True:
# # test()
# # timer = QtCore.QTimer()
# # timer1 = QtCore.QTimer()
# # timer.timeout.connect(test)
# # timer.start()
# # timer1.timeout.connect(testsa)
# # timer1.start(1)
# sys.exit(app.exec_())
