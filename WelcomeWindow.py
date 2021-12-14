from Liblarys import *
from ConfigFiles import *
from ComboList import *
from Monit import *
from PlottingAxes import *


class WelcomeWindow(QWidget):
    def __init__(self, parent=None):
        self._devices = "devices"
        self._baudrate = "baudrate"
        self._tenderness = "tenderness"
        super(WelcomeWindow, self).__init__(parent)
        self.files = ConfigFiles()
        self.setWindowTitle("Python 3.9.7")
        self._configLayout()

    def _configLayout(self):
        self.setFixedSize(900, 600)
        frame = self.frameGeometry()
        position = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(position)
        self.move(frame.topLeft())
        self.logoLabel = QLabel(self)
        self.logo = QPixmap('..\MeansurePerioid\sheets\pollubLogo.png')

        self.logoLabel.setPixmap(self.logo)

        self.pkg = self.files.showData()
        self.dev = self.pkg[self._devices]
        self.baud = self.pkg[self._baudrate]
        self.tenderness = self.pkg[self._tenderness]
        self.descr = self._configText(text=self.pkg["text"]['Start'])
        self.author = self._configText(text=self.pkg["text"]['Autor'],)
        self.comboDevices = ComboList(self, option=self.dev)
        self.comboBaudrate = ComboList(self, option=self.baud)
        self.comboTenderness = ComboList(self, option=self.tenderness)

        self.addDeviceButton = QPushButton('Dodaj nową platformę', self)
        self.addTendernessButton = QPushButton(
            'Dodaj czułość przekaźnika', self)
        self.resetDeviceButton = QPushButton('Odświerz platfory', self)
        self.resetTendernessButton = QPushButton(
            'Reset do wartości pierowtnej', self)
        self.goButton = QPushButton('Zacznij pomiary', self)
        self.textBaudrate = QLabel(
            "Baudrate")
        self.textDevice = QLabel("Platforma")
        self.textBaudrate.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.textDevice.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.textBaudrate.resize(20, 5)
        self.logoLabel.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        # funkcje przycisków po kliknięciu
        addDevice = partial(self.addModule, self.comboDevices,
                            self._devices, 'Platforma', 'Wpisz nową platformę')
        addTenderness = partial(self.addModule, self.comboTenderness,
                                self._tenderness, 'Czułość', 'Wpisz nową czułość')
        resetDevice = partial(self.resetDevices, self._devices)
        resetTenderness = partial(self.resetTenderss, self._tenderness)

        self.addDeviceButton.clicked.connect(addDevice)
        self.resetDeviceButton.clicked.connect(resetDevice)
        self.addTendernessButton.clicked.connect(addTenderness)
        self.resetTendernessButton.clicked.connect(resetTenderness)
        self.goButton.clicked.connect(self.jump)

        self.deviceBox = QGroupBox("Platforma")
        self.baundrateBox = QGroupBox("Baundrate")
        self.tendernessBox = QGroupBox("Czułość przetwornika")
        self.specify = QGridLayout()
        self.deviceLabel = QGridLayout()
        self.baundLabel = QGridLayout()
        self.tendernessLabel = QGridLayout()

        self.specify.addWidget(self.logoLabel, 0, 0, 1, 0)
        self.specify.addWidget(self.descr, 1, 0, 2, 3)
        self.specify.addWidget(self.author, 2, 0, 1, 0)

        self.deviceLabel.addWidget(self.addDeviceButton, 1, 0)
        self.deviceLabel.addWidget(self.resetDeviceButton, 1, 1)
        self.deviceLabel.addWidget(self.goButton, 1, 2)
        self.deviceLabel.addWidget(self.comboDevices, 2, 0, 1, 0)
        self.deviceBox.setLayout(self.deviceLabel)

        self.baundLabel .addWidget(self.comboBaudrate, 1, 0, 1, 0)
        self.baundrateBox.setLayout(self.baundLabel)

        self.tendernessLabel.addWidget(self.addTendernessButton, 1, 0)
        self.tendernessLabel.addWidget(self.resetTendernessButton, 1, 1)
        self.tendernessLabel.addWidget(self.comboTenderness, 2, 0, 1, 0)
        self.tendernessBox.setLayout(self.tendernessLabel)

        self.specify.addWidget(self.deviceBox, 3, 0, 1, 0)
        self.specify.addWidget(self.baundrateBox, 4, 0, 1, 0)
        self.specify.addWidget(self.tendernessBox, 5, 0, 1, 0)
        self.setLayout(self.specify)

    def addModule(self, combo, element, title, monit):
        name = Monit(self)
        name.message(f'{title}', f'{monit}')
        if name.exec():
            gadget = name.inputmsg.text()
            self.files.change(position=element, param=gadget)
            combo.update(gadget)
        else:
            pass

    def resetDevices(self, param):
        self.files.defaultDevices(param)
        self._new = self.files.showData()
        self.comboDevices.clear()
        self.comboDevices.update(self._new[param])

    def resetTenderss(self, param):
        self.files.defaultTenderss(param)
        self._new = self.files.showData()
        self.comboTenderness.clear()
        self.comboTenderness.update(self._new[param])

    def jump(self):
        self.hide()
        plotWindow = Plot_Window(parent=self,
                                 device=self.comboDevices.option, baudrate=self.comboBaudrate.option, tenderness=self.comboTenderness.option)
        plotWindow.showPlots()

    def _configText(self, text):
        self.centralText = QLabel(
            f"{text[0]}")
        self.centralText.setWordWrap(True)
        self.centralText.setFont(QFont('Times', text[1]))
        self.centralText.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        return self.centralText
