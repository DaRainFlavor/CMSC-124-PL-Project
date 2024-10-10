import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import tkinter.messagebox as msgbox
import os
import customtkinter 
from PIL import ImageTk, Image 
from tooltip import ToolTip
import subprocess

class CodeWindow(tk.Frame):
  def __init__(self, parent, main):
    super().__init__(parent, bg="white")
    self.main = main
    self.filepath = False

    # Configure the column and row for resizing
    self.rowconfigure(1, weight=1)
    self.columnconfigure(0, weight=1)

    self.default_text = ""
    self.font_size = 11
    self.text_edit = tk.Text(self, font=("Helvetica", self.font_size), wrap="word", undo = True)
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
    save_as_button = customtkinter.CTkButton(frame, image=save_as_image, text="", command=self.save_as_file, corner_radius=32, fg_color="White", width = 45, height=45)
    self.save_button = customtkinter.CTkButton(frame, image=save_image, text="", command=self.save_file, corner_radius=32, fg_color="White", width = 45, height=45)
    open_button = customtkinter.CTkButton(frame, image=open_image, text="", command=self.open_file, corner_radius=32, fg_color="White", width = 45, height=45)
    new_button = customtkinter.CTkButton(frame, image=new_image, text="", command=self.new_file, corner_radius=32, fg_color="White", width = 45, height=45)
    self.undo_button = customtkinter.CTkButton(frame, image=undo_image, text="", command=self.undo, corner_radius=32, fg_color="White", width = 45, height=45)
    self.redo_button = customtkinter.CTkButton(frame, image=redo_image, text="", command=self.redo, corner_radius=32, fg_color="White", width = 45, height=45)
    self.cut_button = customtkinter.CTkButton(frame, image=cut_image, text="", command=self.cut, corner_radius=32, fg_color="White", width = 45, height=45)
    self.paste_button = customtkinter.CTkButton(frame, image=paste_image, text="", command=self.paste, corner_radius=32, fg_color="White", width = 45, height=45)
    run_button = customtkinter.CTkButton(frame, image=run_image, text="", command=self.run, corner_radius=32, fg_color="White", width = 45, height=45)
    
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

    self.pack(expand=True, fill=tk.BOTH) # maintain this to totally overlap the previous window

    # Bind keyboard shortcuts using lambda functions
    self.main.master.bind_all("<Control-s>", lambda event: self.save_file())
    self.main.master.bind_all("<Control-S>", lambda event: self.save_as_file())
    self.main.master.bind_all("<Control-o>", lambda event: self.open_file())
    self.main.master.bind_all("<Control-n>", lambda event: self.new_file())

    # Bind undo and redo functionality
    self.main.master.bind_all("<Control-z>", lambda event: self.text_edit.edit_undo())
    self.main.master.bind_all("<Control-y>", lambda event: self.text_edit.edit_redo())
    
    # Bind events for detecting changes in text
    self.text_edit.bind("<KeyRelease>", self.on_text_change)

    # Bind the <<Selection>> event to track text selection
    self.text_edit.bind("<<Selection>>", self.update_cut_button)

    # Bind zoom in/out keyboard shortcuts
    self.main.master.bind_all("<Control-equal>", lambda event: self.zoom_in())
    self.main.master.bind_all("<Control-minus>", lambda event: self.zoom_out())

    # Bind window close event
    self.main.master.protocol("WM_DELETE_WINDOW", self.on_closing)

  def on_text_change(self, event=None):
    # Enable or disable the save button based on content change
    # print(f"{self.text_edit.get(1.0, tk.END).strip()}, {self.default_text}")
    if self.text_edit.get(1.0, tk.END).strip() != self.default_text:
      self.save_button.configure(state=tk.NORMAL, fg_color="white")
    else:
      self.save_button.configure(state=tk.DISABLED, fg_color="#DDDCDD")

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
    self.save_button.configure(state=tk.DISABLED, fg_color="#DDDCDD")
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
        
  def undo(self):
    try:
        self.text_edit.edit_undo()
    except tk.TclError:  # This handles when there's nothing to undo
        pass

  def redo(self):
    try:
        self.text_edit.edit_redo()
    except tk.TclError:  # This handles when there's nothing to redo
        pass

  def cut(self):
      try:
          # Check if there's a selection in the text widget
          if self.text_edit.tag_ranges(tk.SEL):
              # Copy selected text to clipboard
              self.text_edit.clipboard_clear()
              self.text_edit.clipboard_append(self.text_edit.selection_get())
              # Delete selected text
              self.text_edit.delete(tk.SEL_FIRST, tk.SEL_LAST)
      except tk.TclError:
          pass  # Handle the case when no text is selected

  def update_cut_button(self, event=None):
    try:
      # If there is a selection, enable the cut button
      if self.text_edit.tag_ranges(tk.SEL):
        self.cut_button.configure(state=tk.NORMAL, fg_color="white")
      else:
        # If no selection, disable the cut button
        self.cut_button.configure(state=tk.DISABLED, fg_color="#DDDCDD")
    except tk.TclError:
      # Disable the button in case of any exception (e.g., no selection)
      self.cut_button.configure(state=tk.DISABLED, fg_color="#DDDCDD")

  def paste(self):
    try:
      # Get the clipboard text and insert it at the current cursor position
      clipboard_text = self.text_edit.selection_get(selection='CLIPBOARD')
      self.text_edit.insert(tk.INSERT, clipboard_text)
    except tk.TclError:
      pass  # Handle the case when the clipboard is empty or no text is available

  def update_paste_button(self):
    try:
      # Try to access clipboard data
      clipboard_text = self.text_edit.clipboard_get()
      if clipboard_text:
          # If clipboard has text, enable the paste button
          self.paste_button.configure(state=tk.NORMAL, fg_color="white")
      else:
          # If clipboard is empty, disable the paste button
          self.paste_button.configure(state=tk.DISABLED, fg_color="#DDDCDD")
    except tk.TclError:
      # Handle the case where the clipboard is empty or unavailable
      self.paste_button.configure(state=tk.DISABLED, fg_color="#DDDCDD")

    # Call this method again after 100ms to continuously check clipboard
    self.after(100, self.update_paste_button)


  def run(self):
    self.save_file()
    mars_path = "Mars4_5.jar"
    code = self.text_edit.get("1.0", tk.END).strip()  # Get the code from the text widget
    # Save the MIPS assembly code to a file
    assembly_file_name = f"{os.path.basename(self.filepath)}.s"
    with open(assembly_file_name, 'w') as f:
      f.write(code)
    try:
      result = subprocess.run(
        ['java', '-jar', mars_path, assembly_file_name],  # Use the mars_path variable
        capture_output=True,
        text=True
      )
      
      # Display the output from MARS
      print("MIPS Program Output:")
      print(result.stdout)
    except Exception as e:
      print("MARS is not installed or not found in your system's PATH.")

  def zoom_in(self):
    if self.font_size < 200:
      self.font_size += 1
      self.text_edit.config(font=("Helvetica", self.font_size))

  def zoom_out(self):
    if self.font_size > 8:
      self.font_size -= 1
      self.text_edit.config(font=("Helvetica", self.font_size))

  def restore_down(self):
    self.main.master.geometry("1055x400")

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
    self.save_button.configure(state=tk.DISABLED, fg_color="#DDDCDD")
    self.update_cut_button()
    # self.update_paste_button()
    self.pack(expand=True, fill=tk.BOTH) # maintain this to totally overlap the previous window
    self.main.master.title(f"{os.path.basename(self.filepath)} - Compiley Studio")
    