# lista bibliotek wykorzystanych w projekcie
# biblioteki do aplikacji okienkowej
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QMainWindow, QApplication, QDesktopWidget, QComboBox, QGroupBox, QGridLayout, QWidget, QPushButton, QLabel, QLineEdit, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QDialog, QFileDialog
from PyQt5.QtGui import QFont, QPixmap

# biblioteka do zwijania funkcji o kilku parametrach do przycisku
from functools import partial

# biblioteki do przetwarzania danych i wizualizacji
import json
import sys
from datetime import date, datetime
import pandas as pd
import numpy as np
import pyqtgraph as pg
from pyqtgraph.ptime import time
from pathlib import Path
import csv

# biblioteki odpowiedzialne za polączenie z arduino po serialu
from serial.serialutil import SerialException
import serial.tools.list_ports
import serial as sr
