import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import tkinter.messagebox as msgbox
import os

class CodeWindow(tk.Frame):
  def __init__(self, parent, main):
    super().__init__(parent, bg="white")
    self.main = main
    self.filepath = False

    # Configure the column and row for resizing
    self.rowconfigure(1, weight=1)
    self.columnconfigure(0, weight=1)

    self.default_text = ""
    self.text_edit = tk.Text(self, font="Helvetica 11", wrap="word", undo = True)
    self.text_edit.insert("1.0", self.default_text)
    self.text_edit.grid(row=1, column=0, sticky="nsew")
    # Set cursor to the end of the default text
    self.text_edit.mark_set(tk.INSERT, tk.END)
    self.text_edit.see(tk.END)

    # Set focus to the text widget so the cursor is active
    self.text_edit.focus_set()

    scroll_bar = tk.Scrollbar(self, command=self.text_edit.yview)
    scroll_bar.grid(row=1, column=1, sticky="ns")
    self.text_edit.config(yscrollcommand=scroll_bar.set)

    frame = tk.Frame(self, relief=tk.RAISED, bd=2)
    save_as_button = tk.Button(frame, text="Save As", command=self.save_as_file)
    save_button = tk.Button(frame, text="Save", command=self.save_file)
    open_button = tk.Button(frame, text="Open", command=self.open_file)
    new_button = tk.Button(frame, text="New", command=self.new_file)
    undo_button = tk.Button(frame, text="Undo")
    redo_button = tk.Button(frame, text="Redo")
    run_button = tk.Button(frame, text="Run")

    # Sticky fills the contents in directions: northsouth, eastwest
    save_as_button.grid(row=0, column=0, padx=5, pady=5, sticky="ns")
    save_button.grid(row=0, column=1, padx=5, pady=5, sticky="ns")
    open_button.grid(row=0, column=2, padx=5, pady=5, sticky="ns")
    new_button.grid(row=0, column=3, padx=5, pady=5, sticky="ns")

    # Create an empty column that will expand
    frame.grid_columnconfigure(4, weight=1)

    # Place the Run button on the far right
    undo_button.grid(row=0, column=5, padx=5, pady=5, sticky="ns")
    redo_button.grid(row=0, column=6, padx=5, pady=5, sticky="ns")
    run_button.grid(row=0, column=7, padx=5, pady=5, sticky="ns")
    frame.grid(row=0, column=0, sticky="ew", columnspan=2)

    self.pack(expand=True, fill=tk.BOTH) # maintain this to totally overlap the previous window

    # Bind keyboard shortcuts using lambda functions
    self.main.master.bind_all("<Control-s>", lambda event: self.save_file())
    self.main.master.bind_all("<Control-S>", lambda event: self.save_as_file())
    self.main.master.bind_all("<Control-o>", lambda event: self.open_file())
    self.main.master.bind_all("<Control-n>", lambda event: self.new_file())

    # Bind undo and redo functionality
    self.main.master.bind_all("<Control-z>", lambda event: self.text_edit.edit_undo())
    self.main.master.bind_all("<Control-y>", lambda event: self.text_edit.edit_redo())
    
    # Bind window close event
    self.main.master.protocol("WM_DELETE_WINDOW", self.on_closing)
  def save_as_file(self):
    path = asksaveasfilename(defaultextension=".rot", filetypes=[("Brain Rot Files", "*.rot")])
    if not path: return
    self.filepath = path
    self.save_file()
  
  def save_file(self):
    if not self.filepath: self.save_as_file()
    content = self.text_edit.get(1.0, tk.END)[:-1]
    with open(self.filepath, "w") as f:
      f.write(content)
    self.default_text = content
    self.main.master.title(f"{os.path.basename(self.filepath)} - Compiley Studio")

  def open_file(self):
    if self.default_text != self.text_edit.get(1.0, tk.END).strip():
      # Prompt the user to save changes
      response = msgbox.askyesnocancel("Unsaved Changes", f"Do you want to save changes to {os.path.basename(self.filepath)}?")
      
      if response is None:  # Cancel
        return
      elif response:  # Yes, save changes
        self.save_file()

    path = askopenfilename(filetypes=[("BrainRot Files", "*.rot")])
    if not path:
      return
    self.filepath = path
    # line one first character to ending character
    self.text_edit.delete(1.0, tk.END)
    with open(self.filepath, "r") as f:
      content = f.read()
      self.text_edit.insert(tk.END, content)
      self.text_edit.mark_set(tk.INSERT, tk.END)
      self.text_edit.see(tk.END)
    self.default_text = content
    self.main.master.title(f"{os.path.basename(self.filepath)} - Compiley Studio")


  def new_file(self):
    # Check if there are unsaved changes
    if self.default_text != self.text_edit.get(1.0, tk.END).strip():
      # Prompt the user to save changes
      response = msgbox.askyesnocancel("Unsaved Changes", f"Do you want to save changes to {os.path.basename(self.filepath)}?")
      
      if response is None:  # Cancel
        return
      elif response:  # Yes, save changes
        self.save_file()

    # Open the save file dialog with a default filename
    path = asksaveasfilename(
      defaultextension=".rot",  # Set .rot as the default extension
      filetypes=[("BrainRot File", "*.rot")],  # Only show .rot files
      initialfile="new_file.rot"  # Default filename
    )
    
    # If the user cancels the dialog, path will be an empty string
    if not path:
      return
    
    self.filepath = path
    # Create a blank file at the specified path
    with open(self.filepath, "w") as f:
      pass  # Just create an empty file

    self.default_text = ""
    self.text_edit.delete(1.0, tk.END)
    self.text_edit.insert(tk.END, self.default_text)
    # Set cursor to the end of the default content
    self.text_edit.mark_set(tk.INSERT, tk.END)
    self.text_edit.see(tk.END)
    self.main.master.title(f"{os.path.basename(self.filepath)} - Compiley Studio")

  def restore_down(self):
    self.main.master.geometry("400x400")

  def on_closing(self):
    # Check if there are unsaved changes
    if self.default_text != self.text_edit.get(1.0, tk.END).strip():
        # Prompt the user to save changes
        response = msgbox.askyesnocancel("Unsaved Changes", f"Do you want to save changes to {os.path.basename(self.filepath) if self.filepath else 'Untitled'}?")
        
        if response is None:  # Cancel
            return
        elif response:  # Yes, save changes
            self.save_file()
    
    # If no unsaved changes or user clicked "No", proceed with closing
    self.main.master.destroy()

  def show(self):
    self.main.master.state('zoomed')
    self.main.master.after(1000, self.restore_down)
    self.main.master.resizable(True, True)
    self.pack(expand=True, fill=tk.BOTH) # maintain this to totally overlap the previous window
    self.main.master.title(f"{os.path.basename(self.filepath)} - Compiley Studio")