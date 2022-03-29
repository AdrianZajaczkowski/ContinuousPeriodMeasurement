#!/usr/bin/env python
# Początek programu, inicjowanie programu
from WelcomeWindow import WelcomeWindow
from libraries import *

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WelcomeWindow()
    window.show()               # wyświetlenie głównego okna ustawień
    sys.exit(app.exec_())
