import datetime
import time
import serial
import sys
import os
import openpyxl as xl
# import pandas as pd


def B2I(in_bytes):                                            # Reconstructs 4 bytes of data into a long int
    value = (in_bytes[0] << 24) | (in_bytes[1] << 16) | (in_bytes[2] << 8) | in_bytes[3]
    return value


now = datetime.datetime.now()                                  # Setting up info for timestamping
filename = now.strftime("%Y-%m-%d_%H-%M") + "_data.xlsx"       # Setting up unique filename for exported data

mainWB = xl.Workbook(write_only=True)                          # Create spreadsheet to store data, using write-only mode in case the datasets get big
datasheet = mainWB.create_sheet("Data")                        # Name the sheet we want to work on
# del mainWB["sheet"]                                          # Delete artefact (only need it when not using write_only mode)

n = 0                                                          # Start master index at 0

ser = serial.Serial('/dev/ttyUSB0', 1000000)                   # Open serial port
data = b""
buffer = b""
BadData = False                                                # Initializing variables during startup
Header = False
cleanAData, cleanTData, cleanSData = [], [], []
AirFlowData, refinedAData, refinedTData, refinedSData = [], [], [], []

try:  # Main code runs here
    print("\033[94m" + "Serial connection opened" + "\033[0m")
    while True:
        intro = ser.readline().decode().strip()                # For the 'mirroring' before actual data is coming in, use built-in decoding
        if intro == "Nano Pass-Through ready":
            print(intro)
            break
        else:
            print(intro)
    del intro
    x = 0
    time.sleep(1)
    start_time = time.time()                                                              # Record starting time for data indexing
    ser.write(b"\x47")                                                                    # Request first data set
    current_time = time.time() - start_time
    print("Startup time: " + str(current_time))
    last_time = current_time

    while True:
        data = ser.read()                                                                 # As data comes in, do not apply decoding since everything is meant to be in binary
        buffer += data                                                                    # Put it into a buffer for short-term storage

        if buffer.endswith(b"?????"):                                                     # Check if the Arduino returned an error
            print("\033[91m" + "Warning: Message to Arduino was not recognized" + "\033[0m")
            buffer = b""                                                                  # If so, make sure to reset the buffer
            time.sleep(1)

        if buffer.endswith(b"~~~~~"):                                                     # And if the terminating message comes in...
            SplitData = list(buffer)                                                      # Split up into list items
            if SplitData[0] == 65 and len(SplitData) == 120:                              # Check if it starts with 0x65 (DEC for "A" for airspeed) and make sure all of it is there
                cleanAData = [item for index, item in enumerate(SplitData) if (index + 1) % 5 != 1]
                cleanAData = cleanAData[:-4]                                              # Remove the last remaining bit of the 5-character terminator symbol
                for i in range(0, len(cleanAData), 4):
                    convertedChunk = B2I(cleanAData[i:i+4])
                    refinedAData.append(convertedChunk / 10000)
                print(refinedAData)
                AirFlowData = [airspeed * 0.00112903 for airspeed in refinedAData]        # Spin off a new list for airflow by multiplying by cross-sectional area

            elif SplitData[0] == 83 and len(SplitData) == 470:                            # Check for DEC "S" for smoke data and make sure all of it is there
                cleanSData = [item for index, item in enumerate(SplitData) if (index + 1) % 5 != 1]
                cleanSData = cleanSData[:-4]                                              # Remove the last of the 5-character terminator symbol
                for i in range(0, len(cleanSData), 4):
                    convertedChunk = B2I(cleanSData[i:i+4])
                    refinedSData.append(convertedChunk)
                print(refinedSData)

            elif SplitData[0] == 84 and len(SplitData) == 450:                             # Check for DEC "T" for temperature data and make sure all of it is there
                cleanTData = [item for index, item in enumerate(SplitData) if (index + 1) % 5 != 1]
                cleanTData = cleanTData[:-4]                                              # Remove the last of the 5-character terminator symbol
                for i in range(0, len(cleanTData), 4):
                    convertedChunk = B2I(cleanTData[i:i+4])
                    refinedTData.append(convertedChunk / 10000)
                print(refinedTData)

            else:
                print("\033[93m" + "Warning: Bad serial TX/RX. Suspected bad data set dumped." + "\033[0m")
                BadData = True

            buffer = b""                                                                  # Purge buffer for next set of incoming data
            x += 1
            if x == 3:                                                                    # And after all 3 sets of data have arrived...
                x = 0                                                                     # Reset the count
                current_time = time.time() - start_time                                   # Check the time
                print("Timestamp: " + str(int(current_time)) + " seconds")                # Show timestamp
                print()

                if not Header:                                                                # If this is the first iteration of the loop...
                    HeaderList = ["Time (seconds)"] + ["Airflow (m3/s)" for _ in AirFlowData] + ["Air Velocity (m/s)" for _ in refinedAData] + ["Temperature (C)" for _ in refinedTData] + ["Gas (ppm)" for _ in refinedSData]

                    datasheet.append(HeaderList)
                    Header = True

                if not BadData:                                                           # If the data was accepted, add it to the spreadsheet
                    ExportList = [int(current_time)] + AirFlowData + refinedAData + refinedSData + refinedTData
                    datasheet.append(ExportList)
                BadData = False                                                           # Reset data integrity tracker

                while current_time - last_time < 10:                                      # Regardless of how long it takes data to come in, make sure there is a constant timing
                    time.sleep(0.1)
                    current_time = time.time() - start_time
                last_time = current_time

                refinedAData, refinedTData, refinedSData = [], [], []                     # Make room for new data decoding
                cleanAData, cleanTData, cleanSData = [], [], []
                print("Requesting new data...")
                ser.write(b"\x47")                                                        # Send the "request data" command

        current_time = time.time() - start_time                                           # Update clock
        n += 1                                                                            # At the end of the loop, advance the master index


except KeyboardInterrupt:                                                                 # Gracefully save data and shut down the program instead of crashing
    print("\033[93m" + "[Keyboard interrupt]" + "\033[0m")
    if ser.is_open:
        ser.close()                                                                        # Close the serial connection
        print("\033[94m" + "Serial connection closed" + "\033[0m")
    print("Saving excel file")
    mainWB.save(filename)                                                                  # Save the spreadsheet
    mainWB.close()

    # os.remove("/home/simrigcontrol/PycharmProjects/Arduino-Python_sensor_datalink/" + filename)  # For testing, don't save spreadsheets
    # print("File deleted")

    print("Exiting program")
    sys.exit(0)                                                                            # Show "success" exit code
