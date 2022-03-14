# class to config propmpt monit of adding elements
from libraries import *


class Monit(QDialog):
    def __init__(self, parent=None):
        super(Monit, self).__init__(parent)

    def message(self, title='Platforma', msg='Wprowadź nową platformę'):
        self.setWindowTitle(f'{title}')
        self.msg = QLabel(f'{msg}')
        self.layout = QVBoxLayout()

        self.inputmsg = QLineEdit(self)
        btn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button = QDialogButtonBox(btn)
        self.button.accepted.connect(self.accept)
        self.button.rejected.connect(self.reject)

        self.layout.addWidget(self.msg)
        self.layout.addWidget(self.inputmsg)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)
