import tkinter as tk
import customtkinter
from PIL import ImageTk, Image
from custom_hovertip import CustomTooltipLabel
from tkinter.filedialog import askopenfilename, asksaveasfilename
import tkinter.messagebox as msgbox
import os
import subprocess
from scroll import *
from terminal import *
import threading

class IDE():
  def __init__(self, parent_frame, root):
    self.itemFrame = parent_frame
    self.root = root
    self.display_flash_screen()
    self.default_text = ""
    self.welcome = False
    self.flash = True
    self.is_running = False
    self.filepath=None

    self.root.bind_all("<Control-s>", lambda event: self.save_file())
    self.root.bind_all("<Control-Shift-S>", lambda event: self.save_as_file())
    self.root.bind_all("<Control-o>", lambda event: self.open_file())
    self.root.bind_all("<Control-n>", lambda event: self.new_file())

  def clear(self, object):
    slaves = object.grid_slaves()
    for x in slaves:
      x.destroy()

  def display_flash_screen(self):
    # Hide the top bar
    self.root.overrideredirect(True)

    # Get the screen width and height
    screen_width = self.root.winfo_screenwidth()
    screen_height = self.root.winfo_screenheight()

    # Set the desired window width and height for the flash screen
    window_width = 500  # You can adjust this as needed
    window_height = 400  # You can adjust this as needed

    # Calculate the x and y coordinates to center the window
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    # Set the window size and position it at the calculated coordinates
    self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    self.clear(self.itemFrame)
    customtkinter.CTkLabel(self.itemFrame, text="Hello").grid(row=0, column=0)
    customtkinter.CTkEntry(self.itemFrame).grid(row=1, column=0)

    my_image = customtkinter.CTkImage(light_image= Image.open('images/logo.jpg'), dark_image=Image.open('images/logo.jpg'), size = (360, 360))
    my_label = customtkinter.CTkLabel(self.itemFrame, text="", image=my_image, fg_color=("white"), width=500)
    my_label.grid(row = 0, column = 0, pady=0)

    label = customtkinter.CTkLabel(self.itemFrame, text = "A BrainRot compiler developed by\nAdrian Vaflor, Kimberly Padilla, and Leian Carl Dela Cruz")
    label.grid(row = 1, column = 0, pady=5)

    # After 3 seconds, switch back to menu1 and restore the top bar
    self.itemFrame.after(3000, lambda: [self.display_welcome_window(), customtkinter.set_appearance_mode("Dark")])


  def toggle_modes(self):
    if customtkinter.get_appearance_mode() == "Dark":
      customtkinter.set_appearance_mode("Light")
      if not self.welcome:
        self.scroll.text.configure(bg='#f5f5f5', foreground="#000000",
                            insertbackground='black',
                            selectbackground="#cce7ff")
        self.scroll.numberLines.configure(bg='#eaeaea')
    else:
      customtkinter.set_appearance_mode("Dark")
      if not self.welcome:
        self.scroll.text.configure(bg='#2b2b2b', foreground="#d1dce8",
                            insertbackground='white',
                            selectbackground="blue",)
        self.scroll.numberLines.configure(bg='#313335')
        



  def display_welcome_window(self):
    self.flash = False
    self.welcome = True
    self.itemFrame.after(0, lambda: self.root.wm_state('zoomed'))
    self.root.overrideredirect(False)
    self.clear(self.itemFrame)

    self.itemFrame.rowconfigure(1, weight=1)
    self.itemFrame.columnconfigure(0, weight=1)

    # Create a main frame to hold left and right frames
    frame = customtkinter.CTkFrame(master=self.itemFrame, border_width=2, corner_radius=0)
    
    # Create left and right sub-frames inside the main frame
    left_frame = customtkinter.CTkFrame(master=frame, fg_color="transparent")
    right_frame = customtkinter.CTkFrame(master=frame, fg_color="transparent")

    # Create images for buttons
    save_as_image = customtkinter.CTkImage(Image.open("images/save_as_image.png").resize((40, 40), Image.Resampling.LANCZOS))
    save_image = customtkinter.CTkImage(Image.open("images/save_image.png").resize((40, 40), Image.Resampling.LANCZOS))
    open_image = customtkinter.CTkImage(Image.open("images/open_image.png").resize((40, 40), Image.Resampling.LANCZOS))
    new_image = customtkinter.CTkImage(Image.open("images/new_image.png").resize((40, 40), Image.Resampling.LANCZOS))
    undo_image = customtkinter.CTkImage(Image.open("images/undo_image.png").resize((40, 40), Image.Resampling.LANCZOS))
    redo_image = customtkinter.CTkImage(Image.open("images/redo_image.png").resize((40, 40), Image.Resampling.LANCZOS))
    cut_image = customtkinter.CTkImage(Image.open("images/cut_image.png").resize((40, 40), Image.Resampling.LANCZOS))
    paste_image = customtkinter.CTkImage(Image.open("images/paste_image.png").resize((40, 40), Image.Resampling.LANCZOS))
    run_image = customtkinter.CTkImage(Image.open("images/run_image.png").resize((40, 40), Image.Resampling.LANCZOS))
    self.darklightmode_image = customtkinter.CTkImage(Image.open("images/darklightmode_image.png").resize((40, 40), Image.Resampling.LANCZOS))

    # Create buttons for left side
    self.save_as_button = customtkinter.CTkButton(master=left_frame, image=save_as_image, text="", corner_radius=10, fg_color="#DDDCDD", state=tk.DISABLED, width=65, height=45, command=self.save_as_file)
    self.save_button = customtkinter.CTkButton(master=left_frame, image=save_image, text="", corner_radius=10, fg_color="#DDDCDD", state=tk.DISABLED, width=65, height=45, command=self.save_file)
    self.open_button = customtkinter.CTkButton(master=left_frame, image=open_image, text="", corner_radius=10, fg_color="White", width=65, height=45, command= self.open_file)
    self.new_button = customtkinter.CTkButton(master=left_frame, image=new_image, text="", corner_radius=10, fg_color="White", width=65, height=45, command=self.new_file)

    # Create buttons for right side
    self.undo_button = customtkinter.CTkButton(master=right_frame, image=undo_image, text="", corner_radius=10, fg_color="#DDDCDD", state=tk.DISABLED, width=65, height=45, command=self.undo)
    self.redo_button = customtkinter.CTkButton(master=right_frame, image=redo_image, text="", corner_radius=10, fg_color="#DDDCDD", state=tk.DISABLED, width=65, height=45, command=self.redo)
    self.cut_button = customtkinter.CTkButton(master=right_frame, image=cut_image, text="", corner_radius=10, fg_color="#DDDCDD", state=tk.DISABLED, width=65, height=45, command=self.cut)
    self.paste_button = customtkinter.CTkButton(master=right_frame, image=paste_image, text="", corner_radius=10, fg_color="#DDDCDD", state=tk.DISABLED, width=65, height=45, command=self.paste)
    self.darklightmode_button = customtkinter.CTkButton(master=right_frame, image = self.darklightmode_image, text="", corner_radius=10, fg_color="White", width=65, height=45, command=self.toggle_modes)
    self.run_button = customtkinter.CTkButton(master=right_frame, image=run_image, text="", corner_radius=10, fg_color="#DDDCDD", state=tk.DISABLED, width=65, height=45, command=self.run)

    # Position buttons in the left frame
    self.save_as_button.grid(row=0, column=0, padx=5, pady=5, sticky="ns")
    self.save_button.grid(row=0, column=1, padx=5, pady=5, sticky="ns")
    self.open_button.grid(row=0, column=2, padx=5, pady=5, sticky="ns")
    self.new_button.grid(row=0, column=3, padx=5, pady=5, sticky="ns")

    # Position buttons in the right frame
    self.undo_button.grid(row=0, column=0, padx=5, pady=5, sticky="ns")
    self.redo_button.grid(row=0, column=1, padx=5, pady=5, sticky="ns")
    self.cut_button.grid(row=0, column=2, padx=5, pady=5, sticky="ns")
    self.paste_button.grid(row=0, column=3, padx=5, pady=5, sticky="ns")
    self.darklightmode_button.grid(row=0, column=4, padx=5, pady=5, sticky="ns")
    self.run_button.grid(row=0, column=5, padx=5, pady=5, sticky="ns")

    # Add tooltips
    CustomTooltipLabel(anchor_widget=self.save_as_button, text="Save As")
    CustomTooltipLabel(anchor_widget=self.save_button, text="Save")
    CustomTooltipLabel(anchor_widget=self.open_button, text="Open")
    CustomTooltipLabel(anchor_widget=self.new_button, text="New")
    CustomTooltipLabel(anchor_widget=self.undo_button, text="Undo")
    CustomTooltipLabel(anchor_widget=self.redo_button, text="Redo")
    CustomTooltipLabel(anchor_widget=self.cut_button, text="Cut")
    CustomTooltipLabel(anchor_widget=self.paste_button, text="Paste")
    CustomTooltipLabel(anchor_widget=self.run_button, text="Run")
    CustomTooltipLabel(anchor_widget=self.darklightmode_button, text="Change Theme")

    # Position left and right frames inside the main frame
    left_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    right_frame.grid(row=0, column=1, padx=10, pady=5, sticky="e")

    # Frame configuration
    frame.grid(row=0, column=0, sticky="ew", columnspan=2)
    frame.grid_columnconfigure(0, weight=1)

    # Welcome frame to hold image and intro
    self.welcome_frame = customtkinter.CTkFrame(master=self.itemFrame, fg_color="transparent")
    self.welcome_frame.columnconfigure(0, weight=1)  # Column for image
    self.welcome_frame.columnconfigure(1, weight=1)  # Column for intro
    self.welcome_frame.rowconfigure(0, weight=1)     # Ensure content is vertically centered

    # Welcome message (still centered)
    welcome_message = "Welcome to Compiley Studio!"
    welcome_label = customtkinter.CTkLabel(self.welcome_frame, text=welcome_message, font=("Arial", 50))
    welcome_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="ew")  # Center welcome label

    # # Image placeholder (replace with actual image)
    # image_placeholder = customtkinter.CTkLabel(self.welcome_frame, text="[Image]", fg_color="red", width=150, height=150)
    # image_placeholder.grid(row=1, column=0, pady=10, sticky="e")  # Place image in left column

    my_image = customtkinter.CTkImage(light_image= Image.open('images/brainrot_image.jfif'), dark_image=Image.open('images/brainrot_image.jfif'), size = (360, 360))
    my_label = customtkinter.CTkLabel(self.welcome_frame, text="", image=my_image, width=150, height = 150, bg_color = "transparent")
    my_label.grid(row=1, column=0, sticky="e")

    # Introduction text beside the image
    intro_message = "Compiley Studio is a compiler for BrainRot (.rot) files.\nBrainRot is a programming language whose syntax is\ninspired by Gen-Alpha terms and slang. This preserves\nthe cringe of the generation this is built."
    intro_label = customtkinter.CTkLabel(self.welcome_frame, text=intro_message, font=("Arial", 20), anchor="w", justify="left")
    intro_label.grid(row=1, column=1, sticky="w")  # Place intro text in right column

    # Place the welcome frame in the main grid
    self.welcome_frame.grid(row=1, column=0, sticky="ew", columnspan=2, pady=(150, 0))


  def update_button_state(self, enable=None, disable=None):
    if enable:
      for buttons in enable:
        buttons.configure(state=tk.NORMAL, fg_color="white")
    if disable:
      for buttons in disable:
        buttons.configure(state=tk.DISABLED, fg_color="#DDDCDD")
    
  def save_as_file(self):
    if self.flash: return
    if self.welcome: return
    path = asksaveasfilename(defaultextension=".rot", filetypes=[("Brain Rot Files", "*.rot")])
    if not path: return
    self.filepath = path
    self.save_file()
  
  def save_file(self):
    if self.flash: return
    if self.welcome: return
    if not self.filepath: 
      self.save_as_file()

    content = self.scroll.get(1.0, tk.END)[:-1]
    with open(self.filepath, "w") as f:
      f.write(content)
    self.default_text = content
    self.on_text_change()
    self.root.title(f"{os.path.basename(self.filepath)} - Compiley Studio")

  def open_file(self):
    if self.flash: return
    if self.welcome:
      path = askopenfilename(filetypes=[("BrainRot File", "*.rot")])
      if not path:
        return
      self.filepath = path
      self.welcome = False
      self.display_text_editor()
      with open(self.filepath, "r") as f:
        content = f.read()
        self.scroll.delete(1.0, tk.END)
        self.scroll.insert(tk.END, content)
      self.default_text = content
      self.on_text_change()
      self.can_paste()
      self.scroll.text.edit_reset()  # Clear undo/redo history
      self.scroll.text.edit_modified(False)  # Reset the modified state
      self.root.title(f"{os.path.basename(self.filepath)} - Compiley Studio")
    else:
      if self.default_text != self.scroll.get(1.0, tk.END)[:-1]:
        if self.filepath == None:
          response = msgbox.askyesnocancel("Unsaved File", f"Do you want to save this draft?")
        else:
          # Prompt the user to save changes
          response = msgbox.askyesnocancel("Unsaved Changes", f"Do you want to save changes to {os.path.basename(self.filepath)}?")
        
        if response is None:  # Cancel
          return
        elif response:  # Yes, save changes
          self.save_file()
        else:
          self.scroll.delete(1.0, tk.END)
          self.scroll.insert(tk.END, self.default_text)  
          self.scroll.text.edit_reset()  # Clear undo/redo history    

      path = askopenfilename(filetypes=[("BrainRot File", "*.rot")])
      if not path:
        return
      
      self.filepath = path

      # line one first character to ending character
      self.scroll.delete(1.0, tk.END)
      with open(self.filepath, "r") as f:
        content = f.read()
        self.scroll.insert(tk.END, content)
      self.default_text = content
      self.on_text_change()
      self.scroll.text.edit_reset()  # Clear undo/redo history
      self.scroll.text.edit_modified(False)  # Reset the modified state
      self.root.title(f"{os.path.basename(self.filepath)} - Compiley Studio")

  def new_file(self):
    if self.flash: return
    if self.welcome:
      # # Open the save file dialog with a default filename
      # self.filepath = asksaveasfilename(
      #   defaultextension=".rot",  # Set .rot as the default extension
      #   filetypes=[("BrainRot File", "*.rot")],  # Only show .rot files
      #   initialfile="new_file.rot"  # Default filename
      # )

      # # If the user cancels the dialog, path will be an empty string
      # if not self.filepath:
      #   return

      # # Create a blank file at the specified path
      # with open(self.filepath, "w") as f:
      #   pass  # Just create an empty file
      
      self.welcome = False
      self.display_text_editor()
      self.scroll.delete(1.0, tk.END)
      self.on_text_change()
      self.can_paste()
      self.default_text = ""
      self.filepath = None
      self.root.title("Unknown - Compiley Studio")
    else:
      if not self.filepath:
        if self.default_text == self.scroll.get(1.0, tk.END)[:-1]: return

        response = msgbox.askyesnocancel("Unsaved File", f"Do you want to save this draft?")
        
        if response is None:  # Cancel
          return
        elif response:  # Yes, save changes
          self.save_file()
      elif self.default_text != self.scroll.get(1.0, tk.END)[:-1]:
        # Prompt the user to save changes
        response = msgbox.askyesnocancel("Unsaved Changes", f"Do you want to save changes to {os.path.basename(self.filepath)}?")
        
        if response is None:  # Cancel
          return
        elif response:  # Yes, save changes
          self.save_file()

      self.scroll.delete(1.0, tk.END)
      self.default_text = ""
      self.scroll.text.edit_reset()
      self.filepath = None
      self.root.title("Unknown - Compiley Studio")
      
      # path = asksaveasfilename(
      #     defaultextension=".rot",  # Set .rot as the default extension
      #     filetypes=[("BrainRot File", "*.rot")],  # Only show .rot files
      #     initialfile="new_file.rot"  # Default filename
      #   )
    
      # # If the user cancels the dialog, path will be an empty string
      # if not path:
      #   return
  
      # self.scroll.delete(1.0, tk.END)
      # # Create a blank file at the specified path
      # with open(path, "w") as f:
      #   pass  # Just create an empty file
      # self.default_text= ""
      # self.scroll.text.edit_reset()  # Clear undo/redo history
      # self.scroll.text.edit_modified(False)  # Reset the modified state
      # self.root.title(f"{os.path.basename(self.filepath)} - Compiley Studio")

  def cut(self):
    try:
      # Check if there's a selection in the text widget
      if self.scroll.text.tag_ranges(tk.SEL):
        # Copy selected text to clipboard
        # self.scroll.text.clipboard_clear()
        self.scroll.text.clipboard_append(self.scroll.text.selection_get())
        # Delete selected text
        self.scroll.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
    except tk.TclError:
        pass  # Handle the case when no text is selected
  
  def paste(self):
    try:
      # Get the clipboard text and insert it at the current cursor position
      clipboard_text = self.scroll.text.selection_get(selection='CLIPBOARD')
      self.scroll.text.insert(tk.INSERT, clipboard_text)
      self.scroll.numberLines.redraw()
    except tk.TclError:
      pass  # Handle the case when the clipboard is empty or no text is available

  def can_paste(self):
    try:
      # Try to access clipboard data
      clipboard_text = self.scroll.text.clipboard_get()
      if clipboard_text:
        # If clipboard has text, enable the paste button
        if self.paste_button.cget("state") == "disabled":
          self.update_button_state({self.paste_button}, {})
      else:
        if self.paste_button.cget("state") == "normal":
          # If clipboard is empty, disable the paste button
          self.update_button_state({}, {self.paste_button})
    except tk.TclError:
      # Handle the case where the clipboard is empty or unavailable
      self.update_button_state({}, {self.paste_button})

    # Call this method again after 100ms to continuously check clipboard
    self.itemFrame.after(100, self.can_paste)

  def undo(self):
    self.update_undo_redo_buttons()
    try:
        self.scroll.text.edit_undo()
    except tk.TclError:  # This handles when there's nothing to undo
        # print("Nothing to undo")
        pass

  def redo(self):
    self.update_undo_redo_buttons()
    try:
        self.scroll.text.edit_redo()
    except tk.TclError:  # This handles when there's nothing to redo
        # print("Nothing to redo")
        pass

  def update_undo_redo_buttons(self):
    self.scroll.redraw()
    if self.scroll.text.edit("canundo"):
        if (self.undo_button.cget("state") == "disabled"):
          self.update_button_state({self.undo_button}, {})
    else:
        if (self.undo_button.cget("state") == "normal"):
          self.update_button_state({}, {self.undo_button})

    if self.scroll.text.edit("canredo"):
        if (self.redo_button.cget("state") == "disabled"):
          self.update_button_state({self.redo_button}, {})
    else:
        if (self.redo_button.cget("state") == "normal"):
          self.update_button_state({}, {self.redo_button})
    self.text_frame.after(200, self.update_undo_redo_buttons)


  def close_terminal(self):
    self.clear(self.terminal_frame)
    self.terminal_frame.destroy()
    self.is_running = False

  def run(self):
    if self.is_running:
      self.close_terminal()
    self.is_running = True
    self.save_file()
    
    # Create the frame for the Text widget and line numbers
    self.terminal_frame = customtkinter.CTkFrame(self.itemFrame, fg_color="transparent")
    self.terminal_frame.grid(row=1, column=1, sticky='nsew')

    # Make the frame expand to fill available space
    self.terminal_frame.grid_rowconfigure(1, weight=1)
    self.terminal_frame.grid_columnconfigure(0, weight=1)

    close_terminal_button = customtkinter.CTkButton(self.terminal_frame, text="X", width=50, command=self.close_terminal)
    # close_terminal_button.grid(row=0, column=0, sticky='ne', padx=5, pady=5)
    close_terminal_button.pack(anchor = "e", padx=5, pady=5)
    CustomTooltipLabel(anchor_widget=close_terminal_button, text="Close")

    # # Create and add the scrollable text widget
    # self.terminal = customtkinter.CTkTextbox(self.terminal_frame, wrap="word", font=("Arial", 12), width=500)
    # self.terminal.grid(row=1, column=0, sticky='nsew')
    # self.terminal.insert("1.0", "Compiling...")


    self.terminal = JavaProcessInterface(self.terminal_frame)
    self.terminal.start_java_process(self.filepath)


  #   # Start a thread to run the MIPS code
  #   threading.Thread(target=self.run_mips).start()

  # def run_mips(self):
  #   mars_path = "Mars4_5.jar"
  #   code = self.scroll.text.get("1.0", tk.END)[:-1]
  #   assembly_file_name = f"{os.path.basename(self.filepath)}.s"
    
  #   with open(assembly_file_name, 'w') as f:
  #       f.write(code)

  #   try:
  #       result = subprocess.run(
  #           ['java', '-jar', mars_path, assembly_file_name],
  #           capture_output=True,
  #           text=True
  #       )
  #       self.terminal.delete(1.0, tk.END)  # Clear the text
  #       # Update the terminal widget with MIPS output
  #       self.terminal.insert(tk.END, f"\n{result.stdout}")
  #   except Exception as e:
  #       self.terminal.delete(1.0, tk.END)  # Clear the text
  #       self.terminal.insert(tk.END, "\nError: MARS is not installed or not found in your system's PATH.\n")
    

  def on_text_change(self, event=None):
    # print(f"{self.scroll.get(1.0, tk.END)[:-1] == self.default_text}, {self.filepath == None}")
    if (self.scroll.get(1.0, tk.END)[:-1] == self.default_text and self.filepath == None and self.new_button.cget("state") == "normal"):
      self.update_button_state({}, {self.new_button})
    elif (self.scroll.get(1.0, tk.END)[:-1] != self.default_text and self.filepath == None and self.new_button.cget("state") == "disabled"):
      self.update_button_state({self.new_button}, {})
    elif (self.scroll.get(1.0, tk.END)[:-1] == self.default_text and (not self.filepath == None) and self.new_button.cget("state") == "disabled"):
      self.update_button_state({self.new_button}, {})
    # elif (self.scroll.get(1.0, tk.END)[:-1] = self.default_text and self.new_button.cget("state") == "disabled"):
    #   self.update_button_state({self.new_button}, {})

    if (self.scroll.get(1.0, tk.END)[:-1] != self.default_text) and (self.save_button.cget("state") == "disabled"):
      self.update_button_state({self.save_button}, {})
    elif (self.scroll.get(1.0, tk.END)[:-1] == self.default_text) and (self.save_button.cget("state") == "normal"):
      self.update_button_state({}, {self.save_button})

    self.itemFrame.after(100, self.on_text_change)
    



  def on_text_selection(self, event=None):
    try:
      # If there is a selection, enable the cut button
      if self.scroll.text.tag_ranges(tk.SEL):
        self.update_button_state({self.cut_button}, {})
      else:
        # If no selection, disable the cut button
        self.update_button_state({}, {self.cut_button})
    except tk.TclError:
      # Disable the button in case of any exception (e.g., no selection)
      self.update_button_state({}, {self.cut_button})

  def display_text_editor(self):
    self.welcome = False
    self.clear(self.welcome_frame)
    self.welcome_frame.destroy()

    self.update_button_state({self.save_as_button, self.save_button, self.undo_button, self.redo_button, self.cut_button, self.paste_button}, {})
    
    # Create the frame for the Text widget and line numbers
    self.text_frame = customtkinter.CTkFrame(self.itemFrame)
    self.text_frame.grid(row=1, column=0, sticky='nsew')

    # Make the frame expand to fill available space
    self.itemFrame.grid_rowconfigure(1, weight=1)  # Allow text_frame to expand vertically
    self.itemFrame.grid_columnconfigure(0, weight=1)  # Allow text_frame to expand horizontally

    # Create and add the scrollable text widget
    self.scroll = ScrollText(self.text_frame)
    self.scroll.grid(row=0, column=0, sticky='nsew')  # Make ScrollText expand within text_frame

    # Ensure scroll occupies all space within text_frame
    self.text_frame.grid_rowconfigure(0, weight=1)
    self.text_frame.grid_columnconfigure(0, weight=1)

    # Insert some initial text
    self.scroll.insert(tk.END, "sadasda\nsdadasda\ndsa")
    self.scroll.text.focus()


    if customtkinter.get_appearance_mode() == "Dark":
        self.scroll.text.configure(bg='#2b2b2b', foreground="#d1dce8",
                            insertbackground='white',
                            selectbackground="blue",)
        self.scroll.numberLines.configure(bg='#313335')

    else:
        self.scroll.text.configure(bg='#f5f5f5', foreground="#000000",
                            insertbackground='black',
                            selectbackground="#cce7ff")
        self.scroll.numberLines.configure(bg='#eaeaea')

    self.scroll.text.bind("<KeyRelease>", self.on_text_change)
    self.scroll.text.bind("<<Selection>>", self.on_text_selection)
    self.scroll.text.bind("<<Modified>>", lambda event: self.update_undo_redo_buttons())
    self.on_text_selection()

    self.scroll.text.delete(1.0, tk.END)  # Clear the text
    self.scroll.text.edit_reset()  # Clear undo/redo history
    self.scroll.text.edit_modified(False)  # Reset the modified state
    self.update_button_state(disable=[self.undo_button, self.redo_button])  # Disable undo/redo buttons
    self.update_button_state({self.run_button}, {})
    self.can_paste()
    # Redraw line numbers after 200ms
    self.text_frame.after(200, self.scroll.redraw())