import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.tix import *
import customtkinter 
from PIL import ImageTk, Image
from tooltip import ToolTip

class WelcomeWindow(tk.Frame):
    def __init__(self, parent, main):
        super().__init__(parent, bg="white")
        self.main = main

        # Configure the column and row for resizing
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        frame = tk.Frame(self, relief=tk.RAISED, bd=2)

        save_as_image = customtkinter.CTkImage(Image.open("save_as_image.png").resize((40, 40)))
        save_image = customtkinter.CTkImage(Image.open("save_image.png").resize((40, 40)))
        open_image = customtkinter.CTkImage(Image.open("open_image.png").resize((40, 40)))
        new_image = customtkinter.CTkImage(Image.open("new_image.png").resize((40, 40)))
        undo_image = customtkinter.CTkImage(Image.open("undo_image.png").resize((40, 40)))
        redo_image = customtkinter.CTkImage(Image.open("redo_image.png").resize((40, 40)))
        cut_image = customtkinter.CTkImage(Image.open("cut_image.png").resize((40, 40)))
        paste_image = customtkinter.CTkImage(Image.open("paste_image.png").resize((40, 40)))
        run_image = customtkinter.CTkImage(Image.open("run_image.png").resize((40, 40)))


        # Create image buttons
        save_as_button = customtkinter.CTkButton(frame, image=save_as_image, text="", corner_radius=32, fg_color="#DDDCDD", state=tk.DISABLED, width = 45, height=45)
        self.save_button = customtkinter.CTkButton(frame, image=save_image, text="", corner_radius=32, fg_color="#DDDCDD", state=tk.DISABLED, width = 45, height=45)
        open_button = customtkinter.CTkButton(frame, image=open_image, text="", command=self.open_file, corner_radius=32, fg_color="White", width = 45, height=45)
        new_button = customtkinter.CTkButton(frame, image=new_image, text="", command=self.new_file, corner_radius=32, fg_color="White", width = 45, height=45)
        self.undo_button = customtkinter.CTkButton(frame, image=undo_image, text="", corner_radius=32, fg_color="#DDDCDD", state=tk.DISABLED, width = 45, height=45)
        self.redo_button = customtkinter.CTkButton(frame, image=redo_image, text="", corner_radius=32, fg_color="#DDDCDD", state=tk.DISABLED, width = 45, height=45)
        self.cut_button = customtkinter.CTkButton(frame, image=cut_image, text="", corner_radius=32, fg_color="#DDDCDD", state=tk.DISABLED, width = 45, height=45)
        self.paste_button = customtkinter.CTkButton(frame, image=paste_image, text="", corner_radius=32, fg_color="#DDDCDD", state=tk.DISABLED, width = 45, height=45)
        run_button = customtkinter.CTkButton(frame, image=run_image, text="", corner_radius=32, fg_color="#DDDCDD", state=tk.DISABLED, width = 45, height=45)

        # Sticky fills the contents in directions: northsouth, eastwest
        save_as_button.grid(row=0, column=0, padx=5, pady=5, sticky="ns")
        self.save_button.grid(row=0, column=1, padx=5, pady=5, sticky="ns")
        open_button.grid(row=0, column=2, padx=5, pady=5, sticky="ns")
        new_button.grid(row=0, column=3, padx=5, pady=5, sticky="ns")


        # Apply tooltips to the buttons
        ToolTip(save_as_button, "Save As")
        ToolTip(self.save_button, "Save")
        ToolTip(open_button, "Open")
        ToolTip(new_button, "New")
        ToolTip(self.undo_button, "Undo")
        ToolTip(self.redo_button, "Redo")
        ToolTip(self.cut_button, "Cut")
        ToolTip(self.paste_button, "Paste")
        ToolTip(run_button, "Run")

        # Create an empty column that will expand
        frame.grid_columnconfigure(4, weight=1)

        # Place the Run button on the far right
        self.undo_button.grid(row=0, column=5, padx=5, pady=5, sticky="ns")
        self.redo_button.grid(row=0, column=6, padx=5, pady=5, sticky="ns")
        self.cut_button.grid(row=0, column=7, padx=5, pady=5, sticky="ns")
        self.paste_button.grid(row=0, column=8, padx=5, pady=5, sticky="ns")
        run_button.grid(row=0, column=9, padx=5, pady=5, sticky="ns")
        frame.grid(row=0, column=0, sticky="ew", columnspan=2)

        frame2 = tk.Frame(self, relief=tk.RAISED, background="white")
        frame2.columnconfigure(0, weight=1)  # Allow column to expand
        frame2.rowconfigure(0, weight=1)      # Allow row for welcome label to expand
        frame2.rowconfigure(1, weight=1)      # Allow row for introduction label to expand

        welcome_message = "Welcome to Compiley Studio!"
        welcome_label = tk.Label(frame2, text=welcome_message, fg="Black", bg="White", font=("Arial", 40))
        welcome_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        intro_message = "A compiler for BrainRot files."
        intro_label = tk.Label(frame2, text=intro_message, fg="Black", bg="White", font=("Arial", 12))
        intro_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))

        frame2.grid(row=1, column=0, sticky="ew", columnspan=2)
        
        self.pack(expand=True, fill=tk.BOTH)  # maintain this to totally overlap the previous window

        # Bind keyboard shortcuts using lambda functions
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
        self.main.master.geometry("1055x400")

    def show(self):
        self.main.master.state('zoomed')
        self.main.master.after(1000, self.restore_down)
        self.main.master.resizable(True, True)
        self.pack(expand=True, fill=tk.BOTH) # maintain this to totally overlap the previous window