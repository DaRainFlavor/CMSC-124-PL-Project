import tkinter as tk
import tkinter.font as tkFont

# This is a scrollable text widget
# Modify ScrollText to use grid() instead of pack()
class ScrollText(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        custom_font = tkFont.Font(family="Arial", size=15)
        self.text = tk.Text(self, bg='#2b2b2b', foreground="#d1dce8",
                            insertbackground='white',
                            selectbackground="blue", width=120, height=30,
                            font=custom_font,
                            undo=True)

        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.text.yview)
        self.text.configure(yscrollcommand=self.scrollbar.set)

        self.numberLines = TextLineNumbers(self, width=40, bg='#313335')
        self.numberLines.attach(self.text)

        # Use grid for proper alignment and resizing
        self.scrollbar.grid(row=0, column=2, sticky='ns')
        self.numberLines.grid(row=0, column=0, sticky='ns')
        self.text.grid(row=0, column=1, sticky='nsew')

        # Make the text and number lines expand to fill the space
        self.grid_columnconfigure(1, weight=1)  # Text widget expands horizontally
        self.grid_rowconfigure(0, weight=1)  # Text widget expands vertically

        # Bindings for updating the line numbers
        self.text.bind("<Key>", self.onPressDelay)
        self.text.bind("<Button-1>", self.numberLines.redraw)
        self.scrollbar.bind("<Button-1>", self.onScrollPress)
        self.text.bind("<MouseWheel>", self.onPressDelay)

        



    def onScrollPress(self, *args):
        self.scrollbar.bind("<B1-Motion>", self.numberLines.redraw)

    def onScrollRelease(self, *args):
        self.scrollbar.unbind("<B1-Motion>", self.numberLines.redraw)

    def onPressDelay(self, *args):
        self.after(2, self.numberLines.redraw)

    def get(self, *args, **kwargs):
        return self.text.get(*args, **kwargs)

    def insert(self, *args, **kwargs):
        self.text.insert(*args, **kwargs)
        self.numberLines.redraw()

    def delete(self, *args, **kwargs):
        return self.text.delete(*args, **kwargs)

    def index(self, *args, **kwargs):
        return self.text.index(*args, **kwargs)

    def redraw(self):
        self.numberLines.redraw()

    def get_text(self):
        return self.text.get("1.0", "end-1c")  # Fetch all the text content
    
    def set_default_text(self, text):
        self.text.delete("1.0", "end")  # Clear any existing text
        self.text.insert("1.0", text)  # Insert the default text at the beginning


'''THIS CODE IS CREDIT OF Bryan Oakley (With minor visual modifications on my side): 
https://stackoverflow.com/questions/16369470/tkinter-adding-line-number-to-text-widget'''


class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs, highlightthickness=0)
        self.textwidget = None
        
        # Define a custom font for line numbers (e.g., Arial size 12)
        self.line_number_font = tkFont.Font(family="Arial", size=15)

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")
        
        i = self.textwidget.index("@0,0")
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            # Use the custom font for the line numbers
            self.create_text(2, y, anchor="nw", text=linenum, fill="#606366", font=self.line_number_font)
            i = self.textwidget.index("%s+1line" % i)


#https://stackoverflow.com/questions/16369470/tkinter-adding-line-number-to-text-widget
