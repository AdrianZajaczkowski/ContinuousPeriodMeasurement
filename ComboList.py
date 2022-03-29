from libraries import *

# klasa od interakcji z rozwijaną listą


class ComboList(QComboBox):

    def __init__(self, parent, **kwargs):
        self.option = kwargs.pop('option')
        self.default = kwargs.pop('default')
        super(ComboList, self).__init__(parent)
        self.setupCombo()

    def setupCombo(self):

        if self.default and not isinstance(self.default, list):
            self.addItem(self.default)
        else:
            self.default = None
        self.addItem('-Wybierz opcje-')
        self.addItems(self.option)
        self.activated[str].connect(self.setData)
        self.setEditable(False)
        self.adjustSize()

    def new(self, param):
        if isinstance(param, str):
            self.addItem(param)
        elif isinstance(param, list):
            self.addItems(param)
        else:
            print("Invalid parameter")

    def update(self, param):
        if self.findText("-Wybierz opcje-"):
            self.addItem("-Wybierz opcje-")
        else:
            pass
        if isinstance(param, str):
            self.addItem(param)
        elif isinstance(param, list):
            self.addItems(param)
        else:
            print("Invalid parameter")

    def setData(self, text):
        self.option = text
        # print(text)
        if not isinstance(text, list):
            self.default = text
