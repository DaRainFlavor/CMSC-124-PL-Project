import customtkinter
from IDE import *


customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("dark-blue")

# setup
root = customtkinter.CTk()
root.title("Compiley Studio")
root.iconbitmap("icon.ico")

# create frames
itemFrame = customtkinter.CTkFrame(master=root)
itemFrame.grid(row=0, column=0, sticky = "nsew")

# Configure root to expand
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

IDE_instance = IDE(itemFrame, root)

root.mainloop()
