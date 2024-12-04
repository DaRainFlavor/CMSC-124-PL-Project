import customtkinter as ctk
from PIL import ImageTk, Image
from custom_hovertip import CustomTooltipLabel
import subprocess
import threading
from COMPILER.compiler import Compiler
import tempfile
import time

import google.generativeai as genai
import pyttsx3
import speech_recognition as sr

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
                    self.clear_output()
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
        self.root.update_idletasks()  # Force UI update


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


genai.configure(api_key="AIzaSyDdYKmKnAj8SBM2P0-cvUTdb4w3pVHfLlE")

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
)

chat_session = model.start_chat(
  history=[
  ]
)

instructions = '''
Be a translator for my IDE that does instructions to code.
Convert my prompt or what I said or I ask you to do in BrainRot syntax. 

If you think my prompt didn't ask you to code something or do something, or sending gibberish propmt, reply this "Error: {tell the reason}". When the prompt asks you as an AI that does not involve coding with Brainrot like asking for your opinion, reply "Error: {tell the reason}" Always begin error messages with "Error: "


Brainrot's syntax has similarity with c++, it only replaced the following:

int -> clout
string -> sigma
'\\n' -> can be written as "slay" "\\n" or hitting new line through enter
cout -> yap
cin -> spill
if -> let him cook
else if -> what if
else -> cooked
return 0 -> it's giving

My grammar can only do one operator (+, -, *, /) per instruction. 
Example : x = 3+3;

This is all the features or what BrainRot is capable of:
clout x = 3;
spill>>x;
sigma y = "Hello";
spill>>y;
yap<<y<<" "<<x<<slay<<x+10<<11+11<<"Hello" + "World"<<"Hello"+slay;
sigma y = "Hello" + "me"; 
sigma = "
Long sentence
" // Long Text can be separated with new lines by using '\n' adding slay "+slay" or hitting enter 

x = x+10;

let him cook(x>3){
    int x = 10;
    yap<<x<<" is greater than 3";
}
what if(x < 1){
    int x = 11;
    yap<<x<<" is less than 3";
}
cooked{
    sigma x = "hey";
    yap<<x<<" is equal to 3";
}

//long comments use /**/ same as C++

it's giving; // return 0 or end the program


Here is the grammar for your guide:
<Program> ::= <Statement> <Program> | 'SEMICOLON' <Program> | ε
<Statement> ::= <Declaration> | <Assignment> | <if> | <Print> | <Scan> | "IT'S" "GIVING" | "SEMICOLON"
<Declaration> ::= <Data_type> <Variable_list> 'SEMICOLON'
<Data_type> ::= 'CLOUT' | 'SIGMA'
<Variable_list> ::= <Variable> <Variable_list_prime>
<Variable> ::= 'IDENTIFIER' <Variable_prime>
<Variable_list_prime> ::= 'COMMA' <Variable_list> | ε
<Variable_prime> ::= 'EQUAL' <Expression> | ε
<Expression> ::= <Term><Expression_prime>
<Expression_prime> ::= <Operator> <Term> | ε
<Term> ::= 'IDENTIFIER' | <Literal>
<Literal> ::= 'MINUS' 'INTEGER_LITERAL' | 'INTEGER_LITERAL' | 'STRING_LITERAL' | 'SLAY'
<Operator> ::= 'PLUS' | 'MINUS' | 'MULTIPLY' | 'DIVIDE'
<Assignment> ::= 'IDENTIFIER' 'EQUAL' <Expression> 'SEMICOLON'
<If> ::= 'LET' 'HIM' 'COOK' <Condition> <Block> <Else_if> <Else>
<Else_if> ::= 'WHAT' 'IF' <condition> <block> <Else_if> | ε
<Else> ::= 'COOKED' <block> | ε
<Condition> ::= 'OPEN_PARENTHESIS' <Expression> (<Relational_operator> <Expression> | ε) 'CLOSE_PARENTHESIS'
<Relational_operator> ::= 'EQUAL' 'EQUAL' | <Less> |'NOT' 'EQUAL' | <Great>
<Less> ::= 'LESS_THAN' <Relational_prime>
<Great> ::= 'GREATER_THAN' <Relational_prime>
<Relational_prime> ::= 'EQUAL' | ε
<Block> ::= 'OPEN_CURLY_BRACE' <Block_program> 'CLOSE_CURLY_BRACE' | <Statement>

<Block_program> ::= <Block_statement> <Block_program> | 'SEMICOLON' <Block_program> | ε
<Block_statement> ::= <Declaration> | <Assignment> | <Print> | <Scan> | "IT'S" "GIVING" | "SEMICOLON"

<Print> ::= 'YAP' 'LESS_THAN' 'LESS_THAN' <Expression> <Print_prime> 'SEMICOLON'
<Print_prime> ::= 'LESS_THAN' 'LESS_THAN' <Expression> <Print_prime>
<Scan> ::= 'SPILL' 'GREATER_THAN' 'GREATER_THAN' 'IDENTIFIER' <Scan_prime> 'SEMICOLON'
<Scan_prime> ::= 'GREATER_THAN' 'GREATER_THAN' 'IDENTIFIER' | ε

The limitation of my code is the following:
1. it can only do +, -, *, / operations
2. operations should only be <operator> <operand> <operator>
3. no nested if-else
4. no loops are available
5. code should only be limited to the grammar like in my sample code

If my prompt above is complicated like it involves multiple operands, use multiple variables instead and do the operation one by one.
Make sure that only one operator (+, -, *, /) is involved per instruction. 
Example : x = 3+3;

If what I asked is too complicated and impossible to handle with my grammar, reply this "Error: {state your reason}".

If you think my prompt didn't ask you to code something or do something, reply this "Error: {tell that you are only capable of converting instructions to code.}". When the prompt asks you as an AI that does not involve coding with Brainrot like asking for your opinion, reply "Error: {tell that you are only capable of converting instructions to code.}" Always begin error messages with "Error: "

If you can generate a BrainRot code, respond right away the code starting with this comment "// AI Generated Code". Do not include introductory or conclusion or unnecessary texts.
'''

class AIJavaProcessInterface:
    def __init__(self, root, IDE):
        self.root = root
        self.IDE = IDE
        
        # Output Text Widget
        self.output_text = ctk.CTkTextbox(root, wrap='word', height=300, width=500, font=('Arial', 18), state='disabled')
        self.output_text.pack(fill='both', expand=True)

        # Input Entry and Send Button in a Frame
        self.input_frame = ctk.CTkFrame(root)
        self.input_frame.pack(pady=5)

        self.input_entry = ctk.CTkEntry(self.input_frame, width=300, placeholder_text="Enter your prompt here", font=('Arial', 18))
        self.input_entry.pack(side='left', padx=(0, 5))

        send_image = ctk.CTkImage(Image.open("images/send_image.png").resize((40, 40), Image.Resampling.LANCZOS))
        self.send_button = ctk.CTkButton(self.input_frame, image=send_image, text="", corner_radius=10, width=65, command=self.send_input)
        self.send_button.pack(side='left')

        # on_mic_image = ctk.CTkImage(Image.open("images/on_mic_image.png").resize((40, 40), Image.Resampling.LANCZOS))
        # self.on_mic_button = ctk.CTkButton(self.input_frame, image=on_mic_image, text="", corner_radius=10, width=65, command=self.on_mic)
        # self.on_mic_button.pack(side='left')
        
        # self.disableConsole()
        CustomTooltipLabel(anchor_widget=self.send_button, text="Send")
        self.process = None

        self.display_output("Speak your program instructions (say 'stop' to end).You can also enter your prompt below. Have fun!\n\n")
        #self.text_to_speech("Speak your program instructions. Say 'stop' to make me stop listening. You can also enter your prompt below. Have fun!")
        self.get_speech_input()

    def text_to_speech(self, text):
        self.root.update_idletasks()  # Force UI update
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()


    def get_speech_input(self):
        print("Here")
        recognizer = sr.Recognizer()

        def listen_for_speech():
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                self.display_output("Listening for input...\n")
                
                while True:
                    try:
                        audio = recognizer.listen(source, timeout=None)
                        instruction = recognizer.recognize_google(audio)
                        print(f"Recognized: {instruction}")

                        if "stop" in instruction.lower():
                            self.display_output("Listening is done.\n")
                            instruction.replace("stop", "")
                            self.input_entry.insert("end", instruction + " ")
                            print(instruction) 
                            return
                        
                        self.input_entry.insert("end", instruction + " ")
                        print(instruction)
                    except sr.UnknownValueError:
                        print("Could not understand the speech, but continuing.")
                        pass
                    except sr.RequestError:
                        self.text_to_speech("Error: Could not process speech. Check your internet connection.")
                        self.display_output("Error: Could not process speech. Check your internet connection.\n")
                    except Exception as e:
                        print(f"An unexpected error occurred: {e}")
                        pass

        # Run the speech listening function in a separate thread
        threading.Thread(target=listen_for_speech, daemon=True).start()
                    
    # def on_mic(self):
    #     pass

    def disableConsole(self):
        # Disable the input entry and send button to prevent user interaction
        self.input_entry.configure(state="disabled")
        self.send_button.configure(state="disabled", fg_color="gray")

    def enableConsole(self):
        self.input_entry.configure(state="normal")
        self.send_button.configure(state="normal", fg_color="#1f538d")
            
    def display_output(self, output):
        self.output_text.configure(state='normal')
        self.output_text.insert("end", output)
        self.output_text.configure(state='disabled')
        self.output_text.see("end")
        self.root.update_idletasks()  # Force UI update

    def send_input(self):
        user_input = self.input_entry.get()
        if user_input:
            self.input_entry.delete(0, "end")
            self.display_output(">> " + user_input + "\n")
            response = chat_session.send_message("This is my prompt:\n"+user_input + instructions)
            response = response.text + '\n'
            response = response.replace("```cpp", "")
            response = response.replace("```", "")
            if response.startswith("Error"):
                self.text_to_speech(response)
            else:
                self.IDE.insertTextToScroll(response)
            
            