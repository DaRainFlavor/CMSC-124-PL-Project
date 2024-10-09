# Passing and accessing values from this state window to other state window should be done by accessing frames in main

import tkinter as tk
from PIL import Image, ImageTk

class FlashWindow(tk.Frame): # Frame 1
  def __init__(self, parent, main):
    # parent is the mainframe from main_window
    # main is the mainWindow class
    super().__init__(parent, background="black")  # put this first Window frame inside the mainframe
    self.parent = parent
    self.main = main

    image_frame = tk.Frame(self, bg="black")
    img = Image.open("logo.jpg")
    image_frame.pack(fill="both", expand=True)

    # Open the image and resize it first
    img = Image.open("logo.jpg")
    resized_img = self.resize_image(img, 500, 300)

    my_img = ImageTk.PhotoImage(resized_img)

    # Create and pack the label
    my_label = tk.Label(image_frame, image=my_img, bg="white") 
    my_label.image = my_img  # Keep a reference to avoid garbage collection
    my_label.pack(fill="both", expand=True)

    # Introduction text
    introduction_message = "A BrainRot compiler developed by Adrian Vaflor, Kimberly Padilla, and Leian Carl Dela Cruz"
    introduction_label = tk.Label(self, text=introduction_message, fg="Black", bg="White", font=("Arial", 8))
    introduction_label.pack()

  def resize_image(self, img, max_width, max_height):
    width, height = img.size
    # Calculate the scaling factor to maintain the aspect ratio
    scaling_factor = min(max_width / width, max_height / height)
    new_width = int(width * scaling_factor)
    new_height = int(height * scaling_factor)
    # Resize the image using the scaling factor
    return img.resize((new_width, new_height))
  
  def switchToNextWindow(self):
    self.main.master.overrideredirect(False)  # Apply to the main window
    self.main.changeWindow("WelcomeWindow")

  def update_display(self):
    pass


  def show(self):
    self.update_display()
    self.parent.configure(bg="white")
    
    # Set the size of the window
    window_width = 500
    window_height = 380

    screen_width = self.main.master.winfo_screenwidth()
    screen_height = self.main.master.winfo_screenheight()

    # Calculate the x and y coordinates for the window to be centered
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    # Set the geometry with the calculated coordinates
    self.main.master.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    self.main.master.overrideredirect(True)  # Apply to the main window

    # self.main.master.resizable(False, False)
    self.place(relx=0.5, rely=0.5, anchor="center")

    self.after(3000, self.switchToNextWindow)