from Liblarys import *


class Monit(QDialog):
    def __init__(self, parent=None):
        super(Monit, self).__init__(parent)

        self.setWindowTitle("Platforma")
        self.msg = QLabel("Wprowadź nową platformę")

        btn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.inputmsg = QLineEdit(self)
        self.button = QDialogButtonBox(btn)
        self.button.accepted.connect(self.accept)
        self.button.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.msg)
        self.layout.addWidget(self.inputmsg)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)
