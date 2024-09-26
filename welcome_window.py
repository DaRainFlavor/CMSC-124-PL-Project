import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import customtkinter 
from PIL import ImageTk, Image 

class WelcomeWindow(tk.Frame):
    def __init__(self, parent, main):
        super().__init__(parent, bg="white")
        self.main = main

        

        # Configure the column and row for resizing
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        frame = tk.Frame(self, relief=tk.RAISED, bd=2)

        # Load the images
        open_image = ImageTk.PhotoImage(Image.open("open_image.png").resize((40, 40)))  # Replace with actual image paths
        new_image = ImageTk.PhotoImage(Image.open("new_image.png").resize((40, 40)))

        # Create image buttons
        open_button = customtkinter.CTkButton(frame, image=open_image, text="", command=self.open_file, corner_radius=32, fg_color="White")
        new_button = customtkinter.CTkButton(frame, image=new_image, text="", command=self.new_file, corner_radius=32, fg_color="White")

        # Sticky fills the contents in directions: northsouth, eastwest
        open_button.grid(row=0, column=0, padx=5, pady=5, sticky="ns")
        new_button.grid(row=0, column=1, padx=5, pady=5, sticky="ns")
        frame.grid(row=0, column=0, sticky="ew", columnspan=2)

        welcome_message = "Welcome to Compiley Studio!"
        welcome_label = tk.Label(self, text=welcome_message, fg="Black", bg="White", font=("Arial", 40))
        welcome_label.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky='nsew')

        self.pack(expand=True, fill=tk.BOTH)  # maintain this to totally overlap the previous window

        # Bind keyboard shortcuts using lambda functions
        self.main.master.bind_all("<Control-s>", lambda event: self.save_file())
        self.main.master.bind_all("<Control-S>", lambda event: self.save_as_file())
        self.main.master.bind_all("<Control-o>", lambda event: self.open_file())
        self.main.master.bind_all("<Control-n>", lambda event: self.new_file())

        # Store references to images to prevent them from being garbage collected
        self.open_image = open_image
        self.new_image = new_image

    def switchToNextWindow(self, path):
        code_window = self.main.frames["CodeWindow"]
        code_window.filepath = path
        code_window.text_edit.delete("1.0", tk.END)  # Clear existing content
        with open(path, "r") as f:
          code_window.default_text = f.read()
          code_window.text_edit.insert("1.0", code_window.default_text)  # Insert the default text
          code_window.text_edit.mark_set(tk.INSERT, tk.END)
          code_window.text_edit.see(tk.END)
        self.main.changeWindow("CodeWindow")

    def open_file(self):
        path = askopenfilename(filetypes=[("BrainRot File", "*.rot")])
        if not path:
          return
        self.switchToNextWindow(path)

    def new_file(self):
        # Open the save file dialog with a default filename
        path = asksaveasfilename(
          defaultextension=".rot",  # Set .rot as the default extension
          filetypes=[("BrainRot File", "*.rot")],  # Only show .rot files
          initialfile="new_file.rot"  # Default filename
        )
    
        # If the user cancels the dialog, path will be an empty string
        if not path:
          return
    
        # Create a blank file at the specified path
        with open(path, "w") as f:
          pass  # Just create an empty file

        self.switchToNextWindow(path)

    def restore_down(self):
        self.main.master.geometry("400x400")

    def show(self):
        self.main.master.state('zoomed')
        self.main.master.after(1000, self.restore_down)
        self.main.master.resizable(True, True)
        self.pack(expand=True, fill=tk.BOTH) # maintain this to totally overlap the previous window