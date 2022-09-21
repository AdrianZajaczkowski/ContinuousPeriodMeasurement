#!/usr/bin/env python
# Początek programu, inicjowanie programu
from WelcomeWindow import WelcomeWindow
from libraries import *

if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = WelcomeWindow()
    window.show()               # wyświetlenie głównego okna ustawień
    sys.exit(app.exec_())
    # słącza miso do spi wyprowadzenia # przyomnienie o programatorze

    # gromadzenie stanów licznika w pamięci ram
# z powodu stabilizacji transmisji, począ☻tkowe x danych jest odrzucanych, ponieważ podczas stabilizacji, dane są przekłamane
# dodaj okno do edycji tytułu F- częstotliwość dewiacji F0- częsotliwość srodkowa, FM - ampituda
# dodaj do głównego pliku po analizie stany licznika H L
# ... z wykorzystaniem mikrokontrolera z rodziny avr
