# This covers the main where customization should preferrably be only the title and window icon
# Anything here reflects the entire application

import tkinter as tk
from main_window import MainWindow

def main():
  root = tk.Tk()
  root.title("Compiley Studio")
  window = MainWindow(root)
  root.iconbitmap("icon.ico")
  root.mainloop()

if __name__ == "__main__":
  main()
