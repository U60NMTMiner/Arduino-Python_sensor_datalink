import time
import serial
import sys
# import openpyxl as xl
# import pandas as pd


def B2I(in_bytes):  # Reconstructs 4 bytes of data into a long int
    value = (in_bytes[0] << 24) | (in_bytes[1] << 16) | (in_bytes[2] << 8) | in_bytes[3]
    return value


ser = serial.Serial('/dev/ttyUSB0', 1000000)  # (Attempt to) open serial port
buffer = b""
data = b""
terminator = b"^T"

try:  # Main code runs here
    print("Serial port connected")
    while True:
        intro = ser.readline().decode().strip()
        if intro == "Nano Pass-Through ready":
            print(intro)
            break
        else:
            print(intro)
    del intro
    x = 0
    time.sleep(2)
    ser.write(b"\x47")

    while True:
        data = ser.read().strip()
        buffer += data
        if buffer.endswith(b"^T") or buffer.endswith(b"^A") or buffer.endswith(b"^S"):
            print(buffer)
            buffer = b""
            x = x + 1
            if x == 3:
                # time.sleep(5)  # x seconds
                print("enter anything to continue")
                anything = input()
                print("Requesting new data:")
                ser.write(b"\x47")
                x = 0


except KeyboardInterrupt:  # Preventing the KeyboardInterrupt error from being annoying
    print("[Keyboard interrupt]")
    if ser.is_open:
        ser.close()
        print("Serial connection closed")
    print("Exiting program")
    sys.exit(0)  # Show "success" exit code
