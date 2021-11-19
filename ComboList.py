from Liblarys import *


class ComboList(QComboBox):

    def __init__(self, parent, **kwargs):
        self.option = kwargs.pop('option')

        super(ComboList, self).__init__(parent)
        self.setupCombo()

    def setupCombo(self):
        self.addItems(self.option)
        self.activated[str].connect(self.setData)
        self.setEditable(False)
        self.adjustSize()

    def update(self, param):
        if isinstance(param, str):
            self.addItem(param)
        elif isinstance(param, list):
            self.addItems(param)
        else:
            print("Invalid parameter")

    def setData(self, text):  # przesył do innej klasy
        self.option = text
        print(self.option)
