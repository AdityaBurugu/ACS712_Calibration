import serial
import json

ser = serial.Serial("COM3", 9600)

# Read line
while True:
    try:
        ser.flush()
        bs = ser.readline()  # Serial port Reading
        decod = (bs).decode('utf-8')  # Response decoding
        js = json.loads(decod.rstrip())  # converting into json
        VO = round(js["current"]/10,2)
        print(VO)
    except(Exception,ser.) as e:
        pass