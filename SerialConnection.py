from multiprocessing.sharedctypes import Value
from Errors import Errors
from TimePrompt import TimePrompt
from libraries import *
import re
import pickle
import bz2


class SerialConnection(QObject):
    finishSignal = pyqtSignal(str)
    popUpSignal = pyqtSignal(str)
    dataSignal = pyqtSignal(object, object)
    errorSignal = pyqtSignal()

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
        self.df_tmp, self.value = None, 1
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
            self.connection.port = f'{self.COM}'
            self.connection.baudrate = self.baudrate
            self.connection.bytesize = serial.EIGHTBITS
            self.connection.stopbits = serial.STOPBITS_ONE
            self.connection.parity = serial.PARITY_NONE
            self.connection.timeout = None
            self.config = {'timestamp': ["Device", "Port", "Baudrate", "Tenderness"],
                           'Nxi': [device, self.connection.port, self.connection.baudrate, tenderness], }
            self.connection.close()
            self.connection.open()
            
        except ValueError as value:
            value = "\n Niepoprawna wartość czułości. Wybierz ponownie. Jesli jest zmiennoprzecinkowa wykorzystaj kropkę \" . \" "
            self.ierrors.message('Błąd', value)
            if self.ierrors.exec():
                self.ierrors.close()
                self.endConnection()
                self.errorSignal.emit()
        except TypeError as ty:
            msg = "\n Brak wybranej płytki lub baundrate.Wybierz ponownie ustawienia płytki"
            self.ierrors.message('Błąd', msg)
            if self.ierrors.exec():
                self.ierrors.close()
                self.endConnection()
                self.errorSignal.emit()
        except Exception as e:
            msg = "\n Brak podłaczonej płytki. Podłącz płytkę i zacznij ponownie."
            self.ierrors.message('Błąd', msg)
            if self.ierrors.exec():
                self.ierrors.close()
                self.endConnection()
                self.errorSignal.emit()

    def rescan(self):
        time.sleep(3)
        call(["devcon.exe", "rescan"])

    # def calc_checksum(self, data):
    #     calculated_checksum = 0
    #     for byte in data:
    #         calculated_checksum ^= byte
    #     return calculated_checksum

    def writers(self, dictionaryList):
        df_final = pd.DataFrame.from_dict(dictionaryList)
        self.compressed_pickle(df_final, True)
        # with open(f'{self.path}RAW {self.title}.csv', 'a+', newline="") as fd:
        #     writer = csv.writer(fd, delimiter=';', quoting=csv.QUOTE_NONE)
        #     writer.writerow(row)

    def compressed_pickle(self, df_data, flag):

        # Path(self.path+title_file)
        if flag:
            new_df = self.df_tmp.append(df_data, ignore_index=True)
            f = bz2.BZ2File(Path(f'{self.path}RAW {self.title}.pbz2'), 'wb')
            pickle.dump(new_df, f)
            f.close()
        else:
            self.df_tmp = df_data

    def createPickleFile(self):    # metoda do stworzenia określonego pliku csv
        self.path = r'D:\\MeansurePerioid\\wyniki pomiarów\\'
        if not Path(f'{self.path}RAW {self.title}.pbz2').is_file():
            headers = ["timestamp", "Nxi"]
            sf = pd.DataFrame(self.config, columns=headers)
            self.compressed_pickle(sf, False)
            # sf.to_csv(Path(self.path+title_file), encoding='utf-8-sig',
            #           index=False, sep=';', header=headers,)

    def validTime(self, amountOfSeconds):
        time.sleep(amountOfSeconds)
        self.flag = False

    def meansureRange(self, chooise, filename):
        self.title = filename
        self.chooise = chooise
        self.popUpSignal.emit(chooise)
        self.createPickleFile()
        time.sleep(0.5)
        listOfTime = re.split(r'(\D+)', chooise)
        if listOfTime[1].strip() == 's':
            self.readValue(int(listOfTime[0]))
        if listOfTime[1].strip() == 'min':
            self.readValue(int(listOfTime[0])*60)
        if listOfTime[1].strip() == 'h':
            self.readValue(int(listOfTime[0])*3600)
        self.finishSignal.emit(chooise)

    def readValue(self, timeOfExecution):
        dictionary_serial = {'timestamp': None,
                             'Nxi': None}

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
                dictionary_serial['timestamp'] = timeNow
                dictionary_serial['Nxi'] = valueDifference
                self.storage.append(dictionary_serial)
                self.lastValue = Ni
            self.writers(self.storage)
            # time.sleep(1)
            # self.timePopUp.message(msg='Koniec Pomiaru')
            # if self.timePopUp.exec():
            #     pass

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
