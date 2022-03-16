from libraries import *
from ConfigFiles import *
from ComboList import *
from Monit import *
from PlottingAxes import *


class WelcomeWindow(QWidget):
    signal = pyqtSignal(str, str, str)

    def __init__(self, parent=None):
        self._devices = "devices"
        self._baudrate = "baudrate"
        self._tenderness = "tenderness"
        self.default = False
        super(WelcomeWindow, self).__init__(parent)
        self.files = ConfigFiles()
        self.serial = SerialConnection()
        self.setWindowTitle("Python 3.9.7")
        self._configLayout()

    def _configLayout(self):

        font = QFont()
        font.setPixelSize(17)
        self.setFont(font)
        self.resize(1024, 700)
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
        self.author = self._configText(text=self.pkg["text"]['Autor'])

        self.comboDevices = ComboList(
            self, option=self.dev["standard"], default=self.dev["default"])
        self.comboBaudrate = ComboList(
            self, option=self.baud["standard"], default=self.baud["default"])
        self.comboTenderness = ComboList(
            self, option=self.tenderness["standard"], default=self.tenderness["default"])

        self.addDeviceButton = QPushButton('Dodaj nową platformę', self)
        self.addTendernessButton = QPushButton(
            'Dodaj czułość przekaźnika', self)
        self.resetDeviceButton = QPushButton('Odśwież platformy', self)
        self.resetTendernessButton = QPushButton(
            'Reset do wartości pierwotnej', self)
        self.goButton = QPushButton('Zacznij pomiary', self)
        self.logoLabel.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        addDevice = partial(self.addModule, self.comboDevices,
                            self._devices, "standard", 'Platforma', 'Wpisz nową platformę')
        addTenderness = partial(self.addModule, self.comboTenderness,
                                self._tenderness, "standard", 'Czułość', 'Wpisz nową czułość')
        resetDevice = partial(self.resetDevices, self._devices, "standard")
        resetTenderness = partial(
            self.resetTenderss, self._tenderness, "standard")

        self.addDeviceButton.clicked.connect(addDevice)
        self.resetDeviceButton.clicked.connect(resetDevice)
        self.addTendernessButton.clicked.connect(addTenderness)
        self.resetTendernessButton.clicked.connect(resetTenderness)
        self.goButton.clicked.connect(self.jump)

        self.deviceBox = QGroupBox("Platforma")
        self.baundrateBox = QGroupBox("Baudrate")
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

    def resizeText(self, event):
        defaultSize = 9
        if self.rect().width() // 40 > defaultSize:
            f = QFont('', self.rect().width() // 40)
        else:
            f = QFont('', defaultSize)
        self.setFont(f)

    def addModule(self, combo, pos, element, title, monit):
        name = Monit(self)
        name.message(f'{title}', f'{monit}')
        if name.exec():
            gadget = name.inputmsg.text()
            self.files.change(part=pos, position=element, param=gadget)
            combo.new(gadget)
        else:
            pass

    def resetDevices(self, param, position):
        self.files.defaultDevices(param, position)
        self._new = self.files.showData()
        self.comboDevices.clear()
        self.comboDevices.update(self._new[param][position])

    def resetTenderss(self, param, position):
        self.files.defaultTenderss(param, position)
        self._new = self.files.showData()
        self.comboTenderness.clear()
        self.comboTenderness.update(self._new[param][position])

    def jump(self):

        self.hide()
        self.files.setDefaulfValue(
            name="devices", position="default", element=self.comboDevices.default)
        self.files.setDefaulfValue(
            name="baudrate", position="default", element=self.comboBaudrate.default)
        self.files.setDefaulfValue(
            name="tenderness", position="default", element=self.comboTenderness.default)

        if self.dev["default"] and self.baud["default"] and self.tenderness["default"]:
            self.serial.showDevices()
            self.signal.connect(self.serial.connect)

            self.signal.emit(self.comboDevices.default,
                             self.comboBaudrate.default, '1')
            plotWindow = Plot_Window(
                parent=self, serial=self.serial, pkg=self.pkg)

            plotWindow.showSecondWindow()
        else:
            self.serial.showDevices()
            self.signal.connect(self.serial.connect)

            self.signal.emit(self.comboDevices.option,
                             self.comboBaudrate.option, '1')
        plotWindow = Plot_Window(
            parent=self, serial=self.serial, pkg=self.pkg)

        plotWindow.showSecondWindow()

    def _configText(self, text):
        self.centralText = QLabel(
            f"{text[0]}")
        self.centralText.setWordWrap(True)
        self.centralText.setFont(QFont('Times', text[1]))
        self.centralText.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        return self.centralText
