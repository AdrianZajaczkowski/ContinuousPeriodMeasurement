from SerialConnection import *
from Liblarys import *
from ComboList import *
from Errors import Errors
import os


class Plot_Window(QMainWindow):
    def __init__(self, parent, **kwargs):
        self.device = kwargs.pop('device')
        self.baudrate = kwargs.pop('baudrate')
        self.ptr = 0
        self.nx = 0
        self.nx1 = 0
        self.currentDay = datetime.now()
        self.timer = QtCore.QTimer()
        self.curentMeansure = str(
            self.currentDay.strftime("%Y_%m_%d %H_%M_%S"))
        self.title_file, self.path = '', ''
        super(Plot_Window, self).__init__(parent, **kwargs)

        self.ierrors = Errors(self)
        self._config = {"Tx": ["platforma:", "Baudrate:", "Czułość przetwornika"],
                        "fx": [self.device, self.baudrate, 1]}
        self.createCsv(self._config)
        self.uiSet()

    def startPlotting(self):
        self._connections()
        self.plotter()

    def clearPlot(self):
        self.chart.clear()
        self.plotter()

    def _connections(self):
        try:
            self.serial = SerialConnection()
            self.serial.showDevices()
            self.serial.connect(self.device, self.baudrate)
        except Exception as ex:
            msg = "\n Sprawdz wybraną płytkę lub wartość baundrate"
            self.ierrors.message('Błąd', msg)
            if self.ierrors.exec():
                self.close()
                self.parent().show()
                self.ierrors.close()
                self.closeConnection()

    def closeConnection(self):
        self.timer.stop()
        self.serial.endConnection()

    def uiSet(self):
        self.setFixedSize(1000, 800)
        frame = self.frameGeometry()
        position = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(position)
        self.move(frame.topLeft())
        self.buttonsConfig()
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.widget = QWidget()
        self.grid = QGridLayout()
        self.chart = pg.PlotWidget()
        self.widget.setLayout(self.grid)
        self.grid.addWidget(self.startPlot, 0, 0)
        self.grid.addWidget(self.backToMenu, 1, 0)
        self.grid.addWidget(self.chart, 0, 1, 3, 1)
        self.setCentralWidget(self.widget)

    def buttonsConfig(self):
        self.startPlot = QPushButton('Start wykresu')
        self.startPlot.clicked.connect(self.startPlotting)
        self.backToMenu = QPushButton('Nowy wykres')
        self.backToMenu.clicked.connect(self.clearPlot)
        self.infoText = QLineEdit()

    def plotter(self):
        self.xdata, self.ydata = [0], [0]
        self.curve = self.chart.plot(pen='g', symbol='o')
        self.timer.timeout.connect(self.update)
        self.timer.start(0)

    def update(self):
        try:
            nx = self.serial.readValue()
            tmp = list((nx, nx, nx))
            self.updateCsv(tmp)
            # fx = 1/nx
            self.xdata.append(nx)
            # self.ydata.append(fx)
            x = np.array(self.xdata, dtype='i')
            y = np.array(self.ydata, dtype='f')
            self.curve.setData(x)
            self.ptr = +1
        except Exception as ex:
            msg = "\n Sprawdz wybraną płytkę lub wartość baundrate"
            self.ierrors.message('Błąd', msg)
            if self.ierrors.exec():
                self.close()
                self.parent().show()
                self.ierrors.close()
                self.closeConnection()
            else:
                pass

    def createCsv(self, config):
        self.title_file = f"pomiar z {self.curentMeansure}.csv"
        self.path = r'D:\\MeansurePerioid\\wyniki pomiarów\\'
        if not Path(self.path+self.title_file).is_file():
            sf = pd.DataFrame(config)
            df = pd.DataFrame({'Tx': ['Tx'],
                               'fx': ['fx'],
                               'xi': ['xi'], })
            frame = pd.concat([sf, df])
            frame.to_csv(Path(self.path+self.title_file),
                         index=False, header=None)
        else:
            print("xd")

    def updateCsv(self, nx):
        row = nx
        with open(f'{self.path+self.title_file}', 'a+', newline='') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_NONE)
            writer.writerow(row)
            file.close()
