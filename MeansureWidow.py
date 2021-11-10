from PyQt5.QtWidgets import QMainWindow
from Liblarys import *
from PlottingAxes import Plot_Window


class MeansureWindow(QMainWindow):
    def __init__(self):
        super(MeansureWindow, self).__init__()
        self._setup()

    def _setup(self):
        self.setFixedSize(1280, 720)
        #frame = self.frameGeometry()
        #position = QtWidgets.QDesktopWidget().availableGeometry().center()
        # frame.moveCenter(position)
        # self.move(frame.topLeft())
        self.plot = Plot_Window(self)
        self.widget = QWidget()
        self.setCentralWidget(self.widget)
        self.label = QGridLayout()
        self.text = QLabel(
            "xddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddD")
        self.label.addWidget(self.plot,0,0)
        self.label.addWidget(self.text,1,0)
        self.widget.setLayout(self.label)


app = QApplication(sys.argv)
window = MeansureWindow()
window.show()
sys.exit(app.exec_())
