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

    def __init__(self, parent, **kwargs):
        self.pkg = kwargs.pop('pkg')
        self.serial = kwargs.pop('serial')
        self.timemeansure = self.pkg['meansurmentTime']
        logging.info(
            f"init package: {self.pkg},serial:{self.serial},timemeansure:{self.timemeansure}")
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
        self.pickleSheet = None
        self.changeSecond, self.changeMain = True, True
        self.full = False
        self.F_CPU = 16000000
        self.PlotCount = 1
        self.timeList = []
        self.freqList = []
        self.prompt = TimePrompt(self)
        self.files = ConfigDropList(serial=self.serial)
        self.title_file, self.path, self.openedfile,  self.openedPath = '', '', '', ''

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
        logging.info(f'uiset: start')
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
        self.grid.addWidget(self.convertToCsvButton, 3, 0)
        self.grid.addWidget(self.plotPointsInChar, 4, 0)
        self.grid.addWidget(self.chart, 0, 1, 13, 4)
        self.timeButtons.addWidget(self.setTimeMeansure, 0, 0)
        self.timeBox.setLayout(self.timeButtons)
        self.grid.addWidget(self.timeBox, 5, 0)
        self.setCentralWidget(self.widget)
        logging.info(f'uiset: done')

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
        self.convertToCsvButton = QPushButton('Konvertuj aktualny plik do CSV')
        self.convertToCsvButton.clicked.connect(self.convertPickleToCsv)
        self.plotPointsInChar = QPushButton('Pokaż punkty wykresu')
        self.plotPointsInChar.clicked.connect(self.plotPointer)
        self.convertToCsvButton.setEnabled(False)

    def showAnalyzedData(self):
        self.openAnalyzedFile()
        self.AnalyzedFileSignal.connect(self.analyzedPlot)

    def analyzedPlot(self, time, freq):
        logging.debug(f'visualization: start ')
        self.showPlot(time, freq)
        self.timeList, self.freqList = [], []

    def startMeanurments(self):
        logging.debug(f'get data: start')
        self.startCatchData.setEnabled(False)
        self.startCatchData.setText('Pobieranie danych')
        self.currentDataMeansure()
        logging.debug(f'get data: set time')
        self.files.setDefaulfValue(
            name="meansurmentTime", position="default", element=self.setTimeMeansure.default)

        if self.timemeansure["default"]:
            meansureThread = threading.Thread(
                target=self.serial.meansureRange, args=(self.setTimeMeansure.default, self.curentMeansureTime,))
        else:
            meansureThread = threading.Thread(
                target=self.serial.meansureRange, args=(self.setTimeMeansure.option, self.curentMeansureTime,))
        logging.debug(f'meansure thread: set {meansureThread}')
        self.serial.popUpSignal.connect(self.popUpTime)
        self.serial.finishSignal.connect(self.buttonState)
        logging.debug(f'meansure thread: start {meansureThread}')
        meansureThread.start()

    def buttonState(self, desc):
        logging.info(f'get data: end capture')
        self.prompt.message(msg=f'Pomiar trwał: {desc}')
        if self.prompt.show():
            self.prompt.layout.removeWidget()

        self.startCatchData.setText('Rozpocznij pobieranie danych')
        self.startCatchData.setEnabled(True)

    def wrongConfig(self):
        logging.warning(
            ' class get wrong params, capture data unavailable!')
        self.startCatchData.setEnabled(False)

    def popUpTime(self, timeDesc):
        logging.info(
            f' pop-up message about meansure time:{timeDesc}')
        self.prompt.message(
            msg=f'Czas pobierania danych: {timeDesc}. Proszę czekać.')
        if self.prompt.show():
            self.prompt.layout.removeWidget()

    def showPlot(self, x, y):   # metoda do dodania kolejnego wykresu pod aktualnym pomiarem
        logging.debug(f'visualization: set coordinates ')
        logging.debug(
            f'visualization: len of coordinates:  x len:{len(x)}, y len:{len(y)} ')
        if self.PlotCount == 2:
            logging.debug(
                f'visualization: full of space for charts')
            self.full = True
        if not self.full:
            logging.debug(
                f'visualization: new chart ')
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
            logging.debug(
                f'visualization: delete previous chart, set new chart ')
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
        logging.info(f'analyzeThread: start')
        logging.debug(f'analyze raw file: start ')
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

            calculated_list.append(calculated_dictionary.copy())
        logging.debug(f'analyze raw file: end ')
        self.addToPickle(calculated_list, True)

        self.RawFileSignal.emit()
        logging.info(f'analyzeThread: done')

    def createFolder(self):
        current_directory = os.getcwd()
        final_directory = os.path.join(current_directory, r'wyniki pomiarów')
        if not os.path.exists(final_directory):
            logging.debug(f'create new folder:{final_directory}')
            os.makedirs(final_directory)

    # def createCsv(self):    # Note metoda do stworzenia określonego pliku csv
    #     logging.debug(f'create csv file: start')
    #     config = {"time": ["platforma:", "Baudrate:", "Czułość przetwornika"],
    #               "Nxi": [self.device, self.baudrate, self.tenderness]}

    #     self.title_file = f"pomiar z {self.curentMeansure}.csv"
    #     self.path = r'D:\\MeansurePerioid\\wyniki pomiarów\\'
    #     if not Path(self.path+self.title_file).is_file():
    #         headers = ["Nxi", "Txi", "Xxi", "t", "fxi",
    #                    " Błąd kwantowania (Nx+1)", "Błąd bezwzględny", "Błąd względny δ", "Błąd względny δ%"]
    #         sf = pd.DataFrame(config, columns=headers)
    #         sf.to_csv(Path(self.path+self.title_file), encoding='utf-8-sig',
    #                   index=False, sep=';', header=headers,)
    #         logging.debug(f'create csv file: created {self.title_file}')
    #         logging.debug(f'create csv file: done')

    # def updateCsv(self, row):     # metoda do aktualizowania pliku csv
    #     logging.debug(f'update csv file: start')
    #     with open(f'{self.path+self.title_file}', 'a+', newline='') as file:
    #         writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_NONE)
    #         writer.writerow(row)
    #         file.close()
    #         logging.debug(f'update csv file: done')

    def addToPickle(self, df_data, flag):
        if flag:
            logging.debug(
                f'pickle file: append sheet to header {self.path}{self.title_file}.pbz2 ')
            self.df_tmp = self.df_tmp.append(df_data, ignore_index=True)
            f = bz2.BZ2File(Path(f'{self.path}{self.title_file}.pbz2'), 'wb')
            pickle.dump(self.df_tmp, f)
            f.close()
        else:
            logging.debug(f'pickle file: hold headers ')
            self.df_tmp = df_data

    # metoda do stworzenia określonego pliku csv

    def createPickleSheet(self, flagFile):
        logging.debug(f'pickle file create: start ')
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
            logging.debug(
                f'pickle file create: created {self.path}{self.title_file}.pbz2 ')
            return True
        else:
            return False

    def openAnalyzedFile(self):
        logging.info(f'read existed file: start ')
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
                logging.info(
                    f'read existed file: selected file {self.openedfile[0]} ')
                self.openedPath = str(self.openedfile[0])
                logging.debug(
                    f'analyze threading: set ')
                analyzeThreading = threading.Thread(
                    target=self.readAnalyzedFile, args=(self.openedPath,))
                analyzeThreading.start()

    def readAnalyzedFile(self, filename):
        logging.debug(
            f'analyze threading: start ')
        logging.debug(f'read existed file: analyze selected file ')
        with bz2.BZ2File(filename, 'rb') as serialSheet:
            self.pickleSheet = pickle.load(serialSheet)
        logging.debug(
            f'pickle sheet: {self.pickleSheet} ')
        logging.debug(
            f'pickle sheet type: {type(self.pickleSheet)},len {len(self.pickleSheet)} ')
        timeListtmp = self.pickleSheet['t'][7:]
        freqListtmp = self.pickleSheet['Xxi'][7:]
        self.timeList = list(map(float, timeListtmp))
        self.freqList = list(map(float, freqListtmp))
        logging.debug(f'read existed file: done ')
        self.AnalyzedFileSignal.emit(self.timeList, self.freqList)
        logging.debug(
            f'analyze threading: done ')
        self.convertToCsvButton.setEnabled(True)

    def convertPickleToCsv(self):
        if len(self.pickleSheet):
            logging.debug('convert to CSV')
            # self.convertToCsvButton.setEnabled(True)
            df_csv = pd.DataFrame(self.pickleSheet)
            logging.debug(f'convert to CSV: {df_csv}')
            newTitleAndPath, _ = self.modifyFileName(self.openedPath)
            logging.debug(f'convert to CSV path: {self.openedPath}')
            logging.debug(f'convert to CSV new path: {newTitleAndPath}.csv')
            df_csv.to_csv(f'{newTitleAndPath}.csv')
            self.convertToCsvButton.setEnabled(False)

    def modifyFileName(self, filename):
        filenameLists = filename.split()
        timePartOfList = filenameLists[-1].split('.')
        logging.debug(
            f'parts of file title: file {filenameLists} {timePartOfList}')
        new_title = f'{filenameLists[-2]} {timePartOfList[0]}'
        titleForCsv = f'{" ".join([str(part) for part in filenameLists[:4]])} {timePartOfList[0]}'
        logging.debug(
            f'read raw file: file {filenameLists[-2]} {timePartOfList[0]} reading...')
        logging.debug(
            f'title for csv: {titleForCsv}')
        return titleForCsv, new_title
        # metoda do odczytu danych do wizualizacji

    def readRawDataFromFile(self, filename):
        logging.info(f'read raw file: {filename}')
        with bz2.BZ2File(filename, 'rb') as serialSheet:
            data = pickle.load(serialSheet)
        _, newFileName = self.modifyFileName(filename)
        logging.debug(
            f'New file {newFileName} ')
        # filenameList = filename.split()
        # timePartOfList = filenameList[-1].split('.')
        # new_title = f'{filenameList[-2]} {timePartOfList[0]}'

        sheet = list(data['Nxi'][7:])
        self.device = data['Nxi'][0]
        self.baudrate = data['Nxi'][2]
        self.tenderness = float(data['Nxi'][3])
        if self.curentMeansureTime == newFileName:
            fileState = self.createPickleSheet(True)
        else:
            self.fileMeansureTime = newFileName
            logging.debug(
                f'read raw file: new title set - {self.fileMeansureTime} ')
            fileState = self.createPickleSheet(False)
        if fileState:
            logging.debug(
                f'read raw file: done')
            return sheet
        else:
            logging.warning()(
                f'read raw file: cant read file, file exist')
            return False

    def openRawFile(self):   # metoda do wyszukania i wybrania pliku z poprzednimi pomiarami
        logging.info(f'select file')
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
            logging.info(f'raw file: selected ')
            if self.openedfile:
                self.openedPath = str(self.openedfile[0])
                data = self.readRawDataFromFile(self.openedPath)
                if data == False:
                    logging.info(f'raw file: file exist ')
                    self.prompt.message(
                        msg=f'Plik już istnieje. Zapisano w:\n{self.path}{self.title_file}.pbz2')
                    if self.prompt.exec():
                        self.prompt.layout.removeWidget()
                    self.analyzeFile.setEnabled(True)
                else:
                    logging.info(f'analyzeThread: set ')
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
