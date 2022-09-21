# Class to reate litsts of elements
from libraries import *
from SerialConnection import *
# klasa do interakcji z rozwijanymi listami
from Monit import *


class ConfigDropList:
    def __init__(self):
        # self.serial = kwargs.pop('serial')
        super(ConfigDropList, self).__init__()
        self.configPath = 'src\config.json'

    # metoda dodawania elementu do pliku configuracyjnego w zależności od listy
    def jsonDump(self, data):
        with open(self.configPath, 'w') as devi:
            json.dump(data, devi, sort_keys=True, indent=4)

    def showData(self):
        with open(self.configPath, 'r') as fp:
            data = json.load(fp)
        return data

    def change(self, part, position, param):
        data = self.showData()
        data[part][position].append(param)
        self.jsonDump(data)

    def setDefaulfValue(self, name, position, element):
        data = self.showData()
        data[name][position] = element
        self.jsonDump(data)

    def addItem(self, object, combo, pos, element, title, monit):
        name = Monit(object)
        name.message(f'{title}', f'{monit}')
        if name.exec():
            gadget = name.inputmsg.text()
            self.change(part=pos, position=element, param=gadget)
            combo.new(gadget)

    def defaultDevices(self, part, position):
        data = self.showData()
        serialConnection = SerialConnection()
        devices = serialConnection.showDevices()
        data[part][position] = devices
        self.jsonDump(data)

     # zmiana czułości do wartości domyslnych
    def setDefaultList(self, part, position):
        data = self.showData()
        data[part][position] = data[part]["recovery"]
        self.jsonDump(data)

    def resetList(self, combo, param, position, option=None):
        if option == "device":
            self.defaultDevices(param, position)
        else:
            self.setDefaultList(param, position)
        self._new = self.showData()
        combo.clear()
        combo.update(self._new[param][position])
