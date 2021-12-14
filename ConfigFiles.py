from Liblarys import *
from SerialConnection import *


class ConfigFiles:
    def __init__(self):
        super(ConfigFiles, self).__init__()
        self.configPath = 'config.json'

    def change(self, position, param):

        with open(self.configPath, 'r') as fp:
            data = json.load(fp)
        data[position].append(param)
        with open(self.configPath, 'w') as devi:
            json.dump(data, devi, indent=4)

    def showData(self):
        with open(self.configPath, 'r') as fp:
            data = json.load(fp)
        return data

    def defaultDevices(self, position):
        self.old = ConfigFiles.showData(self)

        serialConnection = SerialConnection()
        self._module = serialConnection.showDevices()

        self.old[position] = self._module

        with open(self.configPath, 'w') as devi:
            json.dump(self.old, devi, sort_keys=True, indent=4)

    def defaultTenderss(self, position):
        self.old = ConfigFiles.showData(self)
        self._module = "1"

        self.old[position] = list(self._module)

        with open(self.configPath, 'w') as devi:
            json.dump(self.old, devi, sort_keys=True, indent=4)


'''ps = ConfigFiles()
print(ps.showData())
'''
