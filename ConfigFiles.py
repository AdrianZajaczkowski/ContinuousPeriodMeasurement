from Liblarys import *
from SerialConnection import *


class ConfigFiles:
    def __init__(self):
        super(ConfigFiles, self).__init__()

    def change(self, position, param):
        print(position, param)
        with open('config.json', 'r') as fp:
            data = json.load(fp)
        data[position].append(param)
        print(data)
        with open('config.json', 'w') as devi:
            json.dump(data, devi, indent=4)

    def showData(self):
        with open('config.json', 'r') as fp:
            data = json.load(fp)
        return data

    def defaultDevices(self, position):
        self.old = ConfigFiles.showData(self)

        serialConnection = SerialConnection()
        self._module = serialConnection.showDevices()
        print(self.old)
        self.old[position] = self._module
        print(self.old)
        with open('config.json', 'w') as devi:
            json.dump(self.old, devi, sort_keys=True, indent=4)

    def defaultTenderss(self, position):
        self.old = ConfigFiles.showData(self)
        self._module = "1"
        print(self.old)
        self.old[position] = list(self._module)
        print(self.old)
        with open('config.json', 'w') as devi:
            json.dump(self.old, devi, sort_keys=True, indent=4)


"""ps = ConfigFiles()
print(ps.showData())
"""
