import re

class Compiler:
  def __init__(self, code):
    self.code = code
    self.idx = 0 
    self.line = 1
    self.lexer_table = {}
    self.preprocessor()
    self.parser()

  def print_lexer_table(self):
    # Print the table header
    print("           LEXER TABLE")
    print("-" * 45)
    print(f"{'LEXEME':<15} | {'TOKEN':<25}")
    print("-" * 45)
    for lexeme, token in self.lexer_table.items():
      print(f"{lexeme:<15} | {token:<25}")
      print("-" * 45)

  def preprocessor(self): #delete comments
    # NFA ALPHABET (COLUMN)
    # (0) "
    # (1) /
    # (2) \
    # (3) \n
    # (4) other symbols

    table = [
              [1,4,0,0,0],
              [0,1,2,1,1],
              [3,1,1,1,1],
              [1,1,1,1,1],
              [0,5,0,0,0],
              [6,6,6,0,6],
              [6,6,6,0,6]
            ]
    index = 0
    state = 0
    while(index < len(self.code)):
      type = 4
      if self.code[index] == "\"": type = 0
      elif self.code[index] == "/": type = 1
      elif self.code[index] == "\\": type = 2
      elif self.code[index] == "\n": type = 3
      state = table[state][type]
      if(state == 5):
        self.code = self.code[:index] + self.code[index+1:]
        self.code = self.code[:index-1] + self.code[index:]
        index-=2
      if state == 6:
        self.code = self.code[:index] + self.code[index+1:]
        index-=1

      index+=1

  def debugger(self, errorNumber, index=None):
    if index is None:
      index = self.idx
    illegalChar = self.code[index]

    # Scan left from the index until a space or the start of the string
    left = index
    while left > 0 and self.code[left - 1] not in ' \n\t':
      left -= 1

    # Scan right from the index until a space or the end of the string
    right = index
    while right < len(self.code) - 1 and self.code[right + 1] not in ' \n\t':
      right += 1

    word = self.code[left:right + 1]

    if errorNumber == 1: # unexpected character
      if word == illegalChar: print(f"Error in line {self.line}: Unexpected character `{illegalChar}`.")
      else: print(f"Error in line {self.line}: Unexpected character `{illegalChar}` in `{word}`.")
    if errorNumber == 2: # use of §
      if word == "§": print(f"Error in line {self.line}: you can't use `§`.")
      else: print(f"Error in line {self.line}: you can't use `§`. Remove it in `{word}`")
    pass

  def handle_token(self, char, token_name):
    self.lexer_table[char] = token_name
    self.idx += 1
    self.print_lexer_table()
    return char, token_name

  def scanFSMs(self):
    # Check for keywords
    nfa = {
      0: {
        "c": [1],
        "s": [6],
        "y": [11],
        "l": [14],
        "h": [21],
        "w": [29],
        "i": [33],
        "g": [38]
      },
      1: {
        "l": [2],
        "o": [24]
      },
      2: {
        "o": [3]
      },
      3: {
        "u": [4]
      },
      4: {
        "t": [5]
      },
      6: {
        "i": [7]
      },
      7: {
        "g": [8]
      },
      8: {
        "m": [9]
      },
      9: {
        "a": [10]
      },
      11: {
        "a": [12]
      },
      12: {
        "p": [13]
      },
      14: {
        "e": [19]
      },
      15: {
        "i": [16]
      },
      16: {
        "l": [17]
      },
      17: {
        "l": [18]
      },
      19: {
        "t": [20]
      },
      21: {
        "i": [22]
      },
      22: {
        "m": [23]
      },
      24: {
        "o": [25]
      },
      25: {
        "k": [26]
      },
      26: {
        "e": [27]
      },
      27: {
        "d": [28]
      },
      29: {
        "h": [30]
      },
      30: {
        "a": [31]
      },
      31: {
        "t": [32]
      },
      33: {
        "f": [34],
        "t": [35]
      },
      35: {
        "'": [36]
      },
      36: {
        "s": [37]
      },
      38: {
        "i": [39]
      },
      39: {
        "v": [40]
      },
      40: {
        "i": [41]
      },
      41: {
        "n": [42]
      },
      42: {
        "g": [43]
      }
    }

    stop_chars = " ;\"{}()<>,§+-*/=\n"
    state = 0
    lexeme = ""
    withTransition = True #becomes false when there is no state transition
    while self.idx < len(self.code) and self.code[self.idx] not in stop_chars:
      current = self.code[self.idx]
      lexeme+=current
      
      # Check if there's a valid transition for the current character
      if current in nfa.get(state, {}):
        state = nfa[state][current][0]  # Move to the next state
        self.idx += 1
      else:
        withTransition = False
        break
    # print(withTransition)
    # print(state)
    # print(f"curr: {self.code[self.idx]}")
    # print(self.code[self.idx] == "\"")
    if(self.idx<len(self.code) and self.code[self.idx] == '§'):
      self.debugger(2)
      return "", "$"
    if withTransition and state in {13, 18, 20, 23, 26, 28, 32, 34, 37, 43}:
      self.idx-=1
      # print(f"Here: {self.code[self.idx]}")
      return self.handle_token(lexeme, lexeme.upper())
    if withTransition and state in {5, 10}:
      self.idx-=1
      # print(f"Here: {self.code[self.idx]}")
      return self.handle_token(lexeme, "DATA_TYPE")
    if not withTransition and self.idx<len(self.code) and  self.code[self.idx] not in stop_chars and (lexeme == "_" or lexeme.isalpha()):
      self.idx+=1
      print(f"Here: {self.code[self.idx]} lexeme:{lexeme}")
      return self.DFAVarName(1, lexeme)
    if not withTransition and "'" in lexeme:
      print("x")
      self.debugger(1, self.code[:self.idx+1].rfind("'"))
      return "", "$"
    if self.idx<len(self.code) and self.code[self.idx] == "\"":
      return self.DFAStringVal(0)
    elif self.code[self.idx] not in stop_chars and (lexeme.isdigit()):
      return self.DFAIntVal(0)
    else:
      print("a")
      self.debugger(1)
      return "", "$"

  def DFAVarName(self, state, lexeme):
    # NFA ALPHABET (COLUMN)
    # (0) underscore
    # (1) letter
    # (2) number
    # (3) other symbols

    table = [
              [1,1,2,2],
              [1,1,1,2],  
              [2,2,2,2]
            ]
    
    stop_chars = " ;\"{}()<>,§+-*/="
    while self.idx < len(self.code) and (self.code[self.idx]=="_" or self.code[self.idx].isalpha() or self.code[self.idx].isdigit()):
      type = 3
      current = self.code[self.idx]
      lexeme+=current
      if(current == "_"): type = 0
      elif(current.isalpha()): type = 1
      elif(current.isdigit()): type = 2
      
      state = table[state][type]
      self.idx+=1
    if(self.idx<len(self.code) and self.code[self.idx] == '§'):
      self.debugger(2)
      return "", "$"
    if state == 1:
      self.idx-=1
      return self.handle_token(lexeme, "IDENTIFIER")
    else:
      print(self.code[self.idx-1])
      print("b")
      self.debugger(1)
      return "", "$"


  def DFAStringVal(self, state):    
    # NFA ALPHABET (COLUMN)
    # (0) "
    # (1) \
    # (2) §
    # (3) other symbols

    table = [
              [1,6,6,6],
              [5,2,6,3],  
              [4,4,6,6],
              [5,2,6,3],
              [5,2,6,3],  
              [6,6,6,6],
              [6,6,6,6],
            ]
    
    stop_chars = {"§"}
    lexeme = ""
    while self.idx < len(self.code) and self.code[self.idx] not in stop_chars:
      type = 3
      current = self.code[self.idx]
      if state == 5 and current in " ;{}()<>,§+-*=":
        self.idx-=1
        break
      lexeme+=current
      if(current == "\""): type = 0
      elif(current == "\\"): type = 1
      elif(current == "§"): type = 2
      
      state = table[state][type]
      self.idx+=1

    if(self.idx<len(self.code) and self.code[self.idx] == '§'):
      self.debugger(2)
      return "", "$"
    if state == 5: return self.handle_token(lexeme, "STRING_LITERAL")
    else: 
      print("c")
      self.debugger(1)
      return "", "$"

  def DFAIntVal(self, state):
    char = self.code[self.idx]
    while(self.idx < len(self.code) and char == " "):
      self.idx+=1
      char = self.code[self.idx]
    
    # NFA ALPHABET (COLUMN)
    # (0) number
    # (1) other symbols

    table = [
              [1,2],
              [1,2],  
              [2,2]
            ]
    
    lexeme = ""
    # stop_chars = " ;\"{}()<>,§+-*/="
    while self.idx < len(self.code) and self.code[self.idx].isdigit():
      type = 1
      current = self.code[self.idx]
      lexeme+=current
      if(current.isdigit()): type = 0
      
      state = table[state][type]
      self.idx+=1
    
    if(self.idx<len(self.code) and self.code[self.idx] == '§'):
      self.debugger(2)
      return "", "$"
    if state == 1:
      self.idx-=1
      return self.handle_token(lexeme, "INTEGER_LITERAL")
    else:
      print("d")
      self.debugger(1)
      return "", "$"

  def scanner(self):
    char = self.code[self.idx]
    while(self.idx < len(self.code) and (char == " " or char == "\n" or char == "\t")):
      if(char == "\n"): self.line+=1
      self.idx+=1
      if self.idx < len(self.code): char = self.code[self.idx]
    if self.idx >= len(self.code):
      print("No more tokens")
      return "","done"
    if char == '§':
      self.debugger(2)
      return "", "$"    
    if char == ";": return self.handle_token(";", "SEMICOLON")
    if char == "(": return self.handle_token("(", "OPEN_PARENTHESIS")
    if char == ")": return self.handle_token(")", "CLOSE_PARENTHESIS")
    if char == "{": return self.handle_token("{", "OPEN_CURLY_BRACES")
    if char == "}": return self.handle_token("}", "CLOSE_CURLY_BRACES")
    if char == "<": return self.handle_token("<", "LESS_THAN")
    if char == ">": return self.handle_token(">", "GREATER_THAN")
    if char == "=": return self.handle_token("=", "EQUAL")
    if char == ",": return self.handle_token(",", "COMMA")
    if char in "+-*/": return self.handle_token(char, "OPERATOR")

    return self.scanFSMs()


  def parser(self):
    while(self.idx < len(self.code) and input("Do you want a token? [yes(1)/no(0)]: ")):
      lexeme, token = self.scanner()
      print(f"line: {self.line}")
      if(self.line == 8):
        print(f"{self.idx} {len(self.code)}")
      if token[0]=='$' or token == "done":
        break
      print(f"Lexeme Received: {lexeme}\nToken Received: {token}\n")

code = '''clout num1,num2, result;
Sigma operation;
yap << " Input first number: ";
spill >> num1;
yap << " Input second number: ";
spill >> num2;
yap << " Choose an operation (+, -, *, /): ";
spill >> operation;
let him cook (operation == "+"){
  result = num1 + num2;
  yap << "Result: " << num1 << " + " << num2 << " = " << result << slay;
}
what if (operation == "-"){
  result = num1 - num2;
  yap << "Result: " << num1 << " - " << num2 << " = " << result << slay;
}
what if (operation == "*"){
  result = num1 * num2;
  yap << "Result: " << num1 << " * " << num2 << " = " << result << slay;
}
what if (operation == "/"){
  result = num1 / num2;
  yap << "Result: " << num1 << " / " << num2 << " = " << result << slay;
}
cooked {
  yap  << "Invalid operation";
  it's giving; // force to end the program
}'''

comp = Compiler(code)



