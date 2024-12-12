import customtkinter
from IDE import *
from tkinter import messagebox


def on_closing():
  # Ask the user if they want to close the window
  if (not IDE_instance.welcome and not IDE_instance.flash) and IDE_instance.default_text != IDE_instance.scroll.get(1.0, tk.END)[:-1]:
    if IDE_instance.filepath == None:
      response = msgbox.askyesnocancel("Unsaved File", f"Do you want to save this draft?")
    else:
      response = msgbox.askyesnocancel("Unsaved Changes", f"Do you want to save changes to {os.path.basename(IDE_instance.filepath)}?")
    if response is None:  # Cancel
      return
    elif response:  # Yes, save changes
      IDE_instance.save_file()
  root.destroy()  # Close the window


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

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()