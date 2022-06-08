from multiprocessing.sharedctypes import Value
from Errors import Errors
from TimePrompt import TimePrompt
from libraries import *
import re

# klasa odpowiedzialna za nawiązanie komunikacji z mikrokontrolerem


class SerialConnection(QObject):
    finishSignal = pyqtSignal(str)  # sygnał od zakończenia pomiaru
    popUpSignal = pyqtSignal(str)   # sygnał od powiadomienia o pońcu pomiaru

    def __init__(self):
        super(SerialConnection, self).__init__()
        self.devicesList = []
        self.COM = ''
        self.baudrate = 0
        self.ports = []
        self.storage = []
        self.lastValue = 0
        self.overflow = 0xFFFF
        self.ierrors = Errors()
        self.timer = QtCore.QTimer()
        self.connection = None
        self.timePopUp = None
        self.df_tmp, self.value = None, 1
        self.title = ''
        self.flag = ''
        self.config = ''
        self.path = ''
        self.meansureButtonState = True
        self.chooise = ''
        self.endianness = ''
    # wyświetlenie podpiętych mikrokontrolerów

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

    # konfigurowanie połączenia na podstawie parametrów
    def connect(self, device, baudrate, tenderness, endianness):
        try:
            self.endianness = endianness
   
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
            # self.connection.open()

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
            self.ierrors.message('Błąd', msg)
            if self.ierrors.exec():
                self.ierrors.close()
                self.endConnection()

    def rescan(self):  # metoda od poprawnego zakończenia połączenia po sprawdzeniu portów
        time.sleep(3)
        call(["devcon.exe", "rescan"])

    def writers(self, dictionaryList):  # zapis danych w słowniku
        logging.debug(f'file: create part2. Data=get')
        df_final = pd.DataFrame.from_dict(dictionaryList)
        self.compressed_pickle(df_final, True)

    # metoda od zapisu danych do pliku pickle w konfiguracji nagłówek+dane
    def compressed_pickle(self, df_data, flag):
        if flag:
            # new_df = self.df_tmp.append(df_data, ignore_index=True)
            new_df = pd.concat(
                [self.df_tmp, df_data], ignore_index=True)
            f = bz2.BZ2File(Path(f'{self.path}RAW {self.title}.pbz2'), 'wb')
            pickle.dump(new_df, f)
            logging.debug(f'file: done')
            f.close()
            # self.df_tmp = None
        else:
            self.df_tmp = df_data

    def createPickleFile(self):    # metoda do stworzenia określonego pliku csv
        self.path = r'..\\MeansurePerioid\\wyniki pomiarów\\'
        if not Path(f'{self.path}RAW {self.title}.pbz2').is_file():
            headers = ["timestamp", 'RAW L', 'RAW H', 'Ni', "Nxi"]
            sf = pd.DataFrame(self.config, columns=headers)
            self.compressed_pickle(sf, False)

    def validTime(self, amountOfSeconds):  # metoda od odliczania czasu pomiaru
        time.sleep(amountOfSeconds)
        logging.debug(f'readData: stop with {amountOfSeconds}s')
        self.flag = False
    # wyliczenie czasu pomiaru na podstawie wybranego argumentu czasu w sekundach

    def meansureRange(self, chooise, filename):
        logging.debug(f'meansure: set time')
        self.title = filename
        self.chooise = chooise
        self.popUpSignal.emit(chooise)  # powiadomienie o początku pomiaru
        self.createPickleFile()
        logging.debug(f'file: create part1')
        time.sleep(0.5)  # opóźnienie aby poprawnie stworzyć plik
        listOfTime = re.split(r'(\D+)', chooise)
        if listOfTime[1].strip() == 's':
            self.readValue(int(listOfTime[0]))
        if listOfTime[1].strip() == 'min':
            self.readValue(int(listOfTime[0])*60)
        if listOfTime[1].strip() == 'h':
            self.readValue(int(listOfTime[0])*3600)
        self.finishSignal.emit(chooise)
        logging.debug(f'readData: end')

    def readValue(self, timeOfExecution):  # odczyt danych z mikrokontrolera

        if not self.flag:
            try:
                logging.debug(f'self.connection: start')
                self.connection.open()
            except Exception as e:
                logging.info(f'{e}')
                pass

        logging.debug(f'readData: start {timeOfExecution}')
        dictionary_serial = {'timestamp': None, 'RAW L': None, 'RAW H': None, 'Ni': None,
                             'Nxi': None}
        self.flag = True
        thread1 = threading.Thread(
            target=self.validTime, args=(timeOfExecution,))
        thread1.start()

        try:
            while self.flag:

                now = datetime.now()
                timeNow = now.strftime("%H:%M:%S")
                raw1 = self.connection.read(1)
                raw2 = self.connection.read(1)
                raw = raw1+raw2

                Ni1 = struct.unpack(f'{self.endianness}B',  raw1)[0]
                Ni2 = struct.unpack(f'{self.endianness}B',  raw2)[0]
            
                Ni = struct.unpack(f'{self.endianness}H',  raw)[0]
                valueDifference = Ni - self.lastValue
                if valueDifference <= 0:
                    valueDifference += self.overflow
                dictionary_serial['timestamp'] = timeNow
                dictionary_serial['RAW L'] = Ni1
                dictionary_serial['RAW H'] = Ni2
                dictionary_serial['Ni'] = Ni
                dictionary_serial['Nxi'] = valueDifference
                self.storage.append(dictionary_serial.copy())
                self.lastValue = Ni
            self.writers(self.storage)
            self.connection.close()
            logging.debug(f'self.connection: end')

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

    def endConnection(self):  # zamknięcie połączenia
        try:
            self.meansureButtonState = False
            time.sleep(1)
            self.connection.close()
            time.sleep(1)
            self.connection.flushOutput()
        except serial.serialutil.PortNotOpenError:
            self.connection.close()
