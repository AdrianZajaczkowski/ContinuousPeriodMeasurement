# klasa do analizy,zapisu i wyświetlania danych
from sqlite3 import Time
from serial.win32 import EV_CTS
from libraries import *
from ComboList import *
from ConfigDropList import *
from Monit import *
from Errors import Errors
from TimePrompt import TimePrompt
pg.setConfigOption('background', '#F0FFF0')
pg.setConfigOption('foreground', 'k')


class PlotWindow(QMainWindow):
    # serialSignal = pyqtSignal(str, str) # sygnał wykorzystywany pomiędzy klasą SerialConnection a obecna klasą
    # sygnał odpowiedzialny za powiadomienie o nowych przanalizowanych danych
    RawFileSignal = pyqtSignal()
    AnalyzedFileSignal = pyqtSignal()  # sygnał od analizy pliku

    def __init__(self, parent, **kwargs):
        self.pkg = kwargs.pop('pkg')
        self.serial = kwargs.pop('serial')
        self.timemeansure = self.pkg['meansurmentTime']
        logging.info(
            f"init package: {self.pkg},serial:{self.serial},timemeansure:{self.timemeansure}")
        super(PlotWindow, self).__init__(parent, **kwargs)
        self.device = None
        self.baudrate = None
        self.tenderness = None
        self._meansureTime = "meansurmentTime"
        self.currentDay = None
        self.mainPlot = None
        self.WindowFont = None
        self.GridFont = None
        self.df_tmp = None
        self.pickleSheet = None
        self.changeSecond, self.changeMain = True, True
        self.full = False
        self.zoom = None
        self.F_CPU = 16000000

        self.PlotCount = 1
        self.timeList, self.freqList, self.xdata, self.ydata = [], [], [], []
        self.prompt = TimePrompt(self)
        self.files = ConfigDropList()
        self.timer = QtCore.QTimer(self)
        self.title_file, self.path, self.openedfile,  self.openedPath = '', '', '', ''

        self.curentMeansureTime = None
        self.fileMeansureTime = None
        self.ierrors = Errors(self)
        self._config = {"Nxi": ["platforma:", "Baudrate:", "Czułość przetwornika"],
                        "Txi": [self.device, self.baudrate, self.tenderness]}
        self.setWindowTitle("Python 3.9.7")
        self.uiSet()

    def closeConnection(self):
        self.serial.endConnection()
    # NOTE przeniesiono

    def currentDataMeansure(self):  # generowanie aktualnej daty
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
        self.timeButtons.addWidget(self.addNewMeansureTime, 1, 0)
        self.timeButtons.addWidget(self.resetNewMeansureTime, 1, 1)
        self.timeButtons.addWidget(self.comboTimeMeansure, 2, 0, 1, 0)
        self.timeBox.setLayout(self.timeButtons)
        self.grid.addWidget(self.timeBox, 0, 0)
        self.grid.addWidget(self.startCatchData, 1, 0)
        self.grid.addWidget(self.analyzeFile, 2, 0)
        self.grid.addWidget(self.plotFile, 3, 0)
        self.grid.addWidget(self.convertToCsvButton, 4, 0)
        self.grid.addWidget(self.plotPointsInChar, 5, 0)
        self.grid.addWidget(self.chart, 0, 1, 13, 4)
        self.setCentralWidget(self.widget)
        logging.info(f'uiset: done')

    def showSecondWindow(self):  # wyświetlanie maxymalizowanego okna
        self.showMaximized()

    def buttonsConfig(self):
        self.comboTimeMeansure = ComboList(
            self, option=self.timemeansure["standard"], default=self.timemeansure["default"])

        addTime = partial(self.files.addItem, self, self.comboTimeMeansure,
                          self._meansureTime, "standard", 'Czas pomiaru', 'Wpisz nowy czas pomiaru, przykładowo 1 s /1 min /1 h')
        resetTime = partial(self.files.resetList,
                            self.comboTimeMeansure, self._meansureTime, "standard")

        self.addNewMeansureTime = QPushButton('Dodaj nowy czas pomiaru', self)
        self.resetNewMeansureTime = QPushButton(
            'Resetuj czasy poimiaru', self)
        self.addNewMeansureTime.clicked.connect(addTime)
        self.resetNewMeansureTime.clicked.connect(resetTime)
        self.startCatchData = QPushButton('Rozpocznij pobieranie danych')
        self.startCatchData.clicked.connect(self.startMeanurments)
        self.analyzeFile = QPushButton('Analizuj dane')
        self.analyzeFile.clicked.connect(self.openRawFile)
        self.plotFile = QPushButton('Wyświetl dane')
        self.plotFile.clicked.connect(self.showAnalyzedData)
        self.convertToCsvButton = QPushButton('Konwertuj plik do CSV')
        self.convertToCsvButton.clicked.connect(self.startConvertingToCsv)
        self.plotPointsInChar = QPushButton('Pokaż punkty wykresu')
        self.plotPointsInChar.clicked.connect(self.plotPointer)
        if self.serial.meansureButtonState:
            pass
        else:
            self.startCatchData.setEnabled(False)
            logging.warning(
                ' class get wrong params, capture data unavailable!')

    def showAnalyzedData(self):
        self.openAnalyzedFile()
        logging.info(f'Prepare to plot:')
        self.AnalyzedFileSignal.connect(self.analyzedPlot)

    def analyzedPlot(self):
        self.prompt.close()
        logging.debug(f'visualization: start ')
        # zmniejszenie zasobów pamięciu dzięki generatorowi
        self.pairsGenerator = (pair for pair in self.pairs)
        self.configChart()  # metoda konfigurująca dany wykres
        self.countPlot()  # metoda zliczająca ile jest aktualnie wyświetlonych wykresów
        self.update()
        logging.debug(f'visualization: timer start {self.timer} ')
        logging.debug(f'visualization: set coordinates from ')
        # self.timeList, self.freqList = [], []
        self.xdata, self.ydata = [], []

    def countPlot(self):  # metoda do dodawania nowych wartości do wykresu
        self.PlotCount += 1
        logging.debug(f"chart count: {self.PlotCount}")
        logging.debug(
            f'visualization: chart nr {self.PlotCount} ')

    def startMeanurments(self):  # pobieranie nowego zestawu danych z mikrokontrolera
        logging.debug(f'get data: start')
        self.startCatchData.setEnabled(False)
        self.startCatchData.setText('Pobieranie danych')
        self.currentDataMeansure()
        logging.debug(f'get data: set time')
        self.files.setDefaulfValue(
            name="meansurmentTime", position="default", element=self.comboTimeMeansure.default)

        if self.timemeansure["default"]:
            meansureThread = threading.Thread(
                target=self.serial.meansureRange, args=(self.comboTimeMeansure.default, self.curentMeansureTime,))  # dane muszą zostać pobrane z wykorzystaniem wątka, inaczej program przestanie odpowiadać
        else:
            meansureThread = threading.Thread(
                target=self.serial.meansureRange, args=(self.comboTimeMeansure.option, self.curentMeansureTime,))
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

    def popUpTime(self, timeDesc):
        logging.info(
            f' pop-up message about meansure time:{timeDesc}')
        self.prompt.message(
            msg=f'Czas pobierania danych: {timeDesc}. Proszę czekać.')
        if self.prompt.show():
            self.prompt.layout.removeWidget()

    def plotConfiguration(self):
        labels = {'color': 'w',
                  'font-size': f'{self.GridFont.pixelSize()}px'}

        self.plots = self.chart.addPlot(row=0, col=0,
                                        title=f"<b><p style=\"color: black\">{self.title_file}</p></b><")
        self.plotLine = self.plots.plot(
            [], pen=pg.mkPen('#FF4500', width=0.9), connected='pairs')
        self.plots.showGrid(x=True, y=True, alpha=0.5)
        self.plots.setLabel('left', 'Frequency',
                            units='Hz', **labels)
        self.plots.setLabel('bottom', 'Time', units='s', **labels)
        self.plots.getAxis("bottom").setTickFont(self.GridFont)
        self.plots.getAxis("bottom").setStyle(tickTextOffset=20)
        self.plots.getAxis("left").setTickFont(self.GridFont)
        self.plots.getAxis("left").setStyle(tickTextOffset=20)
        self.chart.nextRow()
        self.zoomedplot = self.chart.addPlot(row=1, col=0,
                                             title=f"<b><p style=\"color: black\">Zoomed</p></b><")
        self.zoomedLine = self.zoomedplot.plot(
            [], pen=pg.mkPen('#FF4500', width=0.9), connected='pairs')
        self.zoomedplot.showGrid(x=True, y=True, alpha=0.5)
        self.zoomedplot.setLabel('left', 'Frequency', units='Hz', **labels)
        self.zoomedplot.setLabel('bottom', 'Time', units='s', **labels)
        self.zoomedplot.getAxis("bottom").setTickFont(self.GridFont)
        self.zoomedplot.getAxis("bottom").setStyle(tickTextOffset=20)
        self.zoomedplot.getAxis("left").setTickFont(self.GridFont)
        self.zoomedplot.getAxis("left").setStyle(tickTextOffset=20)
        self.zoom = pg.LinearRegionItem([0, 5])
        self.updateZoom()
        self.zoom.setZValue(1000)
        self.zoom.sigRegionChanged.connect(self.updateZoom)
        self.plots.addItem(self.zoom)

    def updateZoom(self):
        self.zoomedplot.setXRange(*self.zoom.getRegion(), padding=0)

    def configChart(self):  # metoda do konfiguracji wyglądu wykresu
        logging.debug(
            f'visualization: configuration of new chart ')
        if self.PlotCount < 2:
            self.plotConfiguration()
        else:
            self.chart.removeItem(self.plots)
            self.chart.removeItem(self.zoomedplot)
            self.PlotCount = 1
            self.plotConfiguration()

    def update(self):
        logging.debug(f"{len(self.timeList)},{len(self.freqList)}")
        setDataThread = threading.Thread(
            target=self.setDataToLine, args=(self.timeList, self.freqList,), daemon=True)
        setDataThread.start()

    def setDataToLine(self, time, freq):
        self.plotLine.setData(time, freq)
        self.zoomedLine.setData(time, freq)
        self.plotFile.setEnabled(True)

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
        # note może być wartość 0, uwzględnij to
        logging.info(f'analyzeThread: start')
        logging.debug(f'analyze raw file: start ')
        t = 0
        i = 0
        zeros = 0
        calculated_dictionary = {'Nxi': [],
                                 'Txi': [],
                                 'fxi': [],
                                 'Xxi': [],
                                 't': []
                                 #  'Błąd kwantowania (Nx+1)': [],
                                 #  'Błąd bezwzględny': [],
                                 #  'Błąd względny δ': [],
                                 #  'Błąd względny δ%': [],
                                 }
        for nx in sheet:
            i += 1
            if nx == 0:
                zeros += 1
                pass
            else:
                Nxi = float(nx)
                Txi = Nxi*(1/self.F_CPU)
                fxi = 1/Txi
                Xxi = fxi/self.tenderness
                t += Txi
                # bwzg = round((Tx1-Txi), 8)
                # wzg = round((bwzg/Txi), 8)
                # Tx1 = (Nxi+1)*(1/self.F_CPU)
                # proc_wzg = wzg*100
                calculated_dictionary['Nxi'].append(Nxi)
                calculated_dictionary['Txi'].append(Txi)
                calculated_dictionary['fxi'].append(fxi)
                calculated_dictionary['Xxi'].append(Xxi)
                calculated_dictionary['t'].append(t)
                # calculated_dictionary['Błąd kwantowania (Nx+1)'].append(Tx1)
                # calculated_dictionary['Błąd bezwzględny'].append(bwzg)
                # calculated_dictionary['Błąd względny δ'].append(wzg)
                # calculated_dictionary['Błąd względny δ%'].append(proc_wzg)
        tmp_list = calculated_dictionary['Xxi']
        logging.info(f' count of zeros {zeros}')
        logging.info(
            f'max freq:{max(tmp_list)}, min: {min(tmp_list)}')
        logging.debug(f'analyze raw file: size {i} ')
        logging.debug(f'analyze raw file: end ')
        self.addToPickle(calculated_dictionary, True)
        self.RawFileSignal.emit()
        logging.info(f'analyzeThread: done')

    def createFolder(self):
        current_directory = os.getcwd()
        final_directory = os.path.join(current_directory, r'wyniki pomiarów')
        if not os.path.exists(final_directory):
            logging.debug(f'create new folder:{final_directory}')
            os.makedirs(final_directory)

    # dodawanie skoroszuty pickle do poprzedniego skoroszytu
    def addToPickle(self, df_data, flag):
        if flag:
            logging.debug(
                f'pickle file: append sheet to header {self.path}{self.title_file}.pbz2 ')
            tmp_df_data = pd.DataFrame(df_data)
            self.df_tmp = self.df_tmp.append(tmp_df_data, ignore_index=True)
            logging.debug(
                f'pickle file:  {self.df_tmp} ')
            f = bz2.BZ2File(Path(f'{self.path}{self.title_file}.pbz2'), 'wb')

            pickle.dump(self.df_tmp, f)
            f.close()
            self.df_tmp = None  # clear memory
        else:
            logging.debug(f'pickle file: hold headers {df_data} ')
            self.df_tmp = df_data

    # tworzenie pliku pickle z początkowym ustawieniem kolumn
    def createPickleSheet(self, flagFile):
        logging.debug(f'pickle file create: start ')
        if flagFile:
            title = self.curentMeansureTime
        else:
            title = self.fileMeansureTime
        config = {"Nxi": ["platforma:", "Baudrate:", "Czułość przetwornika"],
                  "Txi": [self.device, self.baudrate, self.tenderness]}
        headers = ["Nxi", "Txi", "fxi", "t", "Xxi"]
        self.title_file = f"pomiar z {title}"
        self.path = r'D:\\MeansurePerioid\\wyniki pomiarów\\'
        if not Path(f'{self.path}{self.title_file}.pbz2').is_file():
            sf = pd.DataFrame(config, columns=headers)
            self.addToPickle(sf, False)
            logging.debug(
                f'pickle file create: created {self.path}{self.title_file}.pbz2 ')
            return True
        else:
            logging.debug(
                f'pickle file created before:{self.path}{self.title_file}.pbz2 ')
            return False

    def openFile(self, filetype):
        filterList = []
        typeOfFiles = {
            'all': 'All (*)',
            'csvfile': 'CSV file (*.csv)',
            'csvFileA': 'Analyzed CSV file (pomiar*.csv)',
            'pickleFileRaw': 'Raw Pickle files (RAW*.pbz2)',
            'pickleFileA': 'Analyzed Pickle files (pomiar*.pbz2)',
            'pickleFile': 'Pickle files (*.pbz2)'
        }
        for types in filetype:
            if typeOfFiles.get(types):
                filterList.append(typeOfFiles[types])
        file = f'{QDir.currentPath()}/wyniki pomiarów'
        dialog = QFileDialog(self)
        dialog.setWindowTitle('File')
        dialog.setNameFilters(
            filterList)
        dialog.setDirectory(file)
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_() == QDialog.Accepted:
            self.openedfile = dialog.selectedFiles()
            logging.debug(f'file: {self.openedfile}')
        else:
            self.openedfile = None

    def openAnalyzedFile(self):
        logging.info(f'read existed file: start ')
        self.openFile(['pickleFileA', 'csvfile'])

        if self.openedfile:
            self.plotFile.setEnabled(False)
            logging.info(
                f'read existed file: selected file {self.openedfile[0]} ')
            self.openedPath = str(self.openedfile[0])
            self.title_file = self.openedPath
            logging.debug(
                f'analyze threading: set ')
            analyzeThreading = threading.Thread(
                target=self.readAnalyzedFile, args=(self.openedPath,))
            analyzeThreading.start()
            self.prompt.message(
                msg=f'Trwa wczytywanie zestawu danych z pliku {self.openedPath}. Proszę czekać!')
            if self.prompt.show():
                self.prompt.layout.removeWidget()
        else:
            pass

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

        # zippedDataPairs = zip(self.timeList, self.freqList)
        self.pairs = zip(self.timeList, self.freqList)
        logging.debug(f'read existed file: done ')
        # self.AnalyzedFileSignal.emit(zippedDataPairs)
        self.AnalyzedFileSignal.emit()
        # self.AnalyzedFileSignal.emit(self.timeList, self.freqList)
        logging.debug(
            f'analyze threading: done ')
        self.convertToCsvButton.setEnabled(True)

    def startConvertingToCsv(self):  # wątek do konversji pliku z pickle do csv

        self.convertToCsvButton.setEnabled(False)
        self.openFile(['pickleFileA', 'pickleFile'])
        self.convertToCsvButton.setText('Rozpoczęto konwersje do CSV')
        convertThread = threading.Thread(
            target=self.convertPickleToCsv).start()
        logging.debug(f'start thread: {convertThread} convert to CSV')

    def convertPickleToCsv(self):

        with bz2.BZ2File(str(self.openedfile[0]), 'rb') as pickleAnalyzedSheet:
            pickleSheet = pickle.load(pickleAnalyzedSheet)
        convertThread = threading.Thread(
            target=self.csvconplete, args=(pickleSheet,)).start()

    def csvconplete(self, pickleSheet):

        if len(pickleSheet):
            logging.debug('convert to CSV')
            df_csv = pd.DataFrame(pickleSheet)
            logging.debug(f'convert to CSV: \n {df_csv}')
            newTitleAndPath, _ = self.modifyFileName(str(self.openedfile[0]))
            logging.debug(f'convert to CSV path: {str(self.openedfile[0])}')
            logging.debug(f'convert to CSV new path: {newTitleAndPath}.csv')
            df_csv.to_csv(f'{newTitleAndPath}.csv')
            logging.debug(f'convert to CSV new path: done')
            # self.prompt.message(
            #     msg=f'Plik zapisano jako {newTitleAndPath}.csv.')
            self.convertToCsvButton.setText('Plik zamieniono na format CSV')
            # self.prompt.message(
            #     msg=f'Utworzono plik {newTitleAndPath}.csv')
            # if self.prompt.show():
            #     self.prompt.layout.removeWidget()
            pickleSheet = None  # clear memory
            self.convertToCsvButton.setEnabled(True)
            self.convertToCsvButton.setText('Konwertuj plik do CSV')
            # if self.prompt.exec():
            #     self.prompt.layout.removeWidget()

    def modifyFileName(self, filename):  # metoda do modyfikacji nowej nazwy pliku
        filenameLists = filename.split()
        timePartOfList = filenameLists[-1].split('.')
        logging.debug(
            f'parts of file title: file {filenameLists} {timePartOfList}')
        new_title = f'{filenameLists[-2]} {timePartOfList[0]}'
        titleForCsv = f'{" ".join([str(part) for part in filenameLists[:4]])} {timePartOfList[0]}'
        logging.debug(
            f'one {" ".join([str(part) for part in filenameLists[:4]])}')
        logging.debug(f'two {timePartOfList[0]}')
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
        sheet = list(data['Nxi'][7:])
        logging.debug(f' lowest data {min(sheet)}')
        logging.info(f'length of sheet {len(sheet)}')

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
            logging.warning(
                f'read raw file: cant read file, file exist')

            return False

    def openRawFile(self):   # metoda do wyszukania i wybrania pliku z poprzednimi pomiarami
        logging.info(f'select file')
        self.openFile(['pickleFileRaw'])

        self.analyzeFile.setEnabled(False)
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
                self.prompt.message(
                    msg=f'Trwa analizowanie pliku {self.openedPath}')
                self.analyzeFile.setText('Przetwarzanie danych')
                analyzeThread = threading.Thread(
                    target=self.analyzeDataFromFile, args=(data,))
                analyzeThread.start()
                self.RawFileSignal.connect(self.openButtonState)
                if self.prompt.exec():
                    self.prompt.layout.removeWidget()
        else:
            pass

    def openButtonState(self):
        self.analyzeFile.setText('Analizuj dane')
        self.analyzeFile.setEnabled(True)
