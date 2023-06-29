import serial
import pandas as pd
import datetime
import matplotlib.pyplot as plt      # Importing Libraries
import sys
import os
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

sensloc = ser.readline().decode().strip()  # Read just the second line of serial for sensor locations
sensloc = sensloc.split(' ')

n = 0                                     # Start master index at zero

data_df = pd.DataFrame(columns=[prelim])                          # Start up dataframe
data_df.loc[0] = [0] * len(prelim)                                # Temporarily fill with zeros
row_data = [0] * len(prelim)                                      # Create list to contain each second's data
combined_df = pd.DataFrame(columns=[prelim])                      # Start up master dataframe to hold all data
empty_df = data_df                                                # Dataframe of just zeros


def format_file():                                                # Modify the output .xlsx file to work with Mine_Evacuation.py

    data_workbook = xl.load_workbook(filename)
    wsedit = data_workbook['Sheet2']
    for q, value in enumerate(sensloc):
        cell = wsedit.cell(row=3, column=3 + q)
        cell.value = value
    del q

    data_workbook.save(filename + "mod.xlsx")
    os.remove("C:\\Users\\Sean\\PycharmProjects\\Gas sensor\\" + filename)  #clean up unneeded file

    source_workbook = xl.load_workbook("M_E_DataTemplate.xlsx")   # Pull in the template
    dupe_workbook = xl.Workbook()                                 # Create new spreadsheet to preserve original
    for sheet_name in source_workbook.sheetnames:
        source_sheet = source_workbook[sheet_name]                # Get the source sheet
        new_sheet = dupe_workbook.create_sheet(title=sheet_name)  # Create a new sheet in the new workbook
        for row in source_sheet.iter_rows(values_only=True):      # Copy the values from the source sheet to the new sheet
            new_sheet.append(row)
        del row
    del sheet_name
    del dupe_workbook['Sheet']                                    # Get rid of copy operation artefact
    source_workbook.close()                                       # Close the original to prevent accidental overwrites

    datalen = len(combined_df.columns)
    ws2edit = dupe_workbook['Sheet2']
    ws2edit.delete_rows(5, 13)                                    # Clear out the example data
    for row in range(5, 5 + datalen):
        for column in range(2, 199 + 1):
            cell = ws2edit.cell(row=row, column=column)
            cell.value = 0                                        # Put in zeros to fill any would-be empty cells
    for w in range(datalen):
        ws2edit.cell(row=w + 5, column=1).value = w               # Copy the new index
    del w
    '''
    #read_row = []
    for column in range(35, 67):
        cell = ws2edit[chr(column) + str(3)]
        if cell.value is not None:
            row_data.append(int(cell.value))
    for item in read_row:
        if any(item in sensloc for item in read_row):'''

    dupe_workbook.save("duplicate.xlsx")                          # Save the new workbook

    dupe_workbook.close()
    return


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
            print("Data exported as file: " + filename)  # Then export the file
            sys.exit(0)                                  # Then shut down this program

        data = data.split(',')                 # Separate the sensors' data
        del data[-1]                           # Account for the extra comma at the end

        row_data = [float(item[3:]) for item in data]    #put the data into a list, everything from the 8th character on
        combined_df = pd.concat([combined_df, pd.DataFrame([row_data], columns=[prelim])], ignore_index=True)

        plt.figure(1)                          # Set up the data plot
        plt.ion()                              # Enable interactive graph (plot will automatically redraw)
        plt.ylim([-5, 900])                    # Set y-axis bounds
        plt.xlim([n - 500, n + 5])             # Set scrolling x-axis bounds
        plt.plot(combined_df['S01'].iloc[-500:], 'r-', label="Gas Sensor 1")
        plt.plot(combined_df['S02'].iloc[-500:], 'b-', label="Gas Sensor 2")  # Set gas sensor data colors, and
        plt.plot(combined_df['A01'].iloc[-500:]*10, 'g-', label="Airspeed Sensor 1")  # Plot the last 1000 datapoints of each
        plt.title("Sensor Datafeed [2sec delay]")   # Give the user more context
        plt.xlabel("Time (seconds)")
        if n == 0:                                  # Only add one legend, not a new one for each loop
            plt.legend(loc="upper left")
        plt.pause(0.0001)                           # Mandatory pause command
        n += 1                                      # Move master index forward
