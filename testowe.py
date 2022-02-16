
import serial as sr
import struct
import struct
import csv
import pandas as pd
from pathlib import Path
from datetime import datetime

csvs = pd.DataFrame()
path_s = r'D:\\MeansurePerioid\\wyniki pomiarów\\'
title = "pomiar50khz4.csv"
csvs.to_csv(Path(path_s+title), index=False, sep=';')


def csvWrite(row):

    with open(f'{path_s+title}', 'a+', newline='') as file:
        writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_NONE)
        writer.writerow(row)
        file.close()


hader = ["timestamp", "Ni"]
csvWrite(hader)
arr = [None, None]
ardu = sr.Serial(port='COM6', baudrate=38400)
# ardu.write(b's')
lastValue = 0

while True:
    headerByte = ardu.read(2)
    headers = struct.unpack('<H', headerByte)[0]

    if (headers == 2):
        payload = ardu.read(2)
        now = datetime.now()

        arr[0] = now.strftime("%H:%M:%S")
        value = struct.unpack('<H', payload)[0]
        arr[1] = value
        valueDifference = lastValue - value
        lastValue = value
        end = ardu.read(2)

        end = struct.unpack('<H', end)[0]
        if end == 3:

            csvWrite(arr)
