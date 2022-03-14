# Class to reate litsts of elements
from libraries import *
from SerialConnection import *


class ConfigFiles:
    def __init__(self):
        super(ConfigFiles, self).__init__()
        self.configPath = 'D:\MeansurePerioid\config.json'

    # metoda dodawania elementu do pliku configuracyjnego w zależności od listy
    def change(self, part, position, param):
        with open(self.configPath, 'r') as fp:
            data = json.load(fp)
        data[part][position].append(param)
        with open(self.configPath, 'w') as devi:
            json.dump(data, devi, indent=4)

    def setDefaulfValue(self, name, position, element):
        with open(self.configPath, 'r') as fp:
            data = json.load(fp)
        data[name][position] = element
        with open(self.configPath, 'w') as devi:
            json.dump(data, devi, indent=4)
    # metoda zwracajaca wszystko z pliku configuracyjnego

    def showData(self):
        with open(self.configPath, 'r') as fp:
            data = json.load(fp)
        return data

    # reset mikrokontrolerów do pozycji domyslnych
    def defaultDevices(self, part, position):
        self.old = ConfigFiles.showData(self)

        serialConnection = SerialConnection()
        self._module = serialConnection.showDevices()

        self.old[part][position] = self._module

        with open(self.configPath, 'w') as devi:
            json.dump(self.old, devi, sort_keys=True, indent=4)

     # zmiana czułości do wartości domyslnych
    def defaultTenderss(self, part, position):
        self.old = ConfigFiles.showData(self)
        self._module = "1"

        self.old[part][position] = list(self._module)

        with open(self.configPath, 'w') as devi:
            json.dump(self.old, devi, sort_keys=True, indent=4)


# app = ConfigFiles()

# print(app.showData())
# app.setDefaulfValue(name="baudrate", position="default", element="b")
# print(app.showData())
