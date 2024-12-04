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

        on_mic_image = ctk.CTkImage(Image.open("images/on_mic_image.png").resize((40, 40), Image.Resampling.LANCZOS))
        self.on_mic_button = ctk.CTkButton(self.input_frame, image=on_mic_image, text="", corner_radius=10, width=65, command=self.on_mic)
        self.on_mic_button.pack(side='left')
        
        # self.disableConsole()
        CustomTooltipLabel(anchor_widget=self.send_button, text="Send")
        self.process = None

        self.display_output("Speak your program instructions (say 'stop' to end).")
        self.text_to_speech("It's working")
        self.get_speech_input()

    def text_to_speech(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()


    def get_speech_input(self):
        print("Here")
        recognizer = sr.Recognizer()

        def listen_for_speech():
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                self.display_output("Listening for input... Say 'stop' to end.")
                
                while True:
                    try:
                        audio = recognizer.listen(source, timeout=None)
                        instruction = recognizer.recognize_google(audio)
                        print(f"Recognized: {instruction}")

                        if "stop" in instruction.lower():
                            self.display_output("Paused")
                            break
                        
                        self.input_entry.insert("end", instruction + " ")
                        print(instruction)
                    except sr.UnknownValueError:
                        print("Could not understand the speech, but continuing.")
                        pass
                    except sr.RequestError:
                        self.text_to_speech("Error: Could not process speech. Check your internet connection.")
                        self.display_output("Error: Could not process speech. Check your internet connection.")
                    except Exception as e:
                        print(f"An unexpected error occurred: {e}")
                        pass

        # Run the speech listening function in a separate thread
        threading.Thread(target=listen_for_speech, daemon=True).start()
                    
    def on_mic(self):
        pass

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
