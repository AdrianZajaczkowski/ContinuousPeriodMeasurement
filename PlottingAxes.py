# class to plot data
from sqlite3 import Time
from serial.win32 import EV_CTS
from SerialConnection import *
from libraries import *
from ComboList import *
from ConfigFiles import *
from Errors import Errors
from TimePrompt import TimePrompt
from bufforReading import *

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


class Plot_Window(QMainWindow):
    serialSignal = pyqtSignal(str, str)
    popupSignal = pyqtSignal(object)

    def __init__(self, parent, **kwargs):
        self.pkg = kwargs.pop('pkg')
        self.serial = kwargs.pop('serial')
        self.timemeansure = self.pkg['meansurmentTime']
        super(Plot_Window, self).__init__(parent, **kwargs)
        self.device = None
        self.baudrate = None
        self.tenderness = None
        self.currentDay = None
        self.plots = None
        self.mainPlot = None
        self.WindowFont = None
        self.GridFont = None
        self.changeSecond, self.changeMain = True, True
        self.full = False
        self.F_CPU = 16000000
        self.PlotCount = 1
        self.prompt = TimePrompt(self)
        self.t, self.n = 0, 0
        self.files = ConfigFiles()
        self.title_file, self.path, self.openedfile,  self.openedPath = '', '', '', ''
        self.timer = QtCore.QTimer()
        self.exit = QAction("Exit Application",
                            triggered=lambda: self.exit_app)
        self.curentMeansure = None
        self.ierrors = Errors(self)
        self._config = {"Nxi": ["platforma:", "Baudrate:", "Czułość przetwornika"],
                        "Txi": [self.device, self.baudrate, self.tenderness]}
        self.setWindowTitle("Python 3.9.7")
        self.uiSet()

    def closeConnection(self):
        self.timer.stop()
        self.serial.endConnection()

    def currentDataMeansure(self):
        self.currentDay = datetime.now()
        self.curentMeansure = str(
            self.currentDay.strftime("%Y_%m_%d %H_%M_%S"))

    def uiSet(self):
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
        self.grid.addWidget(self.openFile, 1, 0)
        self.grid.addWidget(self.plotPointsInChar, 2, 0)
        self.grid.addWidget(self.chart, 0, 1, 13, 4)
        self.timeButtons.addWidget(self.setTimeMeansure, 0, 0)
        self.timeBox.setLayout(self.timeButtons)
        self.grid.addWidget(self.timeBox, 3, 0)
        self.setCentralWidget(self.widget)

    def showSecondWindow(self):
        self.showMaximized()

    def buttonsConfig(self):
        self.setTimeMeansure = ComboList(
            self, option=self.timemeansure["standard"], default=self.timemeansure["default"])

        self.startCatchData = QPushButton('Rozpocznij pobieranie danych')
        self.startCatchData.clicked.connect(self.startMeanurments)
        self.openFile = QPushButton('Otwórz plik i wyświetl dane')
        self.openFile.clicked.connect(self.openfile)
        self.plotPointsInChar = QPushButton('Pokaż punkty wykresu')
        self.plotPointsInChar.clicked.connect(self.plotPointer)

    def startMeanurments(self):

        self.currentDataMeansure()
        self.files.setDefaulfValue(
            name="meansurmentTime", position="default", element=self.setTimeMeansure.default)
        self.popupSignal.connect(self.serial.monit)
        self.serialSignal.connect(self.serial.meansureRange)
        self.popupSignal.emit(self.prompt)
        if self.timemeansure["default"]:
            self.serialSignal.emit(
                self.setTimeMeansure.default, self.curentMeansure)
            self.popUpTime(self.setTimeMeansure.default)
        else:
            self.serialSignal.emit(
                self.setTimeMeansure.option, self.curentMeansure)
            self.popUpTime(self.setTimeMeansure.option)

    def popUpTime(self, timeDesc):
        self.prompt.message(
            msg=f'Czas pobierania danych: {timeDesc}. Proszę czaekać.')
        if self.prompt.exec():
            self.startCatchData.enable(False)

    def showPlot(self, x, y):   # metoda do dodania kolejnego wykresu pod aktualnym pomiarem

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
            self.plotPointsInChar.setText("Ukryj punkty dodatkowego wykresu")
            self.plotLine.setSymbol('o')
            self.changeSecond = False
        else:
            self.plotPointsInChar.setText("Pokaż punkty dodatkowego wykresu")
            self.plotLine.setSymbol(None)
            self.changeSecond = True

    def analyzeDataFromFile(self, sheet):  # Metoda do wizualizacji danych
        tList = []
        frequencyList = []
        for i in range(len(sheet)):
            Nxi = int(sheet[i])
            Txi = Nxi*(1/self.F_CPU)
            Tx1 = (Nxi+1)*(1/self.F_CPU)
            fxi = 1/Txi
            Xxi = fxi/self.tenderness
            bwzg = round((Tx1-Txi), 8)
            wzg = round((bwzg/Txi), 8)
            self.t += Txi
            proc_wzg = wzg*100
            row = list((Nxi, Txi, Xxi, self.t, fxi,
                       Tx1, bwzg, wzg, proc_wzg))
            self.updateCsv(row)
            tList.append(self.t)
            frequencyList.append(Xxi)
        self.showPlot(tList, frequencyList)

    def createFolder(self):   # metoda do stworzenia folderu z pomiarami
        current_directory = os.getcwd()
        final_directory = os.path.join(current_directory, r'wyniki pomiarów')
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)

    def createCsv(self):    # metoda do stworzenia określonego pliku csv
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

    def readDataFromFile(self, filename):  # metoda do odczytu danych do wizualizacji
        columns = ["Timestamp", "Ni"]
        data = pd.read_csv(filename, sep=';',
                           encoding='utf-8-sig', names=columns, header=None)

        filenameList = filename.split()
        timePartOfList = filenameList[-1].split('.')
        new_title = f'{filenameList[-2]} {timePartOfList[0]}'
        self.curentMeansure = new_title
        sheet = list(data["Ni"][7:])
        self.device = data['Ni'][1]
        self.baudrate = data['Ni'][3]
        self.tenderness = float(data['Ni'][4])
        self.createCsv()
        return sheet

    def openfile(self):   # metoda do wyszukania i wybrania pliku z poprzednimi pomiarami
        file = QDir.currentPath()
        dialog = QFileDialog(self)
        dialog.setWindowTitle('File')
        dialog.setNameFilters(
            ['All files (*)', 'CSV files (*.csv)'])
        dialog.setDirectory(file)
        dialog.setFileMode(QFileDialog.ExistingFile)

        if dialog.exec_() == QDialog.Accepted:
            self.openedfile = dialog.selectedFiles()
        if self.openedfile:
            self.openedPath = str(self.openedfile[0])
            data = self.readDataFromFile(self.openedPath)
            self.analyzeDataFromFile(data)
