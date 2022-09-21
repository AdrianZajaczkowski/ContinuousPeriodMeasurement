from libraries import *
from ConfigDropList import *
from ComboList import *
from PlotWindow import *
from SerialConnection import *
# Klasa odpowiedzialna za wprowadzenie ustawień startowych do pragoramu


class WelcomeWindow(QWidget):
    logging.info("Start App")
    # sygnał odpowiadający za przekazanie parametrów do metody SerialConnection.connect()
    signalSerial = pyqtSignal(str, str, str, str)

    def __init__(self, parent=None):
        super(WelcomeWindow, self).__init__(parent)
        self._devices = "devices"
        self._baudrate = "baudrate"
        self._tenderness = "tenderness"
        self.default = False
        self.serial = SerialConnection()
        self.radioEndiannessState = '>'
        self.files = ConfigDropList()
        self.setWindowTitle("Python 3.9.7")
        self.serial.showDevices()  # wykrycie podłaczonych mikrokontrolerów
        self._configLayout()

    def configButtons(self):  #
        self.pkg = self.files.showData()
        self.dev = self.pkg[self._devices]
        self.baud = self.pkg[self._baudrate]
        self.tenderness = self.pkg[self._tenderness]

        self.comboDevices = ComboList(
            self, option=self.dev["standard"], default=self.dev["default"])
        self.comboBaudrate = ComboList(
            self, option=self.baud["standard"], default=self.baud["default"])
        self.comboTenderness = ComboList(
            self, option=self.tenderness["standard"], default=self.tenderness["default"])
        # tworzenie obiektów wspomagających edytowanie list
        self.addDeviceButton = QPushButton('Dodaj nową platformę', self)
        self.addTendernessButton = QPushButton(
            'Dodaj czułość przekaźnika', self)
        self.addBaudrateButton = QPushButton('Dodaj nowy baudrate', self)

        self.resetDeviceButton = QPushButton('Odśwież platformy', self)
        self.resetBaudrateButton = QPushButton('Reset baudrate', self)
        self.resetTendernessButton = QPushButton('Reset czułości', self)
        self.goButton = QPushButton('Zacznij pomiary', self)

        # przesyłanie danych z okien wyboru do ponownego zapisu do pliku config.json
        # takie działanie ma na celu zapis nowych danych do pliku i późniejsze wykorzystanie danych
        addDevice = partial(self.files.addItem, self, self.comboDevices,
                            self._devices, "standard", 'Platforma', 'Wpisz nową platformę')
        addBaudrate = partial(self.files.addItem, self, self.comboBaudrate,
                              self._baudrate, "standard", 'Baudrate', 'Wpisz nową wartość baudarte')
        addTenderness = partial(self.files.addItem, self, self.comboTenderness,
                                self._tenderness, "standard", 'Czułość', 'Wpisz nową czułość')

        resetDevice = partial(
            self.files.resetList, self.comboDevices, self._devices, "standard", option="device")
        resetTenderness = partial(
            self.files.resetList, self.comboTenderness, self._tenderness, "standard")
        resetBaudrate = partial(
            self.files.resetList, self.comboBaudrate, self._baudrate, "standard")

        self.addDeviceButton.clicked.connect(addDevice)
        self.addBaudrateButton.clicked.connect(addBaudrate)
        self.addTendernessButton.clicked.connect(addTenderness)

        self.resetDeviceButton.clicked.connect(resetDevice)
        self.resetBaudrateButton.clicked.connect(resetBaudrate)
        self.resetTendernessButton.clicked.connect(resetTenderness)
        self.goButton.clicked.connect(self.jump)

        self.radioEndianness1 = QRadioButton('Little Endian')
        self.radioEndianness2 = QRadioButton('Big Endian')
        self.radioEndianness2.setChecked(True)
        self.radioEndianness1.toggled.connect(
            lambda: self.changeRadio(self.radioEndianness1))
        self.radioEndianness2.toggled.connect(
            lambda: self.changeRadio(self.radioEndianness2))

    def changeRadio(self, radio):

        if radio.text() == 'Little Endian':
            if radio.isChecked() == True:
                self.radioEndiannessState = '<'
            else:
                pass
        if radio.text() == 'Big Endian':
            if radio.isChecked() == True:
                self.radioEndiannessState = '>'
            else:
                pass

    def _configLayout(self):  # metoda do konfiguracji okna klasy
        self.configButtons()

        font = QFont()
        font.setPixelSize(17)
        self.setFont(font)
        self.resize(1024, 800)

        frame = self.frameGeometry()
        position = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(position)
        self.move(frame.topLeft())

        self.logoLabel = QLabel(self)
        self.logo = QPixmap('..\MeansurePerioid\sheets\pollubLogo.png')
        self.logoLabel.setPixmap(self.logo)
        # pobieranie wartości do wyświetlenia z pliku config.json przy pomocy klasy ConfigDropList()
        self.descr = self._configText(text=self.pkg["text"]['Start'])
        self.author = self._configText(text=self.pkg["text"]['Autor'])
        # inicjacja rozwijanych list
        self.logoLabel.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        # inicjowanie siatki elementów oraz grup elementów do wyświetlenia
        self.deviceBox = QGroupBox("Platforma")
        self.baundrateBox = QGroupBox("Baudrate")
        self.tendernessBox = QGroupBox("Czułość przetwornika")
        self.radioEndiannesBox = QGroupBox("Endianness")

        self.specify = QGridLayout()
        self.deviceLabel = QGridLayout()
        self.baundLabel = QGridLayout()
        self.tendernessLabel = QGridLayout()
        self.endiannessLabel = QGridLayout()

        # self.radioGroup = QButtonGroup()
        # self.radioGroup.addButton(self.radioEndianness1)
        # self.radioGroup.addButton(self.radioEndianness2)
        # rozmiezczenie elementów w interfejsie okna
        self.specify.addWidget(self.logoLabel, 0, 0, 1, 0)
        self.specify.addWidget(self.descr, 1, 0, 2, 3)
        self.specify.addWidget(self.author, 2, 0, 1, 0)

        self.deviceLabel.addWidget(self.addDeviceButton, 1, 0)
        self.deviceLabel.addWidget(self.resetDeviceButton, 1, 1)
        self.deviceLabel.addWidget(self.goButton, 1, 2)
        self.deviceLabel.addWidget(self.comboDevices, 2, 0, 1, 0)
        self.deviceBox.setLayout(self.deviceLabel)

        self.baundLabel.addWidget(self.addBaudrateButton, 1, 0)
        self.baundLabel.addWidget(self.resetBaudrateButton, 1, 1)
        self.baundLabel .addWidget(self.comboBaudrate, 2, 0, 1, 0)
        self.baundrateBox.setLayout(self.baundLabel)

        self.tendernessLabel.addWidget(self.addTendernessButton, 1, 0)
        self.tendernessLabel.addWidget(self.resetTendernessButton, 1, 1)
        self.tendernessLabel.addWidget(self.comboTenderness, 2, 0, 1, 0)
        self.tendernessBox.setLayout(self.tendernessLabel)

        self.endiannessLabel.addWidget(self.radioEndianness1, 1, 0)
        self.endiannessLabel.addWidget(self.radioEndianness2, 1, 1)
        self.radioEndiannesBox.setLayout(self.endiannessLabel)

        self.specify.addWidget(self.deviceBox, 3, 0, 1, 0)
        self.specify.addWidget(self.radioEndiannesBox, 4, 0, 1, 0)
        self.specify.addWidget(self.baundrateBox, 5, 0, 1, 0)
        self.specify.addWidget(self.tendernessBox, 6, 0, 1, 0)
        self.setLayout(self.specify)
    # ustawienie tekstu nagłówków

    def _configText(self, text):
        self.centralText = QLabel(
            f"{text[0]}")
        self.centralText.setWordWrap(True)
        self.centralText.setFont(QFont('Times', text[1]))
        self.centralText.setAlignment(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        return self.centralText
    # automatyczne zmienianie wielkości tekstu pod wpływem zmiany wielkości okna

    def resizeText(self, event):
        defaultSize = 9
        if self.rect().width() // 40 > defaultSize:
            f = QFont('', self.rect().width() // 40)
        else:
            f = QFont('', defaultSize)
        self.setFont(f)

    def jump(self):  # metoda odpowiadająca za uruchomienie dwóch klas, SerialConnection oraz PlotAxes
        self.hide()
        self.files.setDefaulfValue(
            name="devices", position="default", element=self.comboDevices.default)
        self.files.setDefaulfValue(
            name="baudrate", position="default", element=self.comboBaudrate.default)
        self.files.setDefaulfValue(
            name="tenderness", position="default", element=self.comboTenderness.default)

        # połączenie do metody SerialConnection.connect()
        self.signalSerial.connect(self.serial.connect)
        if self.dev["default"] and self.baud["default"] and self.tenderness["default"]:
            self.signalSerial.emit(self.comboDevices.default,
                                   self.comboBaudrate.default, '1', self.radioEndiannessState)  # emitowanie konfiguracji do połączenia z mikrokontrolerem
        else:
            self.signalSerial.emit(self.comboDevices.option,
                                   self.comboBaudrate.option, '1', self.radioEndiannessState)
        plotWindow = PlotWindow(
            parent=self, serial=self.serial, pkg=self.pkg)
        plotWindow.showSecondWindow()  # wyświetlenie okna PlotAxes
