from Liblarys import *
from ConfigFiles import *
from ComboList import *
from Monit import *
from PlottingAxes import *


class WelcomeWindow(QWidget):
    def __init__(self, parent=None):
        self._devices = "devices"
        self._baudrate = "baudrate"
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
        self.dev = self.pkg[self._devices]
        self.baud = self.pkg[self._baudrate]

        self.descr = self._configText(text=self.pkg["text"]['Start'])
        self.author = self._configText(text=self.pkg["text"]['Autor'],)
        self.comboDevices = ComboList(self, option=self.dev)
        self.comboBaudrate = ComboList(self, option=self.baud)

        self.addButton = QPushButton('Dodaj nową platformę', self)
        self.resetButton = QPushButton('Reset do domyślnych platform', self)
        self.goButton = QPushButton('Zacznij pomiary', self)
        self.textBaudrate = QLabel(
            "Baudrate")
        self.textDevice = QLabel("Platforma")
        self.textBaudrate.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.textDevice.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.textBaudrate.resize(20, 5)
        self.addButton.clicked.connect(self.addModule)
        self.resetButton.clicked.connect(self.resetModule)
        self.goButton.clicked.connect(self.jump)

        self.deviceBox = QGroupBox("Platforma")
        self.baundrateBox = QGroupBox("Baundrate")
        self.specify = QGridLayout()
        self.deviceLabel = QGridLayout()
        self.baundLabel = QGridLayout()
        self.specify.addWidget(self.descr, 0, 0, 2, 3)
        self.specify.addWidget(self.author, 2, 0, 1, 0)
        self.deviceLabel.addWidget(self.addButton, 1, 0)
        self.deviceLabel.addWidget(self.resetButton, 1, 1)
        self.deviceLabel.addWidget(self.comboDevices, 2, 0, 1, 0)
        self.deviceLabel.addWidget(self.goButton, 1, 2)
        self.baundLabel .addWidget(self.comboBaudrate, 1, 0, 1, 0)
        self.deviceBox.setLayout(self.deviceLabel)
        self.baundrateBox.setLayout(self.baundLabel)

        self.specify.addWidget(self.deviceBox, 3, 0, 1, 0)
        self.specify.addWidget(self.baundrateBox, 4, 0, 1, 0)
        self.setLayout(self.specify)

    def addModule(self):
        name = Monit(self)
        name.message('Platforma', 'Wpisz nową platformę')
        if name.exec():
            gadget = name.inputmsg.text()
            ConfigFiles.change(self, position=self._devices, param=gadget)
            self.comboDevices.update(gadget)
        else:
            pass

    def resetModule(self):
        ConfigFiles.defaultModule(self)
        self._new = ConfigFiles.showData(self)
        self.comboDevices.clear()
        self.comboDevices.update(self._new[self._devices])

    def jump(self):
        self.hide()
        plotWindow = Plot_Window(parent=self,
                                 device=self.comboDevices.option, baudrate=self.comboBaudrate.option)
        plotWindow.show()

    def _configText(self, text):
        self.centralText = QLabel(
            f"{text[0]}")
        self.centralText.setWordWrap(True)
        self.centralText.setFont(QFont('Times', text[1]))
        self.centralText.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        return self.centralText
