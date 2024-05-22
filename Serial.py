import serial
import json

try:
    ser = serial.Serial("COM3", 9600)
except(Exception,serial.SerialException) as e:
    ser=None
    print(str(e).split(":")[0])
# Read line
while True:
    if ser!=None:
        ser.flush()
        bs = ser.readline()  # Serial port Reading
        decod = (bs).decode('utf-8')  # Response decoding
        js = json.loads(decod.rstrip())  # converting into json
        VO = round(js["current"]/10,2)
        print(VO)
    else:
        break