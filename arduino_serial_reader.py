import serial
import pandas as pd
import datetime
import matplotlib.pyplot as plt      # Importing Libraries
import sys

now = datetime.datetime.now()        # Setting up datetime to create unique file name for each test
filename = now.strftime("%Y-%m-%d_%H-%M") + "_data.csv"

ser = serial.Serial('COM10', 600)    # Setup for reading the serial communication

prelim = ser.readline().decode().strip()  # Read just the first line of serial
prelim = prelim.split(' ')                # Put the sensor ID's sent by the Arduino into a list
senslen = len(prelim)                     # Figure out the number of active sensors
for i in range(senslen):                  # Pull out the sensor IDs from the list
    exec(f"{prelim[i]} = {0}")
del i                                     # Clean up unneeded variable

n = 0                                     # Start master index at zero

data_df = pd.DataFrame(columns=[prelim])  # Start up the dataframes
row_data = [0] * len(prelim)
new_df = pd.DataFrame([row_data], columns=[prelim])
combined_df = pd.DataFrame(columns=[prelim])
data_df.loc[0] = [0] * len(prelim)

while True:                                    # Main program loop
    data = ser.readline().decode().strip()     # Continuously pull data from the serial stream
    if data:                                   # Make sure there is something to read
        if "!" in data:                        # Listen for the exit condition from the Arduino
            combined_df.to_csv(filename, index=False)  # If the condition is met, save the data...
            print()
            print("Success!")
            print("Data exported as file: " + filename)
            sys.exit(0)                                # Then shut down the program

        data = data.split(',')                 # Separate the sensors' data
        del data[-1]                           # Account for the extra comma at the end

        row_data = [float(item[3:]) for item in data]    #put the data into a list
        combined_df = pd.concat([combined_df, pd.DataFrame([row_data], columns=[prelim])], ignore_index=True)

        plt.figure(1)                          # Set up the data plot
        plt.ion()                              # Enable interactive graph (plot will automatically redraw)
        plt.ylim([-5, 900])                    # Set y-axis bounds
        plt.xlim([n - 1000, n + 5])            # Set scrolling x-axis bounds
        plt.plot(combined_df['S01'].iloc[-1000:], 'r-', label="Gas Sensor 1")
        plt.plot(combined_df['S02'].iloc[-1000:], 'b-', label="Gas Sensor 2")  # Set gas sensor data colors, and
        plt.plot(combined_df['A01'].iloc[-1000:]*10, 'g-', label="Airspeed Sensor 1")  # Plot the last 1000 datapoints of each
        plt.title("Sensor Datafeed [2sec delay]")   # Give the user more context
        if n == 0:                                  # Only add one legend, not a new one for each loop
            plt.legend(loc="upper left")
        plt.pause(0.00001)                          # Mandatory pause command
        n += 1                                      # Move master index forward
