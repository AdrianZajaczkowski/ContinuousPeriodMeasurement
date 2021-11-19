
import numpy as np
import pyqtgraph as pg
from pyqtgraph.ptime import time
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QStackedWidget, QHBoxLayout, QVBoxLayout, QPushButton

from SerialConnection import *
from Liblarys import *


class Plot_Window(QMainWindow):
    def __init__(self, parent=None, **kwargs):
        self.device = kwargs.pop('device')
        self.baudrate = kwargs.pop('baudrate')
        print(self.baudrate)
        self.ptr = 0
        super(Plot_Window, self).__init__(parent, **kwargs)
        self.uiSet()
        self._connections()
        self.plotter()

    def _connections(self):
        self.serial = SerialConnection()
        self.serial.showDevices()
        self.serial.connect(self.device, self.baudrate)

    def uiSet(self):
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.widget = QWidget()
        self.grid = QGridLayout()
        self.saveData = QPushButton('aaaaaaaa')
        self.infoText = QLineEdit()
        self.chart = pg.PlotWidget()
        self.widget.setLayout(self.grid)
        self.grid.addWidget(self.saveData, 0, 0)
        self.grid.addWidget(self.chart, 0, 1, 3, 1)
        self.setCentralWidget(self.widget)

    def plotter(self):
        self.xdata, self.ydata = [0], [0]
        self.curve = self.chart.plot(pen='g', symbol='o')
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(0)

    def update(self):
        line = int(self.serial.connection.readline())
        #fx = 1/line
        self.xdata.append(line)
        # self.ydata.append(fx)
        x = np.array(self.xdata, dtype='i')
        #y = np.array(self.ydata, dtype='f')
        self.curve.setData(x)
        self.ptr = +1


'''
app = QApplication(sys.argv)
plots = PyQtConnection(device="Arduino", baudrate=500000)
plots.show()
app.exec_()
'''
