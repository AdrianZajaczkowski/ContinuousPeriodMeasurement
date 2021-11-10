from Liblarys import *
from ConfigFiles import *
from ComboList import *
from Monit import *
from PlottingAxes import *


class WelcomeWindow(QWidget):
    def __init__(self, parent=None):
        self._name = "devices"
        self.platform = ''
        super(WelcomeWindow, self).__init__(parent)
        self.setWindowTitle("Python 3.9.7")
        self._configLayout()

    def _configLayout(self):
        self.setFixedSize(600, 400)
        frame = self.frameGeometry()
        position = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(position)
        self.move(frame.topLeft())

        self.pkg = ConfigFiles.showData(self)
        self.module = self.pkg[self._name]

        self.descr = self._configText(text=self.pkg["text"]['Start'])
        self.author = self._configText(text=self.pkg["text"]['Autor'])
        self.combo = ComboList(self, module=self.module)

        self.addButton = QPushButton('Dodaj nową platformę', self)
        self.resetButton = QPushButton('Reset do domyślnych platform', self)
        self.goButton = QPushButton('Zacznij pomiary', self)
        self.addButton.clicked.connect(self.addModule)
        self.resetButton.clicked.connect(self.resetModule)
        self.goButton.clicked.connect(self.jump)

        self.label = QGridLayout()
        self.label.addWidget(self.descr, 0, 0, 2, 3)
        self.label.addWidget(self.author, 2, 1)
        self.label.addWidget(self.addButton, 3, 0)
        self.label.addWidget(self.combo, 3, 1,)
        self.label.addWidget(self.resetButton, 4, 0)
        self.label.addWidget(self.goButton, 3, 2)

        self.setLayout(self.label)

    def addModule(self):
        name = Monit(self)
        if name.exec():
            gadget = name.inputmsg.text()
            ConfigFiles.change(self, position=self._name, param=gadget)
            self.combo.update(gadget)
        else:
            pass

    def resetModule(self):
        ConfigFiles.defaultModule(self)
        self._new = ConfigFiles.showData(self)
        self.combo.clear()
        self.combo.update(self._new[self._name])

    def jump(self):
        self.hide()
        plotWindow = Plot_Window(
            device=self.combo.device, baudrate='115200')
        plotWindow.fig.show()

    def _configText(self, text):
        self.centralText = QLabel(
            f"{text[0]}")
        self.centralText.setWordWrap(True)
        self.centralText.setFont(QFont('Times', text[1]))
        self.centralText.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        return self.centralText
