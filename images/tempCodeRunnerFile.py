print("Speak your program instructions (say 'stop' to end).")
combined_instructions = get_speech_input()

if combined_instructions:
    print("Processing the following instructions:")
    print(combined_instructions)
else:
    print("No valid instructions provided.")
