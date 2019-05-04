import serial
import atexit
from sys import argv


def exit_handler():
    print("Disconnecting from port " + ser.portstr + ".")
    ser.close()


atexit.register(exit_handler)


ser = serial.Serial(port=argv[1], baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS, timeout=0)


print("Connected to port " + ser.portstr + ".")

count = 0
line = []

while ser.readable():
    for c in ser.read():
        line.append(c)
        if c == '\n':
            print(str(count) + "\t" + ''.join(line))
            line = []
            count += 1
            break

# TODO: Read in #sats, lat, lon, ... values (first change arduino code)
