import time
import serial
import sys


def B2I(in_bytes):
    value = (in_bytes[0] <<24) | (in_bytes[1] << 16) | (in_bytes[2] << 8) | in_bytes[3]
    return value


ser = serial.Serial('/dev/ttyUSB0', 1000000)
buffer = b""
data = b""

try:
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
        time.sleep(1)
        ser.write(b"\x47")

        while True:
            data = ser.read().strip()
            buffer += data
            if buffer.endswith(b"^T") or buffer.endswith(b"^A") or buffer.endswith(b"^S"):
                print(buffer)
                buffer = b""
                x = x + 1
                if x == 3:
                    time.sleep(5)
                    print("Requesting new data:")
                    ser.write("\x47")
                    x = 0

except KeyboardInterrupt:
    print("[Keyboard interrupt]")
    if ser.is_open:
        ser.close()
    sys.exit(0)
