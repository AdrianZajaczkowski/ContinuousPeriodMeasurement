from SerialConnection import*
from Liblarys import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec
import numpy as np
from matplotlib.figure import Figure
matplotlib.use('Qt5Agg')


class Plot_Window(FigureCanvas):

    def __init__(self, **kwargs):
        self.device = kwargs.pop('device')
        self.baudrate = kwargs.pop('baudrate')
        self.fig = plt.figure(figsize=(6.4, 4.8), dpi=100)
        spec = gridspec.GridSpec(ncols=2, nrows=2, figure=self.fig)
        self.axes = self.fig.add_subplot(spec[0, :])
        self.setgrid()
        self.serial = SerialConnection()
        self.serial.showDevices()
        self.serial.connect(self.device, self.baudrate)
        self.xdata, self.ydata = [], []

        super(Plot_Window, self).__init__()
        self.animation()
        # self._setupUI()

    def _annotation(self, data):
        x = int(data[0])
        y = int(data[2])
        self.fig.text(x, y, f"{x}:{y}", transform=self.axes.transData)

    def setgrid(self):
        self.axes.grid(color='blue', which='both',
                       linestyle=':', linewidth=0.5)

    def updatePlot(self, i, x, y):
        self.data = self.serial.readValue()
        self._annotation(self.data)
        x.append(int(self.data[0]))
        y.append(self.data[2])
        x, y = x[-20:], y[-20:]
        self.axes.clear()
        self.setgrid()
        self.axes.plot(x, y)

    def animation(self):
        self.ani = animation.FuncAnimation(
            self.fig, self.updatePlot, fargs=(self.xdata, self.ydata), interval=1)
        plt.autoscale()

    def _setupUI(self):
        pass
