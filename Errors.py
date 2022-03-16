# class to setup view of errors prompt monit
from libraries import *


class Errors(QDialog):
    def __init__(self, parent=None):
        super(Errors, self).__init__(parent)
        self.layout = QVBoxLayout()
        self.msg = QLabel()
        btn = QDialogButtonBox.Ok
        self.button = QDialogButtonBox(btn)
        self.button.clicked.connect(self.accept)

    def message(self, title='Błąd', msg=''):
        self.setWindowTitle(f'{title}')
        self.msg.setText(f'{msg}')
        self.msg.setAlignment(Qt.AlignCenter)
        self.msg.setFont(QFont('Times', 10))
        self.layout.addWidget(self.msg)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)
