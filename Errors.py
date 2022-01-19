# class to setup view of errors prompt monit
from Liblarys import *


class Errors(QDialog):
    def __init__(self, parent=None):
        super(Errors, self).__init__(parent)

    def message(self, title='Błąd', msg1=''):
        self.setWindowTitle(f'{title}')

        self.layout = QVBoxLayout()
        self.msg = QLabel(f'{msg1}')
        btn = QDialogButtonBox.Ok
        self.button = QDialogButtonBox(btn)
        self.button.accepted.connect(self.accept)

        self.layout.addWidget(self.msg)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)
