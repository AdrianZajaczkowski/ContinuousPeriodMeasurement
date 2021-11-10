from Liblarys import *
from SerialConnection import *


class ConfigFiles:
    def __init__(self):
        super(ConfigFiles, self).__init__()

    def change(self, position, param):
        with open('config.json', 'r') as fp:
            data = json.load(fp)
        data[position].append(param)
        with open('config.json', 'w') as devi:
            json.dump(data, devi, indent=4)

    def showData(self):
        with open('config.json', 'r') as fp:
            data = json.load(fp)
        return data

    def defaultModule(self):
        self.old = ConfigFiles.showData(self)
        serialConnection = SerialConnection()
        self._module = serialConnection.showDevices()
        print(self.old)
        self.old["devices"] = self._module
        print(self.old)
        with open('config.json', 'w') as devi:
            json.dump(self.old, devi, sort_keys=True, indent=4)
