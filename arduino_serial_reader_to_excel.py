import serial
import pandas as pd
import datetime
import matplotlib.pyplot as plt      # Importing Libraries
import sys
import openpyxl as xl

now = datetime.datetime.now()        # Setting up datetime to create unique file name for each test
filename = now.strftime("%Y-%m-%d_%H-%M") + "_data.xlsx"

ser = serial.Serial('COM10', 600)    # Setup for reading the serial communication

prelim = ser.readline().decode().strip()  # Read just the first line of serial for sensor names
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
empty_df = data_df

sensloc = ser.readline().decode().strip()  # Read just the second line of serial for sensor locations
sensloc = sensloc.split(' ')


def format_file():                                               #modify the output .xlsx file to work with Mine_Evacuation.py
    source_workbook = xl.load_workbook("M_E_DataTemplate.xlsx")  #pull in the template
    dupe_workbook = xl.Workbook()                                 #create new spreadsheet to preserve original
    for sheet_name in source_workbook.sheetnames:
        source_sheet = source_workbook[sheet_name]                # Get the source sheet
        new_sheet = dupe_workbook.create_sheet(title=sheet_name)  # Create a new sheet in the new workbook
        for row in source_sheet.iter_rows(values_only=True):      # Copy the values from the source sheet to the new sheet
            new_sheet.append(row)
    s0 = dupe_workbook.get_sheet_by_name('Sheet')
    dupe_workbook.remove_sheet(s0)                                # Get rid of copy operation artefact
    dupe_workbook.save("duplicate.xlsx")                          # Save the new workbook
    source_workbook.close()                                       # Close the original to prevent accidental overwrites

    #wb = xl.load_workbook(filename)
    #ws = wb.active
    #ws.print(['A1'].1)
    #wb.save(now.strftime("%Y-%m-%d_%H-%M") + "_data_out.xlsx")

    dupe_workbook.close()
    #wb.close()
    pass


while True:                                    # Main program loop
    data = ser.readline().decode().strip()     # Continuously pull data from the serial stream
    if data:                                   # Make sure there is something to read
        if "!" in data:                        # Listen for the exit condition from the Arduino
            with pd.ExcelWriter(filename) as writer:
                empty_df.to_excel(writer, sheet_name='Sheet1', index=False, header=False)
                combined_df.to_excel(writer, sheet_name='Sheet2', index=True, header=True, startrow=1, index_label='Timestamp', startcol=1)  # If the condition is met, save the data...
                empty_df.to_excel(writer, sheet_name='Sheet3', index=False, header=False)
                empty_df.to_excel(writer, sheet_name='Sheet4', index=False, header=False)
                print("Data exported as file: " + filename)
            format_file()
            print()
            print("Success!")
            print("Data exported as file: " + filename)  #Then export the file
            sys.exit(0)                                # Then shut down this program

        data = data.split(',')                 # Separate the sensors' data
        del data[-1]                           # Account for the extra comma at the end

        row_data = [float(item[3:]) for item in data]    #put the data into a list, everything from the 8th character on
        combined_df = pd.concat([combined_df, pd.DataFrame([row_data], columns=[prelim])], ignore_index=True)

        plt.figure(1)                          # Set up the data plot
        plt.ion()                              # Enable interactive graph (plot will automatically redraw)
        plt.ylim([-5, 900])                    # Set y-axis bounds
        plt.xlim([n - 500, n + 5])            # Set scrolling x-axis bounds
        plt.plot(combined_df['S01'].iloc[-500:], 'r-', label="Gas Sensor 1")
        plt.plot(combined_df['S02'].iloc[-500:], 'b-', label="Gas Sensor 2")  # Set gas sensor data colors, and
        plt.plot(combined_df['A01'].iloc[-500:]*10, 'g-', label="Airspeed Sensor 1")  # Plot the last 1000 datapoints of each
        plt.title("Sensor Datafeed [2sec delay]")   # Give the user more context
        plt.xlabel("Time (seconds)")
        if n == 0:                                  # Only add one legend, not a new one for each loop
            plt.legend(loc="upper left")
        plt.pause(0.0001)                           # Mandatory pause command
        n += 1                                      # Move master index forward
