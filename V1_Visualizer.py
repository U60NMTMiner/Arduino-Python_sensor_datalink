
def linspace(a, b, n):
    if n < 2:
        return b
    diff = (float(b) - a)/(n - 1)
    return [diff * i + a for i in range(n)]


def start():
    import openpyxl as xl
    import tkinter as tk
    from tkinter import messagebox, ttk
    from PIL import Image, ImageTk
    #import numpy as np
    import Modules.functions as func
    import os.path
    import tkinter.messagebox
    import time

    # Pull in the config file
    config = func.open_file("config")

    def on_button_click(index):
        # Retrieve the corresponding row from the 97x3 array using the button's index
        global DataArray
        values = DataArray[index]

        # Update the text_label to display the three values in the bottom right corner of the image
        text_label.config(text=str(values))

    # Function to handle radio button selection
    global selected_option
    selected_option = 3

    def on_option_selected():
        global selected_option
        selected_option = radio_var.get()
        update_button_colors()
        root.deiconify()
        # print(f"Selected option: {selected_option}")

    def update_button_colors():
        # Update the colors of all buttons based on their corresponding values from `array_97x3`
        for index, button in enumerate(buttons):
            try:
                value = DataArray[index][selected_option - 1]  # Normally, use the selected option
            except NameError:
                value = DataArray[index][2]  # On first start, no option has yet been registered

            # Map the average value to a color using `value_to_color`
            color = value_to_color(value)

            # Set the background color of the button based on the color
            button.config(bg=color)

    def on_listbox_select(event):
        # Handle listbox selection changes
        selected_index = listbox.curselection()
        if selected_index:
            selected_set = listbox.get(selected_index)
            # Convert the selected set to an integer
            selected_set_index = int(selected_set.replace("Set ", "")) - 1

            # Update the button colors based on the selected set
            update_button_colors()

            # Update the title of the application window
            root.title(f"Image with Buttons - {selected_set}")

    def confirm_exit():
        # Show a confirmation dialog asking if the user wants to quit
        # if messagebox.askyesno("Confirm Exit", "Are you sure you want to quit?"):
        root.quit()

    def close_and_reopen():
        # Clear previous data
        text_label.config(text=str(""))

        # Update the data array from an outside source
        update_array_prime()    # Pull in new data
        update_button_colors()  # Update button colors
        root.deiconify()        # Update the buttons

    def update_array_prime():
        # Update the 97x3 array with values from a spreadsheet
        SpSheet = inputtxt.get()  # Request spreadsheet name from user
        while (not os.path.exists(SpSheet)) and (SpSheet[-4:] != ".xlsx"):  # Check for valid spreadsheet
            tkinter.messagebox.showerror(title="Error",
                                         message="File not found, enter name of data spreadsheet."
                                                 "\n\rUse .xlsx files only")
            inputtxt.delete(0, 'end')   # Clear text entry
            return                      # Don't load a spreadsheet that doesn't exist
        wb = xl.load_workbook(SpSheet)  # If the spreadsheet is valid, load spreadsheet
        sheet = wb["Data"]
        maxCol = sheet.max_column - 2   # For some reason, there are two unassigned coordinates hanging off the end
        maxRow = sheet.max_row
        print("Accessed workbook: ", SpSheet)
        root.title(SpSheet)

        global coordLock
        global HeaderData
        global IdxHeaderDict

        if coordLock == 0:  # Pull the headers from the relevant columns to use later
            HeaderData = []
            for value in sheet.iter_cols(min_col=25, max_col=maxCol, min_row=2, values_only=True):
                HeaderData.append(value[0])

        if maxCol == 220:  # Make sure the row of data is complete
            RowData = []
            for value in sheet.iter_cols(min_col=25, max_col=maxCol, min_row=maxRow, values_only=True):
                RowData.append(value[0])

            AirVel = RowData[:23]         # 23 air velocity sensors
            AirVel = tuple(zip(AirVel, config["Airspeed_Sensor_Coordinates"]))
            #AirVel = list(AirVel)
            #while len(AirVel) < 90:
            #    AirVel.append(("None", ""))
            #AirVel = tuple(AirVel)

            TemVal = RowData[23:(23+90)]  # 89 temperature sensors
            TemVal = tuple(zip(TemVal, config["Temperature_Sensor_Coordinates"]))
            #TemVal = list(TemVal)
            #while len(TemVal) < 90:
            #    TemVal.append(("None", ""))
            #TemVal = tuple(TemVal)

            GasVal = RowData[(23+90):]    # 84 gas sensors
            GasVal = tuple(zip(GasVal, config["Gas_Sensor_Coordinates"]))
            #GasVal = list(GasVal)
            #while len(GasVal) < 90:
            #    GasVal.append(("None", ""))
            #GasVal = tuple(GasVal)

            wb.close()  # Don't keep the spreadsheet open when it's not needed

            # Create a dictionary to hold the combined data
            combined_dict = {}

            # Function to populate the dictionary with data
            def populate_dict(data_list, index):
                for data, coord in data_list:
                    if coord not in combined_dict:
                        combined_dict[coord] = [None, None, None, coord]
                    combined_dict[coord][index] = data

            # Populate the dictionary from each list
            populate_dict(AirVel, 0)
            populate_dict(TemVal, 1)
            populate_dict(GasVal, 2)

            # Convert the dictionary to a list of tuples
            appArray = [tuple(values) for values in combined_dict.values()]

            global DataArray
            #appArray = list(zip(AirVel, TemVal, GasVal))

            # Keep a history of previous data
            global HistArray
            global arrLock
            try:
                if len(HistArray) == 89 and arrLock == 0:
                    HistArray = [HistArray, appArray]
                    arrLock = 1
                else:
                    HistArray.append(appArray)
            except NameError:
                HistArray = appArray     # If this is the first iteration, nothing to extend on
            DataArray = appArray         # Save the new data to the DataArray

            # Splice the coordinates of each sensor into the DataArray
            #DataArray = [(tup[0], tup[1], tup[2], tup2[1]) for tup, tup2 in zip(DataArray, Coordinate_Transform)]

            # Rearrange the DataArray so that the datapoints are in the correct order relative to the button indexes
            DataDict = {coordinate: (data1, data2, data3, coordinate) for data1, data2, data3, coordinate in DataArray}
            DataArray = [DataDict[coordinate] for _, coordinate in Coordinate_Transform]
            DataArray = DataArray

        else:
            wb.close()
            tkinter.messagebox.showerror(title="Error", message="Spreadsheet row contains invalid data")

    def value_to_color(value):
        if value is None or value == "None":
            return "gray"
        elif value < 20:
            return "red"
        elif value < 50:
            return "yellow"
        else:
            return "green"

    ####################################################################################################
    ###  First-run setup  ###

    # Create the main application window
    root = tk.Tk()
    root.title("Simulation Rig Data visualization")

    # Lock the window to prevent resizing
    root.resizable(False, False)

    # Create a variable to hold the value of the selected radio button
    radio_var = tk.IntVar()
    radio_var.set(3)  # Default to gas concentrations
    radio_frame = tk.Frame(root)
    radio_frame.pack(side="bottom")

    # Create three radio buttons
    radio1 = tk.Radiobutton(radio_frame, bg="gray", font="14", text="Air Velocity (m/s)", variable=radio_var, value=1, command=on_option_selected)
    radio1.pack(side="left", padx=5, pady=1)
    radio2 = tk.Radiobutton(radio_frame, bg="gray", font="14", text="Temperature (deg C)", variable=radio_var, value=2, command=on_option_selected)
    radio2.pack(side="left", padx=5, pady=1)
    radio3 = tk.Radiobutton(radio_frame, bg="gray", font="14", text="Gas Concentration (approx. ppm)", variable=radio_var, value=3, command=on_option_selected)
    radio3.pack(side="left", padx=5, pady=1)

    # Load the image using PIL (Pillow) and convert it to a PhotoImage object
    image_path = "Sensor_layout.png"  # Use the reference image path
    image = Image.open(image_path)
    photo = ImageTk.PhotoImage(image)

    # Create a label to display the image
    image_label = tk.Label(root, image=photo)
    image_label.pack(side=tk.LEFT)

    # Initialize an empty array so the program doesn't error out when first starting
    global DataArray
    DataArray = []

    # Set up the key to translate between node index and coordinate
    Coordinate_Transform = []
    counter = 1
    for item in config['Button_Coordinates']:
        Coordinate_Transform.append([counter, item[2]])
        counter += 1
    del counter

    # Set up data storage
    global arrLock
    global coordLock
    arrLock = 0      # Used to kickstart the HistArray data storage
    coordLock = 0    # Used to figure out what order

    # Place all the buttons on the image
    buttons = []
    indx = 0
    for pos in enumerate(config['Button_Coordinates']):
        altbutton = tk.Button(                               # Define button properties
            root,
            text=str(indx),
            command=lambda idx=indx: on_button_click(idx),
            width=2,
            height=1,
            bg="gray",
            fg="black"
        )
        altbutton.place(x=int(pos[1][1]), y=int(pos[1][0]))  # Place the button using pixel coordinates (from top left)
        buttons.append(altbutton)                            # Add the new button to the list of existing buttons
        indx += 1

    # Create a frame to hold buttons and listbox on the right side
    ListFrame = tk.Frame(root)
    ListFrame.pack(side=tk.RIGHT, fill=tk.Y)

    # Create a listbox and define properties
    listbox_bg_color = "#36454F"  # Charcoal gray
    listbox_fg_color = "#D3D3D3"  # Light gray
    listbox_font = ("Arial", 14)
    listbox = tk.Listbox(
        ListFrame,
        height=5,
        font=listbox_font,
        bg=listbox_bg_color,
        fg=listbox_fg_color
    )
    listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Create a scrollbar and attach it to the listbox
    scrollbar = ttk.Scrollbar(ListFrame, orient=tk.VERTICAL, command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)

    # Bind the listbox selection event
    listbox.bind("<<ListboxSelect>>", on_listbox_select)

    # Create a frame for the "close and reopen" and "exit" buttons
    ButtonFrame = tk.Frame(ListFrame)
    ButtonFrame.pack(side=tk.BOTTOM, fill=tk.X)

    # Ask where to get spreadsheet from
    inputtxtlabel = tk.Label(ButtonFrame, text="Enter name of spreadsheet:", font="Arial, 12")
    inputtxtlabel.pack(fill=tk.X)
    inputtxt = tk.Entry(ButtonFrame, font="Arial, 12", bg="white")
    inputtxt.pack(fill=tk.X)

    # Create the "close and reopen" button and place it above the "exit" button
    reopen_button = tk.Button(
        ButtonFrame,
        text="Reload Data",
        command=close_and_reopen,
        bg="blue",
        fg="white"
    )
    reopen_button.pack(fill=tk.X, padx=5, pady=10)

    # Create the "exit" button and place it below the "close and reopen" button
    exit_button = tk.Button(
        ButtonFrame,
        text="Exit",
        command=confirm_exit,
        bg="red",
        fg="white"
    )
    exit_button.pack(fill=tk.X, padx=5, pady=5)

    # Create a label to display text in the bottom right corner of the image
    text_label = tk.Label(root, text="", font=("Arial", 14), bg="white")
    text_label.place(relx=0.80, rely=0.9, anchor="se")

    # Start the Tkinter event loop
    root.mainloop()
    print("Done")


if __name__ == '__main__':
    start()
