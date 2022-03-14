# class to setup view of errors prompt monit
from libraries import *


class TimePrompt(QDialog):
    def __init__(self, parent=None):
        super(TimePrompt, self).__init__(parent)

    def message(self, title='Uwaga!', msg=None):
        self.setWindowTitle(f'{title}')
        self.layout = QVBoxLayout()
        self.wid = QWidget(self)
        self.msg = QLabel(f'{msg}')
        self.layout.addWidget(self.msg)
        self.wid.setLayout(self.layout)

        # self.setLayout(self.layout)
        # popraw wyświetlanie widgeta i będzie git
