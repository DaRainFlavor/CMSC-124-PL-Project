import customtkinter as ctk
from PIL import ImageTk, Image
from custom_hovertip import CustomTooltipLabel
import subprocess
import threading
from COMPILER.compiler import Compiler
import tempfile
import time

class JavaProcessInterface:
    def __init__(self, root):
        self.root = root
        self.startTime = time.time()
        self.isCompiling = True

        # Output Text Widget
        self.output_text = ctk.CTkTextbox(root, wrap='word', height=300, width=500, font=('Arial', 18), state='disabled')
        self.output_text.pack(fill='both', expand=True)

        # Input Entry and Send Button in a Frame
        self.input_frame = ctk.CTkFrame(root)
        self.input_frame.pack(pady=5)

        self.input_entry = ctk.CTkEntry(self.input_frame, width=300, placeholder_text="Enter your input here", font=('Arial', 18))
        self.input_entry.pack(side='left', padx=(0, 5))

        send_image = ctk.CTkImage(Image.open("images/send_image.png").resize((40, 40), Image.Resampling.LANCZOS))
        self.send_button = ctk.CTkButton(self.input_frame, image=send_image, text="", corner_radius=10, width=65, command=self.send_input)
        # self.input_button = ctk.CTkButton(self.input_frame, text="Send", font=('Arial', 18), command=self.send_input)
        self.send_button.pack(side='left')
        
        self.disableConsole()
        CustomTooltipLabel(anchor_widget=self.send_button, text="Send")
        self.process = None
        # self.start_java_process()

    def disableConsole(self):
        # Disable the input entry and send button to prevent user interaction
        self.input_entry.configure(state="disabled")
        self.send_button.configure(state="disabled", fg_color="gray")

    def enableConsole(self):
        self.input_entry.configure(state="normal")
        self.send_button.configure(state="normal", fg_color="#1f538d")
            


    # def start_process(self, filepath):
    #     start_time = time.time()  # Start the timer
    #     self.start_java_process(filepath)
    #     # Wait for the process to finish
    #     self.process.wait()  # This blocks until the process ends
    #     end_time = time.time()  # End the timer after the process completes
    #     self.display_output(f"Execution time: {end_time - start_time:.6f} seconds")

    def start_java_process(self, filepath):
        self.display_output("Compiling...")
        try:
            # Read the content from the provided filepath
            with open(filepath, 'r', encoding='utf-8') as original_file:
                content = original_file.read()
                c = Compiler(content)
                if c.terminalParsingResult:
                    self.display_output(c.terminalParsingResult)
                if not c.success:
                    end_time = time.time()
                    elapsed_time = end_time - self.startTime  # Calculate the time difference
                    self.display_output(f"\nProgram has ended in {elapsed_time:.2f} seconds.")
                    # self.disableConsole()
                    return
                content = c.getFinalMIPS()
                # print(f"content: {content}")

            # Write the content to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".s") as temp_file:
                temp_file.write(content.encode('utf-8'))
                temp_filepath = temp_file.name

            self.process = subprocess.Popen(
                ['java', '-jar', 'Mars4_5.jar', temp_filepath],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # Start a thread to read the output from the Java process
            threading.Thread(target=self.read_output, daemon=True).start()
        except Exception as e:
            print(f"Error occurred: {e}")

    def clear_output(self):
        self.output_text.configure(state='normal')  # Enable editing
        self.output_text.delete('1.0', 'end')       # Clear all text
        self.output_text.configure(state='disabled')  # Disable editing


    def read_output(self):
        credit = "MARS 4.5  Copyright 2003-2014 Pete Sanderson and Kenneth Vollmar\n\n"
        output_buffer = ""
        flag = True
        while True:
            char = self.process.stdout.read(1)
            if not char:
                break  # Process ended
            
            if char!="§":
            #   self.disableConsole()
              output_buffer += char
            
            if output_buffer == credit:
                output_buffer = ""

            if char == "§":
                if self.isCompiling:
                    self.isCompiling = False
                    self.clear_output()
                self.display_output(output_buffer)
                char = self.process.stdout.read(1)
                if char == "0":
                    self.enableConsole()
                    flag = False
                    break
                if char == "1":
                    # self.disableConsole()
                    char = self.process.stdout.read(1)    
                    end_time = time.time()
                    elapsed_time = end_time - self.startTime  # Calculate the time difference
                    self.display_output(f"\nProgram has ended in {elapsed_time:.2f} seconds.")
                    return
                if char == "2":
                    # self.disableConsole()
                    end_time = time.time()
                    elapsed_time = end_time - self.startTime  # Calculate the time difference
                    self.display_output(f"\nDivision by zero occured.\nProgram has ended in {elapsed_time:.2f} seconds.")
                    return
        
        if flag:
            if self.isCompiling and output_buffer:
                self.isCompiling = False
                self.clear_output()
            self.display_output(output_buffer)

        # if self.process.poll() is not None:  # Non-blocking check if the process ended
        #   self.display_output("\nProgram has ended.")

    def display_output(self, output):
        self.output_text.configure(state='normal')
        self.output_text.insert("end", output)
        self.output_text.configure(state='disabled')
        self.output_text.see("end")

    def send_input(self):
        user_input = self.input_entry.get()
        if user_input:
            self.display_output(user_input + "\n")
        
        if self.process and self.process.stdin:
            self.input_entry.delete(0, "end")
            self.disableConsole()
            self.process.stdin.write(user_input + '\n')
            self.process.stdin.flush()
        
        self.input_entry.delete(0, "end")
        threading.Thread(target=self.read_output, daemon=True).start()  # Resume output reading