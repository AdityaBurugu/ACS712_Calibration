import pyvisa
import time
import serial
import json
import pandas as pd
import datetime
import os

INVolt = input("Enter Supply Voltage:")

csv = pd.read_csv("Sample_Rates.csv")
Input_Cases = [Val for Val in csv["input_voltage"]]
sample_rates = [rates for rates in csv["samples"]]
if INVolt in Input_Cases:
    index = Input_Cases.index(INVolt)
else:
    index = Input_Cases.index("default")

sample_rate = int(sample_rates[index])

def Connection():
    # Query if rmt_loadrument is present
    try:
        rm = pyvisa.ResourceManager()
        ser = serial.Serial("COM3", 9600)
        rmt_load = rm.open_resource("RIGOL_DC_ELoad")  ####  TCPIP0::192.168.178.112::rmt_loadR
        rmt_rps = rm.open_resource("LRPS")
        print(rmt_rps.query("*IDN?"))
        print(rmt_load.query("*IDN?"))
        run = True
    except:
        run = False
    return run,rmt_load,rmt_rps,ser

def Initialise_Parameters(rmt_rps,rmt_load):
    rmt_rps.write("*RST")  # Resets to Default Values
    time.sleep(1)

    rmt_load.write("*RST")  # Resets to Default Values
    time.sleep(1)

    rmt_rps.write(f''':VOLT {INVolt}''')  # Sets Voltage Level of RPS
    time.sleep(.1)

    rmt_rps.write(":OUTP:STAT CH1,ON")  # Enable RPS
    time.sleep(.1)

    rmt_load.write(":SOUR:LIST:MODE CC")  # Sets To Constant Current Mode
    time.sleep(.1)

    print("Mode: ", rmt_load.query(":SOURCE:LIST:MODE?").strip())
    time.sleep(1)

    rmt_load.write(f''':SOUR:CURR:VON {INVolt}''')  # Sets VOn to 24V
    time.sleep(.1)

    rmt_load.write(":SOUR:CURR:RANG 40")  # Sets Curret Range to 4A or 40A
    time.sleep(.1)

    rmt_load.write(":SOURCE:INPUT:STATE On")  # Enable electronic load
    time.sleep(.1)

def Read(rmt_load,ser):
    load_list = []
    recv_list = []
    cur = 0
    maxLoad = 5
    tolerance = 0.2
    while cur <= (maxLoad + tolerance):
        load_Current = round(cur, 2)
        rmt_load.write(f''':SOUR:CURR:LEV:IMM {load_Current}''')  # sets Load Current
        # Wait for value to stabilize
        # Measure!
        print("Current Load:", load_Current)
        time.sleep(.1)

        ser.flushInput()
        bs = ser.readline()  # Serial port Reading
        decod = (bs).decode('utf-8')  # Response decoding
        js = json.loads(decod.rstrip())  # converting into json
        recv = js["current"]
        print("recv:", recv)

        load_list.append(load_Current)
        recv_list.append(recv)

        # print("Voltage: ", rmt_load.query(":MEASURE:VOLTAGE?").strip())
        # print("Current: ", rmt_load.query(":MEASURE:CURRENT?").strip())
        # print("Power: ", rmt_load.query(":MEASURE:POWER?").strip())

        cur = cur + 0.2

    return load_list, recv_list

def Save(pd_data):
    current_time = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")

    path = f'''{os.getcwd()}/ELOAD_Reports'''
    isdir = os.path.isdir(path)
    if isdir == False:
        os.mkdir(path)
    else:
        pass

    pd_data.to_csv(f'''{path}/Test_{INVolt}V_{current_time}.csv''')

def main():
    run,rmt_load,rmt_rps,ser = Connection()
    time.sleep(2)
    loadlist = []
    recvlist = []
    if run:
        pd_data = pd.DataFrame()
        Initialise_Parameters(rmt_rps,rmt_load)

        for _ in range(sample_rate):
            print("*"*10,"Sample",_+1,"*"*10)
            load,Vo = Read(rmt_load,ser)
            loadlist.append(load)
            recvlist.append(Vo)
        loadlist = loadlist[0]

        pd_data = pd_data.assign(Load=loadlist)
        for i in range(sample_rate):
            header = f'''Vo_{INVolt}V_{i+1}'''
            new_data = {header: recvlist[i]}
            pd_data = pd_data.assign(**new_data)
        print(pd_data)

        Save(pd_data)

        rmt_load.write(":SOURCE:INPUT:STATE Off")
        time.sleep(2)
        rmt_rps.write(":OUTP:STAT CH1,OFF")
    else:
        print("Cannot Connect to RIGOL_DC_ELoad")
if __name__=="__main__":
    main()