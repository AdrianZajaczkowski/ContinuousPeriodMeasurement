# lista bibliotek wykorzystanych w projekcie
# biblioteki do aplikacji okienkowej
from ctypes.wintypes import BYTE
from subprocess import call
import struct
import serial as sr
import serial.tools.list_ports
from serial.serialutil import SerialException
import bz2
import pickle
import csv
from pathlib import Path
import pyqtgraph as pg
import numpy as np
import pandas as pd
import time
from datetime import date, datetime
import os
import sys
import json
import threading
from functools import partial
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread, QDir, pyqtSignal, Qt, QObject
from PyQt5.QtWidgets import QMainWindow, QAction,  QApplication, QDesktopWidget, QComboBox, QGroupBox, QGridLayout, QWidget, QPushButton, QLabel, QLineEdit, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QDialog, QMessageBox, QFileDialog
from PyQt5.QtGui import QFont, QPixmap, QKeySequence
import logging
logging.basicConfig(filename='myProgramLog.txt', level=logging.DEBUG, filemode='w',
                    format=' Date time :%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s- line no: %(lineno)d - %(message)s')  # zapis logów do pliku, uwzględniając poziomy od Debug i wyżej, data/leve/wiadomosc

# biblioteka do zwijania funkcji o kilku parametrach do przycisku
# biblioteki do przetwarzania danych i wizualizacji


# biblioteki odpowiedzialne za polączenie z arduino po serialu
