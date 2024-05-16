import pyvisa
import time
import serial
import json
import pandas as pd
import datetime
import os


csv = pd.read_csv("Sample_Rates.csv")
Input_Cases = [Val for Val in csv["input_voltage"]]
sample_rates = [rates for rates in csv["samples"]]
for i in range(len(Input_Cases)):
    INVolt,sample_rate = Input_Cases[i],sample_rates[i]
    print(INVolt,sample_rate)

