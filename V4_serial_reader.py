import time
import serial
import sys
# import openpyxl as xl
# import pandas as pd


def B2I(in_bytes):  # Reconstructs 4 bytes of data into a long int
    value = (in_bytes[0] << 24) | (in_bytes[1] << 16) | (in_bytes[2] << 8) | in_bytes[3]
    return value


ser = serial.Serial('/dev/ttyUSB0', 1000000)  # (Attempt to) open serial port
data = b""
buffer = b""
lastbuffer = b""

try:  # Main code runs here
    print("\033[94m" + "Serial connection opened" + "\033[0m")
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
    DataCount = 0                                                                         # Tracks the number of bytes of raw data per 4 bytes
    IgnoreFlag = 0                                                                        # Tells the program to ignore coincidental terminator symbols
    last_deletion = False

    while True:
        data = ser.read()                                                                 # As data comes in...
        buffer += data                                                                    # Put it into a buffer for temporary storage
        time.sleep(0)

        if buffer.endswith(b"\r\n"):                                                      # Recreating my own "ser.read().strip()" function
            buffer = buffer[:-2]                                                          # Only remove /r or /n if they appear directly next to each other
        if buffer.endswith(b" ") and data != b" " and not last_deletion:
            buffer = buffer[:-1]                                                          # Remove empty space bytes
            DataCount += 1                                                     # Keep track of how many bytes have arrived, since each byte has a space after it
            last_deletion = True

        if DataCount == 5:
            DataCount = 0
            last_deletion = False

        time.sleep(0)

        if DataCount == 1 and (buffer.endswith(b"^T") or buffer.endswith(b"^A") or buffer.endswith(b"^S")):    # And if a terminating message comes in...
            print(buffer)
            SplitData = list(buffer)                                                      # Split up
            if SplitData[0] == 65 and len(SplitData) == 117:                              # Check if it starts with 0x65 (DEC for "A") and make sure all of it is there
                # rawAData = SplitData                                                    # If so, save the data as new, unique variable
                cleanAData = [item for index, item in enumerate(SplitData) if (index + 1) % 5 != 1]
                cleanAData = cleanAData[:-1]
            elif SplitData[0] == 83: #and len(SplitData) == 464:                            # Check for DEC "S"
                # rawSData = SplitData
                cleanSData = [item for index, item in enumerate(SplitData) if (index + 1) % 5 != 1]
                cleanSData = cleanSData[:-1]
            elif SplitData[0] == 84:                                                      # Check for DEC "T"
                # rawTData = SplitData
                cleanTData = [item for index, item in enumerate(SplitData) if (index + 1) % 5 != 1]
                cleanTData = cleanTData[:-1]
            else:
                print("\033[91m" + "Critical Error: Serial data did not begin with 'A', 'S', or 'T' identifier, or had missing bytes" + "\033[0m")
                print("\033[91m" + "Diagnostic data:" + "\033[0m")
                print("\033[91m" + "Last data read:" + "\033[0m")
                print(data)
                print("\033[91m" + "Current Buffer:" + "\033[0m")
                print(buffer)
                print("\033[91m" + "Buffer length:" + "\033[0m")
                print(len(buffer))
                print("\033[91m" + "Data attempted to be written:" + "\033[0m")
                print(SplitData)
                print("\033[91m" + "Last Buffer written:" + "\033[0m")
                print(lastbuffer)
                print("\033[91m" + "DataCount:" + "\033[0m")
                print("\033[91m" + str(DataCount) + "\033[0m")
                print("\033[91m" + "IgnoreFlag:" + "\033[0m")
                print("\033[91m" + str(IgnoreFlag) + "\033[0m")
                if ser.is_open:
                    ser.close()
                    print("\033[94m" + "Serial connection closed" + "\033[0m")
                sys.exit(1)
            lastbuffer = buffer  # For debug, save contents of buffer just in case
            buffer = b""                                                                  # Purge buffer for next set of incoming data
            x += 1
            if x == 3:
                time.sleep(4)  # x seconds
                # print("enter anything to continue")
                # anything = input()
                print("Requesting new data:")
                ser.write(b"\x47")
                x = 0


except KeyboardInterrupt:  # Preventing the KeyboardInterrupt error from being annoying
    print("\033[93m" + "[Keyboard interrupt]" + "\033[0m")
    if ser.is_open:
        ser.close()
        print("\033[94m" + "Serial connection closed" + "\033[0m")
    print("Exiting program" + "\033[0m")
    sys.exit(0)  # Show "success" exit code
