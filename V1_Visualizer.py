
def start():
    import openpyxl as xl
    import tkinter as tk
    from tkinter import messagebox, ttk
    from PIL import Image, ImageTk
    import numpy as np

    def on_button_click(index):
        # Retrieve the corresponding row from the 97x3 array using the button's index
        values = array_97x3[index]

        # Update the text_label to display the three values in the bottom right corner of the image
        text_label.config(text=str(values))

    # Function to handle radio button selection
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
            # global array_97x3
            global selected_option
            try:
                value = array_97x3[index, (selected_option - 1), 0]
            except NameError:
                value = array_97x3[index, 2, 0]

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
            # root.quit()
        root.quit()

    def close_and_reopen():
        # Clear previous data
        text_label.config(text=str(""))

        # Update the 97x3 array from an outside source (here, we're simulating with random values)
        update_array()
        update_button_colors()
        # root.after(5, root.deiconify)
        root.deiconify()

    def update_array():
        # Update the 97x3 array with random values (simulate from an outside source)
        global array_97x3
        appArray = np.random.randint(0, 100, size=(97, 3, 1))
        global HISTArray_97x3
        HISTArray_97x3 = np.dstack((array_97x3, appArray))  # Keep a history of previous data
        array_97x3 = appArray                               # Redefine array with new data

    def value_to_color(value):
        # Map a value to a specific color
        if value < 20:
            return "red"
        elif value < 50:
            return "yellow"
        else:
            return "green"

    # Create the main application window
    root = tk.Tk()
    root.title("Image with Buttons")

    # Lock the window size to prevent resizing
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

    # Initialize a 97x3 array with random values (replace with your data as needed)
    global array_97x3
    array_97x3 = np.random.randint(0, 100, size=(97, 3, 1))

    # Create buttons and place them on the image in a grid
    buttons = []
    num_buttons = 97
    grid_rows = 10
    grid_cols = 10

    # Loop through rows and columns to create the 97 buttons
    for index in range(num_buttons):
        # Calculate the row and column of the button
        row = index // grid_cols
        col = index % grid_cols

        # Create a button and set its command to the `on_button_click` function
        button = tk.Button(
            root,
            text=str(index + 1),
            command=lambda idx=index: on_button_click(idx),
            width=5,
            height=2,
            bg="gray",  # Buttons start as grayed out to show no dataset selected
            fg="black"
        )

        # Place the button on the image using a grid layout
        button.place(x=50 + col * 50, y=50 + row * 50)  # Adjust button positions as needed
        buttons.append(button)

    # Create a frame to hold buttons and listbox on the right side
    frame = tk.Frame(root)
    frame.pack(side=tk.RIGHT, fill=tk.Y)

    # Create a listbox for selecting values with custom colors and fonts
    listbox_bg_color = "#36454F"  # Charcoal gray
    listbox_fg_color = "#D3D3D3"  # Light gray
    listbox_font = ("Arial", 14)

    listbox = tk.Listbox(
        frame,
        height=5,
        font=listbox_font,
        bg=listbox_bg_color,
        fg=listbox_fg_color
    )
    listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Populate the listbox with the names of the sets of values
    for i in range(1, array_97x3.shape[2]):
        listbox.insert(tk.END, f"Set {i}")

    # Create a scrollbar and attach it to the listbox
    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)

    # Bind the listbox selection event
    listbox.bind("<<ListboxSelect>>", on_listbox_select)

    # Create a frame for the "close and reopen" and "exit" buttons
    button_frame = tk.Frame(frame)
    button_frame.pack(side=tk.BOTTOM, fill=tk.X)

    # Create the "close and reopen" button and place it above the "exit" button
    reopen_button = tk.Button(
        button_frame,
        text="Reload Data",
        command=close_and_reopen,
        bg="blue",
        fg="white"
    )
    reopen_button.pack(fill=tk.X, padx=5, pady=10)

    # Create the "exit" button and place it below the "close and reopen" button
    exit_button = tk.Button(
        button_frame,
        text="Exit",
        command=confirm_exit,
        bg="red",
        fg="white"
    )
    exit_button.pack(fill=tk.X, padx=5, pady=5)

    # Create a label to display text in the bottom right corner of the image
    text_label = tk.Label(root, text="", font=("Arial", 14), bg="white")
    text_label.place(relx=0.80, rely=1.0, anchor="se")

    update_button_colors()

    # Start the Tkinter event loop
    root.mainloop()

    print("Done")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    start()
