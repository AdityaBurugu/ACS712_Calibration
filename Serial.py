import serial
import json

ser = serial.Serial("COM3", 9600)

# Read line
while True:
    bs = ser.readline()
    data = (bs).decode('utf-8')
    js = json.loads(data.rstrip())
    print(js["current"])