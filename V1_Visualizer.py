import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk


def on_button_click(text):
    # Display a message box with the specified text when the button is clicked
    messagebox.showinfo("Information", text)


# Create the main application window
root = tk.Tk()
root.title("Image with Buttons")

# Load the image using PIL (Pillow) and convert it to a PhotoImage object
image_path = "ref.bmp"  # Replace with your image path
image = Image.open(image_path)
photo = ImageTk.PhotoImage(image)

# Create a label to display the image
image_label = tk.Label(root, image=photo)
image_label.pack()

# Create buttons and place them on the image
button_texts = ["Button 1", "Button 2", "Button 3", "Button 4"]
button_texts_texts = ["Text 1", "Text 2", "Text 3", "Text for button number 4"]
button_positions = [(50, 50), (150, 100), (250, 150), (0,0)]  # Coordinates for buttons (x, y)

# Create buttons and add them to the image
for text, btn_text, pos in zip(button_texts, button_texts_texts, button_positions):
    button = tk.Button(
        root,
        text=text,
        command=lambda btn_text=btn_text: on_button_click(btn_text),
        width=10,  # Change button width
        height=2,  # Change button height
        bg="lightblue",  # Change button background color
        fg="black"  # Change button foreground (text) color
    )
    button.place(x=pos[0], y=pos[1])

# Start the Tkinter event loop
root.mainloop()
