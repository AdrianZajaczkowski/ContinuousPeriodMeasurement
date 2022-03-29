# klasa do analizy,zapisu i wyświetlania danych
from sqlite3 import Time
from serial.win32 import EV_CTS
from libraries import *
from ComboList import *
from ConfigDropList import *
from Errors import Errors
from TimePrompt import TimePrompt

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


class Plot_Window(QMainWindow):
    serialSignal = pyqtSignal(str, str)
    RawFileSignal = pyqtSignal()
    AnalyzedFileSignal = pyqtSignal(object, object)
    logging.info("Plot init")

    def __init__(self, parent, **kwargs):
        self.pkg = kwargs.pop('pkg')
        self.serial = kwargs.pop('serial')
        self.timemeansure = self.pkg['meansurmentTime']
        logging.info(f"Plot init {self.pkg}")
        logging.info(f"Plot init {self.serial}")
        logging.info(f"Plot init {self.timemeansure}")
        super(Plot_Window, self).__init__(parent, **kwargs)
        self.device = None
        self.baudrate = None
        self.tenderness = None
        self.currentDay = None
        self.plots = None
        self.mainPlot = None
        self.WindowFont = None
        self.GridFont = None
        self.df_tmp = None
        self.changeSecond, self.changeMain = True, True
        self.full = False
        self.F_CPU = 16000000
        self.PlotCount = 1
        self.timeList = []
        self.freqList = []
        self.prompt = TimePrompt(self)
        self.files = ConfigDropList(serial=self.serial)
        self.title_file, self.path, self.openedfile,  self.openedPath = '', '', '', ''
        self.exit = QAction("Exit Application",
                            triggered=lambda: self.exit_app)
        self.curentMeansureTime = None
        self.fileMeansureTime = None
        self.ierrors = Errors(self)
        self._config = {"Nxi": ["platforma:", "Baudrate:", "Czułość przetwornika"],
                        "Txi": [self.device, self.baudrate, self.tenderness]}
        self.setWindowTitle("Python 3.9.7")
        self.serial.errorSignal.connect(self.wrongConfig)
        self.uiSet()

    def closeConnection(self):
        self.serial.endConnection()

    def currentDataMeansure(self):
        self.currentDay = datetime.now()
        self.curentMeansureTime = str(
            self.currentDay.strftime("%Y_%m_%d %H_%M_%S"))

    def uiSet(self):
        self.currentDataMeansure()

        self.WindowFont = QFont()
        self.WindowFont.setPixelSize(17)
        self.GridFont = QFont()
        self.GridFont.setPixelSize(20)
        self.setFont(self.WindowFont)
        self.createFolder()
        self.setMinimumSize(800, 600)
        self.setGeometry(0, 0, 1920, 1080)
        frame = self.frameGeometry()
        self.move(frame.topLeft())
        self.buttonsConfig()

        self.widget = QWidget()
        self.grid = QGridLayout()
        self.timeBox = QGroupBox("Czas pomiaru")
        self.timeButtons = QGridLayout()
        self.chart = pg.GraphicsLayoutWidget(show=True)

        self.widget.setLayout(self.grid)
        self.grid.addWidget(self.startCatchData, 0, 0)
        self.grid.addWidget(self.analyzeFile, 1, 0)
        self.grid.addWidget(self.plotFile, 2, 0)
        self.grid.addWidget(self.plotPointsInChar, 3, 0)
        self.grid.addWidget(self.chart, 0, 1, 13, 4)
        self.timeButtons.addWidget(self.setTimeMeansure, 0, 0)
        self.timeBox.setLayout(self.timeButtons)
        self.grid.addWidget(self.timeBox, 4, 0)
        self.setCentralWidget(self.widget)

    def showSecondWindow(self):
        self.showMaximized()

    def buttonsConfig(self):
        self.setTimeMeansure = ComboList(
            self, option=self.timemeansure["standard"], default=self.timemeansure["default"])

        self.startCatchData = QPushButton('Rozpocznij pobieranie danych')
        self.startCatchData.clicked.connect(self.startMeanurments)
        self.analyzeFile = QPushButton('Analizuj dane')
        self.analyzeFile.clicked.connect(self.openRawFile)
        self.plotFile = QPushButton('Wyświetl dane')
        self.plotFile.clicked.connect(self.showAnalyzedData)
        self.plotPointsInChar = QPushButton('Pokaż punkty wykresu')
        self.plotPointsInChar.clicked.connect(self.plotPointer)

    def showAnalyzedData(self):
        self.openAnalyzedFile()

        self.AnalyzedFileSignal.connect(self.analyzedPlot)
        # self.showPlot(self.timeList, self.freqList)

    def analyzedPlot(self, time, freq):
        self.showPlot(time, freq)
        self.timeList, self.freqList = [], []

    def startMeanurments(self):
        self.startCatchData.setEnabled(False)
        self.startCatchData.setText('Pobieranie danych')
        self.currentDataMeansure()
        self.files.setDefaulfValue(
            name="meansurmentTime", position="default", element=self.setTimeMeansure.default)

        if self.timemeansure["default"]:
            self.thread2 = threading.Thread(
                target=self.serial.meansureRange, args=(self.setTimeMeansure.default, self.curentMeansureTime,))
        else:
            self.thread2 = threading.Thread(
                target=self.serial.meansureRange, args=(self.setTimeMeansure.option, self.curentMeansureTime,))
        self.serial.popUpSignal.connect(self.popUpTime)
        self.serial.finishSignal.connect(self.buttonState)
        self.thread2.start()

    def buttonState(self, desc):
        self.prompt.message(msg=f'Pomiar trwał: {desc}')
        if self.prompt.show():
            self.prompt.layout.removeWidget()

        self.startCatchData.setText('Rozpocznij pobieranie danych')
        self.startCatchData.setEnabled(True)

    def wrongConfig(self):
        self.startCatchData.setEnabled(False)

    def popUpTime(self, timeDesc):
        self.prompt.message(
            msg=f'Czas pobierania danych: {timeDesc}. Proszę czekać.')
        if self.prompt.show():
            self.prompt.layout.removeWidget()

    def showPlot(self, x, y):   # metoda do dodania kolejnego wykresu pod aktualnym pomiarem
        print(len(x))
        print(len(y))

        if self.PlotCount == 2:
            self.full = True
        if not self.full:
            self.plots = self.chart.addPlot(row=0, col=0,
                                            title=f"<b><p style=\"color: black\">{self.title_file}</p></b><")
            self.plotLine = self.plots.plot(pen=pg.mkPen('r', width=2))
            self.plots.showGrid(x=True, y=True, alpha=1)
            labels = {'color': 'w',
                      'font-size': f'{self.GridFont.pixelSize()}px'}
            self.plots.setLabel('left', 'Frequency',
                                units='Hz', **labels)
            self.plots.setLabel('bottom', 'Time', units='s', **labels)
            self.plots.getAxis("bottom").setTickFont(self.GridFont)
            self.plots.getAxis("bottom").setStyle(tickTextOffset=20)
            self.plots.getAxis("left").setTickFont(self.GridFont)
            self.plots.getAxis("left").setStyle(tickTextOffset=20)
            self.plotLine.setData(x, y)
            self.PlotCount += 1
        else:
            self.chart.removeItem(self.plots)
            self.full = False
            self.PlotCount = 1
            self.showPlot(x, y)

    def plotPointer(self):
        if self.changeSecond:
            self.plotPointsInChar.setText("Ukryj punkty wykresu")
            self.plotLine.setSymbol('o')
            self.changeSecond = False
        else:
            self.plotPointsInChar.setText("Pokaż punkty wykresu")
            self.plotLine.setSymbol(None)
            self.changeSecond = True

    def analyzeDataFromFile(self, sheet):  # Metoda do wizualizacji danych
        t = 0
        calculated_list = []
        calculated_dictionary = {'Nxi': {},
                                 'Txi': {},
                                 'Xxi': {},
                                 't': {},
                                 'fxi': {},
                                 'Błąd kwantowania (Nx+1)': {},
                                 'Błąd bezwzględny': {},
                                 'Błąd względny δ': {},
                                 'Błąd względny δ%': {},
                                 }

        for i in range(len(sheet)):

            Nxi = int(sheet[i])
            Txi = Nxi*(1/self.F_CPU)
            Tx1 = (Nxi+1)*(1/self.F_CPU)
            fxi = 1/Txi
            Xxi = fxi/self.tenderness
            bwzg = round((Tx1-Txi), 8)
            wzg = round((bwzg/Txi), 8)
            t += Txi
            proc_wzg = wzg*100
            calculated_dictionary['Nxi'] = Nxi
            calculated_dictionary['Txi'] = Txi
            calculated_dictionary['Błąd kwantowania (Nx+1)'] = Tx1
            calculated_dictionary['fxi'] = fxi
            calculated_dictionary['Xxi'] = Xxi
            calculated_dictionary['Błąd bezwzględny'] = bwzg
            calculated_dictionary['Błąd względny δ'] = wzg
            calculated_dictionary['t'] = t
            calculated_dictionary['Błąd względny δ%'] = proc_wzg
            # self.timeList.append(t)
            # self.freqList.append(Xxi)

            calculated_list.append(calculated_dictionary.copy())

        self.addToPickle(calculated_list, True)

        self.RawFileSignal.emit()

    def createFolder(self):
        current_directory = os.getcwd()
        final_directory = os.path.join(current_directory, r'wyniki pomiarów')
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)

    def dataframecreate(self, param):
        file = pd.DataFrame(param)
        print(file)

    def createCsv(self):    # Note metoda do stworzenia określonego pliku csv
        config = {"time": ["platforma:", "Baudrate:", "Czułość przetwornika"],
                  "Nxi": [self.device, self.baudrate, self.tenderness]}

        self.title_file = f"pomiar z {self.curentMeansure}.csv"
        self.path = r'D:\\MeansurePerioid\\wyniki pomiarów\\'
        if not Path(self.path+self.title_file).is_file():
            headers = ["Nxi", "Txi", "Xxi", "t", "fxi",
                       " Błąd kwantowania (Nx+1)", "Błąd bezwzględny", "Błąd względny δ", "Błąd względny δ%"]
            sf = pd.DataFrame(config, columns=headers)
            sf.to_csv(Path(self.path+self.title_file), encoding='utf-8-sig',
                      index=False, sep=';', header=headers,)

    def updateCsv(self, row):     # metoda do aktualizowania pliku csv
        with open(f'{self.path+self.title_file}', 'a+', newline='') as file:
            writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_NONE)
            writer.writerow(row)
            file.close()

    def addToPickle(self, df_data, flag):
        if flag:
            self.df_tmp = self.df_tmp.append(df_data, ignore_index=True)
            f = bz2.BZ2File(Path(f'{self.path}{self.title_file}.pbz2'), 'wb')
            pickle.dump(self.df_tmp, f)
            f.close()
        else:
            self.df_tmp = df_data

    # metoda do stworzenia określonego pliku csv

    def createPickleSheet(self, flagFile):
        if flagFile:
            title = self.curentMeansureTime
        else:
            title = self.fileMeansureTime
        config = {"Nxi": ["platforma:", "Baudrate:", "Czułość przetwornika"],
                  "Txi": [self.device, self.baudrate, self.tenderness]}
        headers = ["Nxi", "Txi", "Xxi", "t", "fxi",
                   " Błąd kwantowania (Nx+1)", "Błąd bezwzględny", "Błąd względny δ", "Błąd względny δ%"]
        self.title_file = f"pomiar z {title}"
        self.path = r'D:\\MeansurePerioid\\wyniki pomiarów\\'
        if not Path(f'{self.path}{self.title_file}.pbz2').is_file():
            sf = pd.DataFrame(config, columns=headers)
            self.addToPickle(sf, False)
            return True
        else:
            return False

    def openAnalyzedFile(self):
        file = QDir.currentPath()
        dialog = QFileDialog(self)
        dialog.setWindowTitle('File')
        dialog.setNameFilters(
            ['Pickle files (*.pbz2)'])
        dialog.setDirectory(file)
        dialog.setFileMode(QFileDialog.ExistingFile)

        if dialog.exec_() == QDialog.Accepted:
            self.openedfile = dialog.selectedFiles()
            if self.openedfile:
                self.openedPath = str(self.openedfile[0])
                analyzeThreading = threading.Thread(
                    target=self.readAnalyzedFile, args=(self.openedPath,))
                analyzeThreading.start()

    def readAnalyzedFile(self, filename):
        with bz2.BZ2File(filename, 'rb') as serialSheet:
            data = pickle.load(serialSheet)

        timeListtmp = data['t'][7:]
        freqListtmp = data['Xxi'][7:]
        self.timeList = list(map(float, timeListtmp))
        self.freqList = list(map(float, freqListtmp))
        self.AnalyzedFileSignal.emit(self.timeList, self.freqList)

    # metoda do odczytu danych do wizualizacji
    def readRawDataFromFile(self, filename):
        with bz2.BZ2File(filename, 'rb') as serialSheet:
            data = pickle.load(serialSheet)

        filenameList = filename.split()
        timePartOfList = filenameList[-1].split('.')
        new_title = f'{filenameList[-2]} {timePartOfList[0]}'
        sheet = list(data['Nxi'][7:])
        self.device = data['Nxi'][0]
        self.baudrate = data['Nxi'][2]
        self.tenderness = float(data['Nxi'][3])
        if self.curentMeansureTime == new_title:
            fileState = self.createPickleSheet(True)
        else:
            self.fileMeansureTime = new_title
            fileState = self.createPickleSheet(False)
        if fileState:
            return sheet
        else:
            return False

    def openRawFile(self):   # metoda do wyszukania i wybrania pliku z poprzednimi pomiarami
        file = QDir.currentPath()
        dialog = QFileDialog(self)
        dialog.setWindowTitle('File')
        dialog.setNameFilters(
            ['All files (*)', 'Pickle files (*.pbz2)'])
        dialog.setDirectory(file)
        dialog.setFileMode(QFileDialog.ExistingFile)

        self.analyzeFile.setEnabled(False)
        if dialog.exec_() == QDialog.Accepted:
            self.openedfile = dialog.selectedFiles()
            if self.openedfile:
                self.openedPath = str(self.openedfile[0])
                data = self.readRawDataFromFile(self.openedPath)
                if data == False:
                    self.prompt.message(
                        msg=f'Plik już istnieje. Zapisano w:\n{self.path}{self.title_file}.pbz2')
                    if self.prompt.exec():
                        self.prompt.layout.removeWidget()
                    self.analyzeFile.setEnabled(True)
                else:
                    analyzeThread = threading.Thread(
                        target=self.analyzeDataFromFile, args=(data,))
                    self.analyzeFile.setText('Przetwarzanie danych')
                    analyzeThread.start()
                    self.RawFileSignal.connect(self.openButtonState)
        else:
            self.analyzeFile.setEnabled(True)

    def openButtonState(self):
        self.analyzeFile.setText('Analizuj dane')
        self.analyzeFile.setEnabled(True)
