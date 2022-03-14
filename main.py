#!/usr/bin/env python
from WelcomeWindow import WelcomeWindow
from libraries import *

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WelcomeWindow()
    window.show()
    sys.exit(app.exec_())
