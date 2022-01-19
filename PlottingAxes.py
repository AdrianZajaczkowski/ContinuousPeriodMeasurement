# class to plot data
from serial.win32 import EV_CTS
from SerialConnection import *
from Liblarys import *
from ComboList import *
from Errors import Errors

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


class Plot_Window(QMainWindow):
    def __init__(self, parent, **kwargs):
        self.device = kwargs.pop('device')
        self.baudrate = kwargs.pop('baudrate')
        self.tenderness = kwargs.pop('tenderness')
        self.Nnext, self.Nprev = 0, 0
        self.overflow = 65535
        self.F_CPU = 16000000
        self.plots = None
        self.test = []
        self.mainPlot = None
        self.iter = 1
        self.t = 0
        self.WindowFont = None
        self.GridFont = None
        self.full = False
        self.errorFlag, self.quitflag = False, False
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
        self._config = {"Nx": ["platforma:", "Baudrate:", "Czułość przetwornika"],
                        "Tx": [self.device, self.baudrate, self.tenderness]}
        self.setWindowTitle("Python 3.9.7")

        try:

            if isinstance(self.tenderness, str):
                self.tenderness = float(self.tenderness)
                self.uiSet()

            elif isinstance(self.tenderness, list):
                raise ValueError

            elif isinstance(self.device, str) and isinstance(self.baudrate, str):
                pass
                # raise Exception

        except (TypeError, ValueError):
            self.errorFlag = True
            msg = 'Wybierz poprawną wartość czułości.'
            self.ierrors.message('Błąd danych', msg)
            if self.ierrors.exec():
                self.close()
                self.parent().show()
        except Exception:
            self.errorFlag = True
            msg = 'Wybierz poprawny mikrokontroler i baudrate.'
            self.ierrors.message('Błąd danych', msg)
            if self.ierrors.exec():
                self.close()
                self.parent().show()

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

    def currentDataMeansure(self):
        self.currentDay = datetime.now()
        self.curentMeansure = str(
            self.currentDay.strftime("%Y_%m_%d %H_%M_%S"))

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, 'Quit', 'Czy na pewno chcesz skonczyć pomiary?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes and self.quitflag == False:
            event.accept()
            self.close()
            self.closeConnection()

            print('Window closed')
            self.quitflag = True
        else:
            event.ignore()

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
        self.chart = pg.GraphicsLayoutWidget(show=True)
        self.chart.setBackground("w")

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
        self.startPlot = QPushButton('Rozpocznij rysowanie wykresu')
        self.startPlot.clicked.connect(self.startPlotting)
        self.newPlot = QPushButton('Nowy wykres')
        self.newPlot.clicked.connect(self.clearPlot)
        self.pointMain = QPushButton('Pokaż punkty głównego wykresu')
        self.pointMain.clicked.connect(self.pointersMain)
        self.pointSecond = QPushButton('Pokaż punkty dodatkowego wykresu')
        self.pointSecond.clicked.connect(self.pointerSecond)
        self.openFile = QPushButton('Otwórz plik')
        self.openFile.clicked.connect(self.openfile)

    def plotter(self):    # metoda do dormatowania wykresu
        self.createCsv(self._config)
        self.tdata, self.fdata = [None], [None]
        labels = {'color': 'w', 'font-size': f'{self.GridFont.pixelSize()}px'}
        if not self.mainPlot:
            self.mainPlot = self.chart.addPlot(row=0, col=0,
                                               title="<b><p style=\"font-size:17px\">Ciągły pomiar okresu sygnału</p></b>", **labels)
        else:
            pass
        self.serialLine = self.mainPlot.plot(pen=pg.mkPen('r', width=1))
        self.mainPlot.showGrid(x=True, y=True, alpha=1)
        self.mainPlot.setLabel('left', 'Frequency',
                               units='Hz', **labels)
        self.mainPlot.setLabel(
            'bottom', 'Time', units="s", **labels)
        self.mainPlot.getAxis("bottom").setTickFont(self.WindowFont)
        self.mainPlot.getAxis("bottom").setStyle(tickTextOffset=20)
        self.mainPlot.getAxis("left").setTickFont(self.WindowFont)
        self.mainPlot.getAxis("left").setStyle(tickTextOffset=20)
        self.updateData()

    def startPlotting(self):    # metoda do inicjalizowania wykresu głównego

        self.startPlot.setEnabled(False)
        self._connections()
        self.serial.connection.write(b's')
        self.plotter()

    def clearPlot(self):     # metoda do czyszczenia dodawanych wykresów
        self.t = 0
        self.mainPlot.removeItem(self.serialLine)
        self.mainPlot.clear()
        self.mainPlot.replot()
        self.plotter()

    def secondPlot(self, data):   # metoda do dodania kolejnego wykresu pod aktualnym pomiarem

        if self.iter == 2:
            self.full = True
        if not self.full:
            self.plots = self.chart.addPlot(row=1, col=0,
                                            title=f"<b><p style=\"color: black\">{self.openedPath}</p></b><")
            self.secondLine = self.plots.plot(pen='g')
            self.plots.showGrid(x=True, y=True, alpha=1)
            labels = {'color': 'g',
                      'font-size': f'{self.GridFont.pixelSize()}px'}
            self.plots.setLabel('left', 'Frequency',
                                units='Hz', **labels)
            self.plots.setLabel('bottom', 'Time', units='s', **labels)
            self.plots.getAxis("bottom").setTickFont(self.GridFont)
            self.plots.getAxis("bottom").setStyle(tickTextOffset=20)
            self.plots.getAxis("left").setTickFont(self.GridFont)
            self.plots.getAxis("left").setStyle(tickTextOffset=20)
            x = data[0]
            y = data[1]
            self.secondLine.setData(x, y)
            self.iter += 1
        else:
            self.chart.removeItem(self.plots)
            self.full = False
            self.iter = 1
            self.secondPlot(data)

    def pointersMain(self):   # metody do wyświetlania punktorów
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

    def updateData(self):       # metoda do ciągłego aktualizowania wykresu
        self.timer.timeout.connect(self.plotSerial)
        self.timer.start(0)

    def plotSerial(self):  # Metoda do wizualizacji danych

        Nx = self.serial.readValue()
        if Nx is None:
            # print("dane przekłamane")
            return
        else:
            print(Nx)

            if Nx:
                Tx = Nx*(1/self.F_CPU)
                f = 1/Tx
                Tx1 = (Nx+1)*(1/self.F_CPU)
                Xxi = f/self.tenderness
                wzg = abs(Tx1-Tx)
                bwzg = wzg/Tx
                self.t += Tx
                proc_bwzg = bwzg*100
                tmp = list(( Nx, Tx, Xxi, self.t, f,
                           Tx1, wzg, bwzg, proc_bwzg))
                self.updateCsv(tmp)
                self.tdata.append(self.t)
                self.fdata.append(Xxi)
                x = np.array(self.tdata, dtype='f')
                y = np.array(self.fdata, dtype='f')
                self.serialLine.setData(x, y)

    def createFolder(self):   # metoda do stworzenia folderu z pomiarami
        current_directory = os.getcwd()
        final_directory = os.path.join(current_directory, r'wyniki pomiarów')
        if not os.path.exists(final_directory):
            os.makedirs(final_directory)

    def createCsv(self, config):    # metoda do stworzenia określonego pliku csv
        self.currentDataMeansure()
        self.title_file = f"pomiar z {self.curentMeansure}.csv"
        self.path = r'D:\\MeansurePerioid\\wyniki pomiarów\\'
        if not Path(self.path+self.title_file).is_file():
            headers = ["Nx", "Tx", "Xxi", "t", "f",
                       " Błąd kwantowania (Nx+1)", "Błąd bezwzględny", "Błąd względny δ", "Błąd względny δ%"]
            sf = pd.DataFrame(config, columns=headers)
            sf.to_csv(Path(self.path+self.title_file), encoding='utf-8-sig',
                      index=False, sep=';', header=headers,)

    def updateCsv(self, nx):     # metoda do aktualizowania pliku csv
        row = nx
        with open(f'{self.path+self.title_file}', 'a+', newline='') as file:
            writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_NONE)
            writer.writerow(row)
            file.close()

    def readFile(self, filename):  # metoda do odczytu danych do wizualizacji
        columns = ["Nx", "Tx", "Xxi", "t", "f",
                   " Blad kwantowania (Nx+1)", "Blad bezwzgledny", "Blad wzgledny δ", "Blad wzgledny δ%"]
        data = pd.read_csv(filename, sep=';',
                           encoding='utf-8-sig', skiprows=4, names=columns, header=None)
        print(data)
        t = list(data["t"])
        f = data["Xxi"]
        sheet = list((t, f))
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
            data = self.readFile(self.openedPath)
            self.secondPlot(data)


# app = QApplication(sys.argv)

# # plot = Plot_Window(None, device="Arduino Uno",
# #                    baudrate="9600", tenderness="1")
# plot = Plot_Window(None, device="Arduino Mega",
#                    baudrate="115200", tenderness="1")
# plot._connections()
# plot.show()

# # while True:
# #     plot.testss()
# sys.exit(app.exec_())
