# from PlottingAxes import *
from PyQt5.QtCore import QObject, pyqtSignal
from SerialConnection import *
from collections import deque


class Read(QObject):
    plot = pyqtSignal(int)
    csvdata = pyqtSignal(int)
    con = pyqtSignal()

    def __init__(self,  parent=None, **kwargs):
        self.deq = deque()
        self.obj = kwargs.pop('obj')
        self.storage = [1, 2, 3, 4, 5]
        self.i = 0
        super(Read, self).__init__(parent, **kwargs)
        self.plots = self.obj
        self.arduino = SerialConnection()

    def appendToDeq(self, param):
        self.deq.append(param)

    def popFromDeq(self):
        self.deq.pop()

    def test1(self):
        self.plot.connect(
            self.plots.plotses)
        # self.csvdata.connect(
        #     self.plots.calculations)

    def emitsSignals(self, param):

        # self.plot.emit("Arduino Mega", "38400")
        self.plot.emit(param)

    def test2(self):
        self.con.connect(self.plots.updateData)
        self.con.emit()

    def test4(self, x, y):
        print(x+2)

    def test3(self):
        print("x")

    def loops(self):
        i = 0
        while True:
            self.emitsSignals(i)
            i += 1
            if i >= 100:
                break

# a = Read()
# a.test1()

# app = QApplication(sys.argv)
# win = Read()
# win.test1()
# win.test2()
# # win.arduino.showDevices()
# # for i in range(100):
# #     win.appendToDeq(i+1)

# # win.emitsSignals(win.deq[4])
# # win.arduino.start()
# i = 0
# while True:
#     win.emitsSignals(i)
#     i += 1
#     if i >= 10000000:
        # break
# win.arduino.close()
