import sys
import threading
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from SerialConnection import *


class Wykres(QtGui.QMainWindow):
    plot = QtCore.pyqtSignal(float, float)
    csvsignal = QtCore.pyqtSignal(float, float)

    def __init__(self,  parent=None, **kwargs):
        self.dataBuffer1 = kwargs.pop("data_buffer1")
        self.bufferLength = kwargs.pop("buffer_size")
        self.graphTitle = kwargs.pop("graph_title")
        self.dataBuffer2 = kwargs.pop("data_buffer2")
        super(Wykres, self).__init__(parent, **kwargs)
        #### Create Gui Elements ###########
        self.F_CPU = 16000000
        self.tenderness = 1
        self.t = 0
        self.mainbox = QtGui.QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtGui.QVBoxLayout())

        self.canvas = pg.GraphicsLayoutWidget()
        self.mainbox.layout().addWidget(self.canvas)

        self.label = QtGui.QLabel()
        self.mainbox.layout().addWidget(self.label)

        self.view = self.canvas.addViewBox()
        self.view.setAspectLocked(True)
        self.view.setRange(QtCore.QRectF(0, 0, 100, 100))

        self.numDstreams = 1

        self.otherplot = self.canvas.addPlot(
            row=0, col=0, title=self.graphTitle)  # , repeat line for more

        self.h2 = self.otherplot.plot(pen='r')

        self.plot.connect(self.update_plot)
        # self.csvsignal.connect(self.restof)

    def update_plot(self, data1, data2):  # dodawanie danych do wykresu
        self.dataBuffer1.append(data1)
        self.dataBuffer2.append(data2)
        self.xdata = np.array(self.dataBuffer1, dtype='f')
        self.ydata = np.array(self.dataBuffer2, dtype='f')
        self.h2.setData(self.xdata, self.ydata)

    def calculations(self, Nxi):  # obliczenia niezbędne do wykreślenia przebiegu
        Txi = Nxi*(1/self.F_CPU)
        fxi = 1/Txi
        Tx1 = (Nxi+1)*(1/self.F_CPU)
        Xxi = fxi/self.tenderness
        self.t += Txi
        self.plot.emit(self.t, Xxi)  # wysyłanie danych do metody update_plot()
        # self.csvsignal.emit(self.t, Xxi)

    def restof(self, Tx1, Txi):  # reszta obliczeń
        print("a")
        bwzg = round((Tx1-Txi), 8)
        wzg = round((bwzg/Txi), 8)
        proc_wzg = wzg*100
        print(bwzg)


def CreateGraph(graph_title):  # metoda do tworzenia obiektu klasy wyświetlającej
    thisapp1 = Wykres(graph_title=graph_title, data_buffer1=[],
                      data_buffer2=[], buffer_size=0)
    thisapp1.show()
    return thisapp1


class Helper(QtCore.QObject):  # funkcja do przechowywania obiektów sygnału
    bufferChanged = QtCore.pyqtSignal(int, int)
    calculations = QtCore.pyqtSignal(int)


# buffor odbierający dane i od razu wysyłające do calculations()
def generate_buffer(helper):
    while 1:
        data = round(ardu.readValue())

        # test_buffer1.append(data)
        # helper.bufferChanged.emit(test_buffer1, test_buffer1)
        helper.calculations.emit(data)
        # QtCore.QThread.msleep(1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ardu = SerialConnection()
    ardu.showDevices()
    ardu.connect(device="Arduino Mega", baudrate="38400")
    ardu.start()
    graph = CreateGraph("Activity Score")
    helper = Helper()
    threading.Thread(target=generate_buffer, args=(
        helper, ), daemon=True).start()
    helper.calculations.connect(graph.calculations)
    # helper.bufferChanged.connect(graph.update_plot)

    if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):
        sys.exit(app.exec_())
