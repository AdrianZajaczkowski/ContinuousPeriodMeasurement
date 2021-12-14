from serial.win32 import EV_CTS
from SerialConnection import *
from Liblarys import *
from ComboList import *
from Errors import Errors


class Plot_Window(QMainWindow):
    def __init__(self, parent, **kwargs):
        self.device = kwargs.pop('device')
        self.baudrate = kwargs.pop('baudrate')
        self.tenderness = kwargs.pop('tenderness')
        self.ptr, self.iter = 0, 0
        self.plots = [None, None, None]
        self.test = []
        self.plot = None
        self.full = False
        self.errorFlag = False
        self.title_file, self.path, self.openedfile,  self.openedPath = '', '', '', ''
        self.currentDay = datetime.now()
        self.timer = QtCore.QTimer()
        self.serial = SerialConnection()
        self.curentMeansure = str(
            self.currentDay.strftime("%Y_%m_%d %H_%M_%S"))
        super(Plot_Window, self).__init__(parent, **kwargs)
        self.ierrors = Errors(self)
        self._config = {"Tx": ["platforma:", "Baudrate:", "Czułość przetwornika"],
                        "fx": [self.device, self.baudrate, 1]}

        try:
            if isinstance(self.tenderness, str):
                self.tenderness = int(self.tenderness)
                self.uiSet()
            elif isinstance(self.tenderness, list):
                raise TypeError
            else:
                raise ValueError
        except (TypeError, ValueError):
            self.errorFlag = True
            msg = 'Wybierz poprawną wartość czułości.'
            self.ierrors.message('Błąd danych', msg)
            if self.ierrors.exec():
                self.close()
                self.parent().show()

    def uiSet(self):
        self.createCsv(self._config)
        self.setMinimumSize(800, 600)
        self.setGeometry(0, 0, 1920, 1080)
        frame = self.frameGeometry()
        self.move(frame.topLeft())
        self.buttonsConfig()

        self.widget = QWidget()
        self.grid = QGridLayout()
        self.chart = pg.GraphicsLayoutWidget(show=True)
        self.widget.setLayout(self.grid)
        self.grid.addWidget(self.startPlot, 0, 0)
        self.grid.addWidget(self.backToMenu, 1, 0)
        self.grid.addWidget(self.openFile, 2, 0)
        self.grid.addWidget(self.chart, 0, 1, 4, 1)

        self.setCentralWidget(self.widget)

    def showPlots(self):
        if not self.errorFlag:
            self.showMaximized()
        else:
            pass

    def buttonsConfig(self):
        self.startPlot = QPushButton('Start wykresu')
        self.startPlot.clicked.connect(self.startPlotting)
        self.backToMenu = QPushButton('Nowy wykres')
        self.backToMenu.clicked.connect(self.clearPlot)
        self.openFile = QPushButton('Otwórz plik')
        self.openFile.clicked.connect(self.openfile)

    def startPlotting(self):
        self._connections()
        self.plotter()

    def clearPlot(self):
        self.plot.removeItem(self.serialLine)
        self.plot.clear()
        self.plotter()

    def _connections(self):
        try:
            self.serial.showDevices()
            self.serial.connect(self.device, self.baudrate)
        except Exception:
            self.close()
            self.parent().show()
            self.serial.endConnection()

    def closeConnection(self):
        self.timer.stop()
        self.serial.endConnection()

    def plotter(self):
        self.txdata, self.fxdata, self.xidata = [0], [0], [0]
        if not self.plot:
            self.plot = self.chart.addPlot(
                title="Ciągły pomiar okresu sygnału")
        else:
            pass
        self.serialLine = self.plot.plot(pen='g', symbol='o')
        self.plot.showGrid(x=True, y=True)
        self.timer.timeout.connect(self.updateSerial)
        self.timer.start(0.00) # albo wywoływanie wykresu

    def testss(self):
        tx = self.serial.readValue()
        if tx is not None:
            print(tx)

    def updateSerial(self):  # popraw plot, coś chrzani wykres
        tx = self.serial.readValue()
        if tx:
            fx = 1/tx
            print(tx)
            xi = fx/self.tenderness
            tmp = list((tx, fx, xi))
            self.updateCsv(tmp)
            self.txdata.append(tx)
            self.fxdata.append(fx)
            self.xidata.append(xi)
            x = np.array(self.txdata, dtype='f')
            #y = np.array(self.fxdata, dtype='f')
            self.serialLine.setData(x)
            self.ptr = +1

    def createCsv(self, config):
        self.title_file = f"pomiar z {self.curentMeansure}.csv"
        self.path = r'D:\\MeansurePerioid\\wyniki pomiarów\\'
        if not Path(self.path+self.title_file).is_file():
            headers = ["Tx", "fx", "xi"]
            sf = pd.DataFrame(config, columns=headers)
            sf.to_csv(Path(self.path+self.title_file),
                      index=False, sep=';', header=headers)

    def updateCsv(self, nx):
        row = nx
        with open(f'{self.path+self.title_file}', 'a+', newline='') as file:
            writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_NONE)
            writer.writerow(row)
            file.close()

    def secondPlot(self, data):
        if self.iter == 2:
            self.full = True
        if not self.full:
            self.chart.nextRow()
            self.plots[self.iter] = self.chart.addPlot(
                title=f"{self.openedPath}")
            self.plots[self.iter].showGrid(x=True, y=True)
            self.line = self.plots[self.iter].plot(pen='g', symbol='o')
            x = data[0]
            y = data[1]
            self.line.setData(x, y)
            self.iter += 1
        else:
            self.plots[0].removeItem(self.line)
            self.plot[0].clear()
            self.line = self.plots[0].plot(pen='g', symbol='o')
            x = np.cos(np.linspace(0, 2*np.pi, 1000))
            y = np.sin(np.linspace(0, 4*np.pi, 1000))
            self.line.setData(x, y)

    def readFile(self, filename):
        x, y = [], []
        columns = ["Tx", "fx", "xi"]
        data = pd.read_csv(filename, sep=';',
                           encoding='UTF-8', skiprows=5,  names=columns, header=None)
        tx = list(data["Tx"])
        xi = data["fx"]
        sheet = list((tx, xi))
        return sheet

    def openfile(self):
        file = QDir.currentPath()
        dialog = QFileDialog(self)
        dialog.setWindowTitle('File')
        dialog.setNameFilters(
            ['All files (*)', 'CSV files (*.csv)', 'Excel files (*.xls)'])
        dialog.setDirectory(file)
        dialog.setFileMode(QFileDialog.ExistingFile)

        if dialog.exec_() == QDialog.Accepted:
            self.openedfile = dialog.selectedFiles()
        if self.openedfile:
            self.openedPath = str(self.openedfile[0])
            data = self.readFile(self.openedPath)
            self.secondPlot(data)


app = QApplication(sys.argv)

plot = Plot_Window(None, device="Arduino", baudrate="115200", tenderness="1")
plot._connections()
# plot.show()
while True:
    plot.testss()
sys.exit(app.exec_())
