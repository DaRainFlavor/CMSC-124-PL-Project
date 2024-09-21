# Anything in here reflects to all state windows

import tkinter as tk
# import all state windows
from flash_window import FlashWindow
from code_window import CodeWindow
from welcome_window import WelcomeWindow

class MainWindow():
  # master is the root from the main
  def __init__(self, master):
    self.master = master # used to access the root from different state windows
    mainframe = tk.Frame(self.master) # create a frame to be displayed in the root
    mainframe.pack(fill="both", expand=1)
    self.current_window = "FirstWindow" # current window initialized to first window

    # create a dictionary containing all the state windows
    # pass the mainframe to be inside the mainframe
    self.frames = {
      # self is MainWindow()     
      # mainframe is where the frames of each state windows be placed
      "FlashWindow": FlashWindow(mainframe, self),
      "WelcomeWindow": WelcomeWindow(mainframe, self),
      "CodeWindow": CodeWindow(mainframe, self)
    }
    
    # display only the current state window
    self.forgetExcptCurrent()

    # Show the initial window customizations being set
    self.frames["FlashWindow"].show()

  # call when the desired state window is set first
  def forgetExcptCurrent(self):
    for key, state in self.frames.items():
      if(key == self.current_window): continue
      state.forget()  # forget all state windows except the current

  def changeWindow(self, currentStateWindow):
    self.current_window = currentStateWindow
    self.forgetExcptCurrent()
    self.frames[self.current_window].tkraise() # put on top of stack the current state window
    self.frames[self.current_window].show() # display any customizations of the window affecting the root