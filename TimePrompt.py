# class to setup view of errors prompt monit
from libraries import *

# klasa do wyświtlania monitów o długości pomiaru


class TimePrompt(QDialog):
    def __init__(self, parent=None):
        super(TimePrompt, self).__init__(parent)
        frame = self.frameGeometry()
        position = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(position)
        self.move(frame.topLeft())
        self.msg = QLabel()
        self.msg.setFont(QFont('Times', 15))
        self.msg.setWordWrap(True)
        self.layout = QVBoxLayout()

    def message(self, title='Uwaga!', msg=None):
        self.setWindowTitle(f'{title}')
        self.msg.setText(f'{msg}')
        self.msg.adjustSize()
        self.layout.addWidget(self.msg)
        self.setLayout(self.layout)
        self.show()
