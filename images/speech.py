import pyttsx3
import speech_recognition as sr

# Text-to-Speech Function
def text_to_speech(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_speech_input():
    recognizer = sr.Recognizer()
    combined_instructions = ""

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening for input... Say 'stop' to end.")
        
        while True:
            try:
                audio = recognizer.listen(source, timeout=None)
                instruction = recognizer.recognize_google(audio)
                print(f"Recognized: {instruction}")

                if "stop" in instruction.lower():
                    text_to_speech("Stopping listening.")
                    break
                
                combined_instructions += instruction + " "
            
            except sr.UnknownValueError:
                print("Could not understand the speech, but continuing.")
            except sr.RequestError:
                print("Error: Could not process speech. Check your internet connection.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                
    return combined_instructions.strip()

# Main execution
print("Speak your program instructions (say 'stop' to end).")
combined_instructions = get_speech_input()

if combined_instructions:
    print("Processing the following instructions:")
    print(combined_instructions)
else:
    print("No valid instructions provided.")
