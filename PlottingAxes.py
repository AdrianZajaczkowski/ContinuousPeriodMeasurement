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
        self.ptr, self.iter = 0, 1
        self.plots = None
        self.test = []
        self.mainPlot = None
        self.new = False
        self.t = 0
        self.full = False
        self.errorFlag = False
        self.changeSecond, self.changeMain = True, True
        self.title_file, self.path, self.openedfile,  self.openedPath = '', '', '', ''
        self.currentDay = None
        self.timer = QtCore.QTimer()
        self.serial = SerialConnection()
        self.exit = QAction("Exit Application",
                            triggered=lambda: self.exit_app)
        self.curentMeansure = None
        super(Plot_Window, self).__init__(parent, **kwargs)
        self.ierrors = Errors(self)
        self._config = {"Ni": ["platforma:", "Baudrate:", "Czułość przetwornika"],
                        "Nx": [self.device, self.baudrate, self.tenderness]}
        self.setWindowTitle("Python 3.9.7")

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

    def currentDataMeansure(self):
        self.currentDay = datetime.now()
        self.curentMeansure = str(
            self.currentDay.strftime("%Y_%m_%d %H_%M_%S"))

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, '', 'Czy na pewno chcesz skonczyć pomiary?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
            self.serial.endConnection()
            print('Window closed')
        else:
            event.ignore()

    def uiSet(self):

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
        self.grid.addWidget(self.newPlot, 1, 0)
        self.grid.addWidget(self.openFile, 2, 0)
        self.grid.addWidget(self.pointMain, 3, 0)
        self.grid.addWidget(self.pointSecond, 4, 0)
        self.grid.addWidget(self.chart, 0, 1, 6, 1)

        self.setCentralWidget(self.widget)

    def showPlots(self):
        if not self.errorFlag:
            self.showMaximized()
        else:
            pass

    def buttonsConfig(self):
        self.startPlot = QPushButton('Start wykresu')
        self.startPlot.clicked.connect(self.startPlotting)
        self.newPlot = QPushButton('Nowy wykres')
        self.newPlot.clicked.connect(self.clearPlot)
        self.pointMain = QPushButton('Pokaż punkty głównego wykresu')
        self.pointMain.clicked.connect(self.pointersMain)
        self.pointSecond = QPushButton('Pokaż punkty dodatkowego wykresu')
        self.pointSecond.clicked.connect(self.pointerSecond)
        self.openFile = QPushButton('Otwórz plik')
        self.openFile.clicked.connect(self.openfile)

    def startPlotting(self):

        self.startPlot.setEnabled(False)
        self._connections()
        self.plotter()

    def clearPlot(self):
        self.mainPlot.removeItem(self.serialLine)
        self.mainPlot.clear()
        self.mainPlot.replot()
        self.plotter()

    def pointersMain(self):
        if self.changeMain:
            self.pointMain.setText("Ukryj punkty głównego wykresu")
            self.serialLine.setSymbol('o')
            self.changeMain = False
        else:
            self.pointMain.setText("Pokaż punkty głównego wykresu")
            self.serialLine.setSymbol(None)
            self.changeMain = True

    def pointerSecond(self):
        if self.changeSecond:
            self.pointSecond.setText("Ukryj punkty dodatkowego wykresu")
            self.secondLine.setSymbol('o')
            self.changeSecond = False
        else:
            self.pointSecond.setText("Pokaż punkty dodatkowego wykresu")
            self.secondLine.setSymbol(None)
            self.changeSecond = True

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
        self.createCsv(self._config)
        self.tdata, self.fdata = [0], [0]
        if not self.mainPlot:
            self.mainPlot = self.chart.addPlot(row=0, col=0,
                                               title="Ciągły pomiar okresu sygnału")
        else:
            pass
        self.serialLine = self.mainPlot.plot(pen='g')
        self.mainPlot.showGrid(x=True, y=True)
        self.mainPlot.setLabel('left', 'Frequency', units='Hz')
        self.mainPlot.setLabel('bottom', 'Time', units='s')
        self.serial.connection.write(b's')
        self.updateData()

    def updateData(self):
        self.timer.timeout.connect(self.plotSerial)
        self.timer.start(0)

    def testss(self):
        self.value = self.serial.connection.read(2)
        # self.value = self.connection.readline(16).strip()
        # print(self.value)
        unpacked_data = struct.unpack("<H", self.value)[0]
        # unpacked_data = int(self.value.decode('utf-8'))
        print(unpacked_data)

    def plotSerial(self):  # popraw plot, coś chrzani wykres
        try:
            Nx = self.serial.readValue()

            if Nx:
                Tx = Nx*(1/16000000)
                # print(tx)
                f = 1/Tx
                print(f)
                Nx1 = (Nx+1)*(1/16000000)
                wzg = Nx1-Tx
                bwzg = wzg/Tx
                self.t += Tx
                proc_bwzg = bwzg*100
                tmp = list((0, Nx, Tx, self.t, f, Nx1, wzg, bwzg, proc_bwzg))
                self.updateCsv(tmp)
                self.tdata.append(self.t)
                self.fdata.append(f)
                x = np.array(self.tdata, dtype='f')
                y = np.array(self.fdata, dtype='f')
                self.serialLine.setData(x, y)
        except Exception:
            self.close()

    def createCsv(self, config):
        self.currentDataMeansure()
        self.title_file = f"pomiar z {self.curentMeansure}.csv"
        self.path = r'D:\\MeansurePerioid\\wyniki pomiarów\\'
        if not Path(self.path+self.title_file).is_file():
            headers = ["Ni", "Nx", "Tx", "t", "f",
                       " Błąd kwantowania (Nx+1)", "Błąd bezwzględny", "Błąd względny δ", "Błąd względny δ%"]
            sf = pd.DataFrame(config, columns=headers)
            sf.to_csv(Path(self.path+self.title_file), encoding='utf-8-sig',
                      index=False, sep=';', header=headers,)

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
            self.plots = self.chart.addPlot(row=1, col=0,
                                            title=f"{self.openedPath}")
            self.secondLine = self.plots.plot(pen='g')
            self.plots.showGrid(x=True, y=True)
            self.plots.setLabel('left', 'Frequency', units='Hz')
            self.plots.setLabel('bottom', 'Time', units='s')
            x = data[0]
            y = data[1]
            self.secondLine.setData(x, y)
            self.iter += 1
        else:
            self.chart.removeItem(self.plots)
            self.full = False
            self.iter = 1
            self.secondPlot(data)

    def readFile(self, filename):
        columns = ["Ni", "Nx", "Tx", "t", "f",
                   " Blad kwantowania (Nx+1)", "Blad bezwzgledny", "Blad wzgledny δ", "Blad wzgledny δ%"]
        data = pd.read_csv(filename, sep=';',
                           encoding='utf-8-sig', skiprows=4, names=columns, header=None)
        print(data)
        t = list(data["t"])
        f = data["f"]
        sheet = list((t, f))
        return sheet

    def openfile(self):
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
            data = self.readFile(self.openedPath)
            self.secondPlot(data)


app = QApplication(sys.argv)

# plot = Plot_Window(None, device="Arduino Uno",
#                    baudrate="9600", tenderness="1")
plot = Plot_Window(None, device="Arduino Mega",
                   baudrate="115200", tenderness="1")
plot._connections()
plot.show()

# while True:
#     plot.testss()
sys.exit(app.exec_())
