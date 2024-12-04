import re

class Compiler:
  def __init__(self, code):
    self.code = code
    self.idx = 0 
    self.line = 1
    self.stack = -1

    self.lexer_table = {}
    self.symbol_table = {}

    self.currentToken = self.currentLexeme = None


    self.mipsData = ".data\n"
    self.mipsCode = "\n.text\n.globl main\nmain:\n\n"
    self.subroutine = {}

    self.scope = 0
    self.scopeCounter = 0

    self.keepTranslating = True # turns false when it's giving is encountered outside if-else statements
    self.success = False

    self.terminalParsingResult = None

    self.hasRelationalOperator = False
    self.firstTerm = False
    self.secondTerm = False
    self.isInIf = False
    self.isInIfCondition = False
    self.hasElseIf = False
    self.hasElse = False
    self.ifCondition = ""
    self.ifConditionMips = ""
    self.ifMips = ""
    self.block = ""

    try:
      self.preprocessor()
      self.currentLexemeToken()
      self.parseProgram()
      self.success = True
    except SyntaxError as e:
      self.terminalParsingResult = f"{e}\n"
      print(f"Syntax error: {e}")
    
    self.print_lexer_table()
    print("\n\n")
    self.print_symbol_table()

    print("\n           MIPS\n")
    print(self.mipsData+self.mipsCode)
    for value in self.subroutine.values():
      print(value)
    print(f"\n# Exit the program\n\n# add flag § (167)\nli $a0, 167\nli $v0, 11\nsyscall\n# return code: 1\nli $v0, 1\nli $a0, 1\nsyscall\nli $v0, 10\nsyscall\n\n")
       
  def getFinalMIPS(self):
    self.mipsData+=self.mipsCode
    self.mipsData += f"\n# Exit the program\n\n# add flag § (167)\nli $a0, 167\nli $v0, 11\nsyscall\n# return code: 1\nli $v0, 1\nli $a0, 1\nsyscall\nli $v0, 10\nsyscall\n\n"
    for value in self.subroutine.values():
      self.mipsData+=value
    print(self.mipsData)
    return self.mipsData
  
  def print_lexer_table(self):
    # Print the table header
    print("           LEXER TABLE")
    print("-" * 45)
    print(f"{'LEXEME':<15} | {'TOKEN':<25}")
    print("-" * 45)
    for lexeme, token in self.lexer_table.items():
      print(f"{lexeme:<15} | {token:<25}")
      print("-" * 45)

  def print_symbol_table(self):
    print("           SYMBOL TABLE")
    print("-" * 55)
    print("VARIABLE        | SCOPE    | DATATYPE  | VALUE  | STACK")
    print("-" * 55)

    for (varName, scope), details in self.symbol_table.items():
      print(f"{varName:<16}| {scope:<9}| {details['datatype']:<10}| "
        f"{str(details['value']):<6}| {details['stack']}")
      print("-" * 55)

  def preprocessor(self): #delete comments
    # NFA ALPHABET (COLUMN)
    # (0) "
    # (1) /
    # (2) \n
    # (3) *
    # (4) other symbols

    table = [
              [1,2,0,0,0],
              [0,1,1,1,1],
              [0,3,0,5,0],
              [4,4,0,4,4],
              [4,4,0,4,4],
              [6,6,7,8,6],
              [6,6,7,8,6],
              [6,6,7,8,6],
              [6,9,7,8,6],
              [1,2,0,0,0]
            ]
    index = 0
    state = 0
    multipleCommentStart = None;
    while(index < len(self.code)):
      type = 4
      if self.code[index] == "\"": type = 0
      elif self.code[index] == "/": type = 1
      elif self.code[index] == "\n": type = 2
      elif self.code[index] == "*": type = 3
      state = table[state][type]
      if(state in [3, 5]):
        if state == 5:
          print("DIRI")
        self.code = self.code[:index] + self.code[index+1:]
        self.code = self.code[:index-1] + self.code[index:]
        index-=2
      if state in [4, 6, 8, 9]:
        self.code = self.code[:index] + self.code[index+1:]
        index-=1

      index+=1
    if state in [5, 6, 7, 8]:
      self.debugger(5)

    print(self.code)
    print(self.line)
    self.idx = 0

  def debugger(self, errorNumber, index=None):
    if index is None:
      index = self.idx
    print(self.code[self.idx-1])
    illegalChar = self.code[index]

    if(errorNumber == 3):
      # Scan left from the index until a space or the start of the string
      left = index
      while left > 0 and self.code[left - 1] not in '"':
        left -= 1

      # Scan right from the index until a space or the end of the string
      right = index
      while right < len(self.code) - 1 and self.code[right + 1] not in '"':
        right += 1

      word = self.code[left:right + 1]
      raise SyntaxError(f"Skibidi in Toilet {self.getLineError()}: Missing close quotation mark.")


    # Scan left from the index until a space or the start of the string
    left = index
    while left > 0 and self.code[left - 1] not in ' ,;\n\t':
      left -= 1

    # Scan right from the index until a space or the end of the string
    right = index
    while right < len(self.code) - 1 and self.code[right + 1] not in ' ,;\n\t':
      right += 1

    word = self.code[left:right + 1]

    if errorNumber == 1: # unexpected character
      if word == illegalChar: raise SyntaxError(f"Skibidi in toilet {self.line}: Unexpected rizz `{illegalChar}`.")
      else: raise SyntaxError(f"Skibidi in Toilet {self.getLineError()}: Unexpected rizz `{illegalChar}` in `{word}`.")
    if errorNumber == 2: # use of §
      if word == "§": raise SyntaxError(f"Skibidi in Toilet {self.line}: you can't rizz `§`.")
      else: raise SyntaxError(f"Skibidi in Toilet {self.getLineError()}: you can't rizz `§`. Yeet in `{word}`")
    if errorNumber == 4: # inavlid use of \
       raise SyntaxError(f"Skibidi in Toilet {self.getLineError()}: Invalid use of `\\` in `\\{self.code[self.idx]}`.")
    if errorNumber == 5: # Missing closing comment
       raise SyntaxError(f"Skibidi in Toilet {self.getLineError()}: Missing closing comment.")


  def handle_token(self, char, token_name):
    self.lexer_table[char] = token_name
    self.idx += 1
    return char, token_name

  def scanFSMs(self):
    print(f"line: {self.line}")
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
        "i": [7],
        "p": [15],
        "l": [44]
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
      },
      44:{
        "a": [45]
      },
      45:{
        "y": [46]
      }

    }

    stop_chars = " ;\"{}()<>,§+-*/!=\n"
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
    # print(f"lexeme: {lexeme}")
    # print(withTransition)
    # print(state)
    # print(f"curr: {self.code[self.idx]}")
    # print(self.code[self.idx] == "\"")
    if(self.idx<len(self.code) and self.code[self.idx] == '§'):
      self.debugger(2)
      return "", "$"
    if withTransition and state in {5, 10, 13, 18, 20, 23, 26, 28, 32, 34, 37, 43, 46}:
      self.idx-=1
      return self.handle_token(lexeme, lexeme.upper())
    # if withTransition and state == 5:
    #   self.idx-=1
    #   return self.handle_token(lexeme, "")
    # if withTransition and state == 10:
    #   self.idx-=1
    #   return self.handle_token(lexeme, "STRING")
    if self.idx<len(self.code) and (lexeme == "_" or lexeme.isalpha()):
      if not withTransition and self.code[self.idx] not in stop_chars:
        self.idx+=1
      return self.DFAVarName(1, lexeme)
    if not withTransition and "'" in lexeme:
      self.debugger(1, self.code[:self.idx+1].rfind("'"))
      return "", "$"
    if self.idx<len(self.code) and self.code[self.idx] == "\"":
      return self.DFAStringVal(0)
    elif self.idx<len(self.code) and self.code[self.idx] not in stop_chars and (lexeme.isdigit()):
      return self.DFAIntVal(0)
    else:
      if self.idx>=len(self.code):
        self.idx-=1
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
    
    stop_chars = " ;\"{}()<>,§+-*/!="
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
      self.debugger(1)
      return "", "$"

  def DFAStringVal(self, state):    
    # DFA ALPHABET (COLUMN)
    # (0) "
    # (1) \
    # (2) n
    # (3) t
    # (4) §
    # (5) other symbols

    table = [
              [1,6,6,6,6,6],
              [5,2,3,3,6,3],  
              [4,4,4,4,6,6],
              [5,2,3,3,6,3],
              [5,2,3,3,6,3],  
              [6,6,6,6,6,6],
              [6,6,6,6,6,6],
            ]
    
    stop_chars = {"§"}
    lexeme = ""
    while self.idx < len(self.code) and self.code[self.idx] not in stop_chars:
      type = 5
      current = self.code[self.idx]
      if state == 5 and current in " ;{}()<>,§+-*=\n":
        self.idx-=1
        break
      lexeme+=current
      if(current == "\""): type = 0
      elif(current == "\\"): type = 1
      elif(current == "n"): type = 2
      elif(current == "t"): type = 3
      elif(current == "§"): type = 4
      
      oldState = state
      state = table[state][type]
      if oldState == 2 and state == 6:
        self.debugger(4)
      self.idx+=1
    if(self.idx<len(self.code) and self.code[self.idx] == '§'):
      self.debugger(2)
      return "", "$"
    if state == 5: return self.handle_token(lexeme, "SIGMA_LITERAL")
    else:
      if(self.idx==len(self.code)):
        self.idx-=1
      self.debugger(3)
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
      return self.handle_token(lexeme, "CLOUT_LITERAL")
    else:
      self.debugger(1)
      return "", "$"

  def scanner(self):
    char = self.code[self.idx]
    print("Kuan")
    print(self.code)
    while(self.idx < len(self.code) and (char == " " or char == "\n" or char == "\t")):
      if(char == "\n"): 
        self.line+=1
      self.idx+=1
      if self.idx < len(self.code): char = self.code[self.idx]
    if self.idx >= len(self.code):
      # print("No more tokens")
      return "","$"
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
    if char == "!": return self.handle_token("!", "NOT")
    if char == ",": return self.handle_token(",", "COMMA")
    if char == "-": return self.handle_token("-", "MINUS")
    if char in "+": return self.handle_token(char, "PLUS")
    if char in "*": return self.handle_token(char, "MULTIPLY")
    if char in "/": return self.handle_token(char, "DIVIDE")

    return self.scanFSMs()

  def getLexemeToken(self):
    if(self.idx < len(self.code)):
      return self.scanner()
    else:
      return "", "$"
    
  def currentLexemeToken(self):
    if not self.currentLexeme and not self.currentToken:
      self.currentLexeme, self.currentToken = self.getLexemeToken()
  
  def match(self, token):
    if self.currentToken == token:
      self.currentLexeme = self.currentToken = ""
      self.currentLexemeToken()
    else:
      raise SyntaxError(f"Skibidi in Toilet {self.getLineError()}: Expected {token} but found {self.currentToken}")
############# SYMBOL TABLE #############
  def isInScope(self, varName):
    scope = self.scope
    if((varName, scope) in self.symbol_table or (varName, 0) in self.symbol_table):
      return True
    return False

  def insertSymbol(self, varName, datatype):
    if(self.scope>0):
      self.stack+=1
    self.symbol_table[varName, self.scope] = {"datatype": datatype, "value": False, "stack": self.stack}

  def isInSymbolTable(self, varName):
    self.getScope(varName)
  
  def updateSymbolTableValue(self, varName):
    scope = self.getScope(varName)
    self.symbol_table[varName, scope]["value"] = True
  
  def getScope(self, varName):
    scope = self.scope
    while(scope>=0): 
      if((varName, scope) in self.symbol_table):
        return scope
      scope-=1
    self.debugUndeclaredVariable(varName)

  def getType(self, varName):
    return self.symbol_table[varName, self.getScope(varName)]["datatype"]
  
  def getStackValue(self, varName):
    return self.symbol_table[varName, self.getScope(varName)]["stack"]
  
  def isValueAssigned(self, varName, varNameType):
    if(varNameType in ["SLAY", "CLOUT_LITERAL", "SIGMA_LITERAL"]):
      return
    if(self.symbol_table[varName, self.getScope(varName)]["value"] == None):
      self.debugNoValueAssigned(varName)

  def findVarName(self, lexeme, token):
    if(token == 'IDENTIFIER'):
      lexemeScope = self.getScope(lexeme)
      token = self.symbol_table[lexeme, lexemeScope]["datatype"]
    if(token in ['SIGMA', 'SIGMA_LITERAL', 'SLAY']):
      return "$a2", 'SIGMA', 
    if(token in ['CLOUT', 'CLOUT_LITERAL']):
      return "$a0", 'CLOUT'

    else:
      self.debugInvalidPrint(token)

  def countVarWithValue(self, inScope):
    count = 0
    for (varName, scope) in self.symbol_table:  
      if scope == inScope and self.symbol_table[varName, scope]["value"] == True:
        count += 1
    return count
    
  
############## TRANSLATORS #############
  def translateReturn(self):
    if(not self.keepTranslating): return 
    self.mipsCode += f"\n# end\n\n# add flag § (167)\nli $a0, 167\nli $v0, 11\nsyscall\n# return code: 1\nli $v0, 1\nli $a0, 1\nsyscall\nli $v0, 10\nsyscall\n\n"
    if(self.keepTranslating and self.stack==-1):
      self.keepTranslating = False
  
  def translateDeclaration(self, datatype, varName):
    if(self.getScope(varName) == 0):
      if (datatype == "CLOUT"):
        self.mipsData+=(f"{varName}: .word 0\n")
      elif (datatype == "SIGMA"):
        self.mipsData+=(f".align 2\n{varName}: .space 1024\n")

  def translateIntAssignment(self, varName, varName1, varName1Type):
    print("d2 b?")
    if not self.isInIf and not self.isInIfCondition:
      self.mipsCode+=f"\n# {varName} = {varName1}\n"
    elif self.isInIf and not self.isInIfCondition:
      self.ifMips+=f"\n# {varName} = {varName1}\n"
    firstLine = ""
    secondLine = ""
    if(varName1Type == "CLOUT_LITERAL"):
      if '$' in varName:
        if not self.isInIf and not self.isInIfCondition: 
          self.mipsCode+=f"li $a0, {varName1}\n"  
        elif self.isInIf and not self.isInIfCondition:
           self.ifMips+=f"li $a0, {varName1}\n"  
        return
      firstLine = f"li $t0, {varName1}\n"
    else:
      varName1Scope = self.getScope(varName1)
      varName1Stack = self.symbol_table[varName1, varName1Scope]["stack"]
      if(varName1Stack == -1): # global variable name
        if '$' in varName:
          if not self.isInIf and not self.isInIfCondition:
            self.mipsCode+=f"lw $a0, {varName1}\n"
          else:
            self.ifMips+=f"lw $a0, {varName1}\n"
          return  
        firstLine = f"lw $t0, {varName1}\n"
        print("ditetch")

      else:
        varName1Stack*=4
        if '$' in varName:
          if not self.isInIf and not self.isInIfCondition:
            self.mipsCode+=f"lw $a0, {varName1Stack}($sp)\n"
          else:
            self.ifMips+=f"lw $a0, {varName1Stack}($sp)\n"
          return  
        firstLine = f"lw $t0, {varName1Stack}($sp)\n"
    varNameScope = self.getScope(varName)
    varNameStack = self.symbol_table[varName, varNameScope]["stack"]
    if(varNameStack == -1): # global variable name
      # print(f"varname: {varName} self.stack: {self.stack}")
      secondLine = f"sw $t0, {varName}\n"
      print("ditetch")

    else:
      varNameStack*=4
      # print(f"varname: {varName} self.stack: {self.stack}")
      # print(self.symbol_table)
      secondLine = f"sw $t0, {varNameStack * 4}($sp)\n"
    if not self.isInIf and not self.isInIfCondition:
      self.mipsCode+=(firstLine+secondLine+"\n")
    else:
      self.ifMips+=(firstLine+secondLine+"\n")

  def translateString(self, assignedTo, strValue):
    storage = '$a0'
    if '$' in assignedTo:
      storage = assignedTo
    else:
      if not self.isInIf:
        self.mipsCode+=f"la $a0, {assignedTo}\n"
      else: 
        self.ifMips+=f"la $a0, {assignedTo}\n"
    stack = 0
    slash = 0
    for char in strValue:
      if(char == '\\' and not slash):
        slash = True
        continue
      if slash:
        if(char == '\\'):
          char == '\\'
          slash = False
        elif(char == 'n'):
          char = '\n'
          slash = False
        elif(char == 't'):
          char = '\t'
          slash = False
        elif(char == '\"'):
          char = '\"'
          slash = False
      comment = char
      if(char == '\n'): comment="\\n"
      if(char == '\t'): comment ="\\t"
      if(char == '\"'): comment ="\""

      if not self.isInIf:
        self.mipsCode+=f"li $t0, {ord(char)}\t# '{comment}'\nsb $t0, {stack}({storage})\n"
      else:
        self.ifMips+=f"li $t0, {ord(char)}\t# '{comment}'\nsb $t0, {stack}({storage})\n"
      stack+=1
    if not self.isInIf:
      self.mipsCode+=f"# add null terminator\nli $t0, 0\nsb $t0, {stack}({storage})\n\n"
    else:
      self.ifMips+=f"# add null terminator\nli $t0, 0\nsb $t0, {stack}({storage})\n\n"

  def copyString(self, source, copyTo): # copyTo = source
    if(not "string_copy" in self.subroutine):
      self.subroutine["string_copy"] = f"string_copy:\ncopy_loop:\nlb $t0, 0($a0)\nsb $t0, 0($a1)\nbeq $t0, $zero, copy_done\naddi $a0, $a0, 1\naddi $a1, $a1, 1\nj copy_loop\n\ncopy_done:\njr $ra\n"
    if '$' in copyTo:
      if not self.isInIf:
        self.mipsCode+=f"la $a0, {source}\nmove $a1, {copyTo}\njal string_copy\n\n"
      else:
        self.ifMips+=f"la $a0, {source}\nmove $a1, {copyTo}\njal string_copy\n\n"
    else:
      if not self.isInIf:
        self.mipsCode+=f"la $a0, {source}\nla $a1, {copyTo}\njal string_copy\n\n"
      else:
        self.ifMips+=f"la $a0, {source}\nla $a1, {copyTo}\njal string_copy\n\n"

  def translateStringAssigment(self, varName, varName1, varName1Type):
    filtered1 = varName1.replace('\n', '#')
    if not self.isInIf:
      self.mipsCode+=f"# {varName} = {filtered1}\n"
    else:
      self.ifMips+=f"# {varName} = {filtered1}\n"
    firstLine = ""
    secondLine = ""
    if(varName1Type == "SLAY"):
      if('$' in varName or self.getScope(varName) == 0):
        self.translateString(varName, '\\n')
        return
    elif (varName1Type == 'SIGMA_LITERAL'):
      if('$' in varName or self.getScope(varName) == 0):
        self.translateString(varName, varName1[1:-1])
        return
      return
    else:
      if('$' in varName or self.getScope(varName) == 0): # change this, this is both global
        self.copyString(varName1, varName)
        return
      return

  def translateIntComp(self, varName1, varName1Type, varName2, varName2Type, operator, varName3, varName3Type):
    if not self.isInIf:
      self.mipsCode+=f"# {varName1} = {varName2}{operator}{varName3}\n"
    elif self.isInIf:
      self.ifMips+=f"# {varName1} = {varName2}{operator}{varName3}\n"
    elif self.isInIfCondition:
      self.ifConditionMips+=f"# {varName1} = {varName2}{operator}{varName3}\n"
    if operator == '+': operator = 'add'
    if operator == '-': operator = 'sub'
    if operator == '*': operator = 'mul'
    if operator == '/': operator = 'div'
    varName1Scope = 0
    if not '$' in varName1:
      varName1Scope = self.getScope(varName1)
    varName2Scope = 'e'
    varName3Scope = 'e'
    print(f"type: {varName1Type}")
    print(f"scope: {varName2Type}")
    if varName2Type == 'IDENTIFIER':
      print("a")
      varName2Scope = self.getScope(varName2)
    if varName3Type == 'IDENTIFIER':
      print("b")
      varName3Scope = self.getScope(varName3)
    if varName2Scope != 'e':
      print("OOOOOOOOOOOO")
      if varName2Scope == 0:
        if not self.isInIf and not self.isInIfCondition:
          self.mipsCode+=f"lw $t0, {varName2}\n"
          print("or ditooo")
        else:
          self.ifMips += f"lw $t0, {varName2}\n"
    else:
      print("JJJJJJJJJJJJJJJ")
      if not self.isInIf or self.isInIfCondition:
        self.mipsCode+=f"li $t0, {int(varName2)}\n"
      # elif self.isInIfCondition:
      #   self.ifConditionMips+=f"li $t0, {int(varName2)}\n"
      elif self.isInIf: 
        self.ifMips+=f"li $t0, {int(varName2)}\n"
      
    
    print(f"SCCCC: {varName3Scope}")
    if varName3Scope != 'e':
      if varName3Scope == 0:
        if not self.isInIf and not self.isInIfCondition:
          self.mipsCode+=f"lw $t1, {varName3}\n"
        else:
          self.ifMips+=f"lw $t1, {varName3}\n"
    else:
      print("HEYYYY")
      if not self.isInIf or self.isInIfCondition:
        self.mipsCode+=f"li $t1, {int(varName3)}\n"
      # elif self.isInIfCondition:
      #   self.ifCondition+=f"li $t1, {int(varName3)}\n"
      elif self.isInIf:
        self.ifMips+=f"li $t1, {int(varName3)}\n"
      
    if operator == 'div':
      self.mipsCode+="# Check division by zero\nbeq $t1, $zero, division_by_zero\n"
      if(not "division_by_zero" in self.subroutine):
        self.subroutine["division_by_zero"] = "# Division by zero handling flag §\ndivision_by_zero:\nli $a0, 167\nli $v0, 11\nsyscall\n# return code: 2\nli $v0, 1\nli $a0, 2\nsyscall\nli $v0, 10\nsyscall\n\n"

        
      if '$' in varName1:
        if not self.isInIf or self.isInIfCondition:
          self.mipsCode+=f"div $t0, $t1\nmflo {varName1}\n"  
        # elif self.isInIfCondition:
        #   self.ifConditionMips+=f"div $t0, $t1\nmflo {varName1}\n"
        elif self.isInIf:
          self.ifMips+=f"div $t0, $t1\nmflo {varName1}\naddi $sp, $sp, -4\nsw $t2, 0($sp)\n"
        
      else:
        if not self.isInIf or self.isInIfCondition:
          self.mipsCode+=f"div $t0, $t1\nmflo $t2\n"
        else:
          self.ifMips+=f"div $t0, $t1\nmflo $t2\naddi $sp, $sp, -4\nsw $t2, 0($sp)\n"
    else:
      if '$' in varName1:
        if not self.isInIf or self.isInIfCondition:
          self.mipsCode+=f"{operator} {varName1}, $t0, $t1\n"
        # elif self.isInIfCondition:
        #   self.ifConditionMips+=f"{operator} {varName1}, $t0, $t1\n"
        elif self.isInIf:
          self.ifMips+=f"{operator} {varName1}, $t0, $t1\naddi $sp, $sp, -4\nsw $t2, 0($sp)\n"

      else:
        if not self.isInIf:
          self.mipsCode+=f"{operator} $t2, $t0, $t1\n"
        else:
          self.ifMips+=f"{operator} $t2, $t0, $t1\naddi $sp, $sp, -4\nsw $t2, 0($sp)\n"
    
    if varName1Scope == 0 and not '$' in varName1:
      self.mipsCode+=f"sw $t2, {varName1}\n\n"
    # elif self.isInIfCondition:
    #   self.mipsCode+=f"sw $t6, {varName1}\n\n"


  def translateStringtoA(self, strValue, n):
    if not self.isInIf and not self.isInIfCondition:
      self.mipsCode+=f"li $v0, 9\nli $a0, 1024\nsyscall\nmove $a{n}, $v0\n"
    elif self.isInIf and not self.isInIfCondition:
      # self.ifMips+="#2\n"
      self.ifMips+=f"li $v0, 9\nli $a0, 1024\nsyscall\nmove $a{n}, $v0\n"
    stack = 0
    slash = 0
    for char in strValue:
      if(char == '\\' and not slash):
        slash = True
        continue
      if slash:
        if(char == '\\'):
          char = '\\'
          slash = False
        elif(char == 'n'):
          char = '\n'
          slash = False
        elif(char == 't'):
          char = '\t'
          slash = False
        elif(char == '\"'):
          char = '\"'
          slash = False
      comment = char
      if(char == '\n'): comment="\\n"
      if(char == '\t'): comment ="\\t"
      if(char == '\"'): comment ="\""

      if not self.isInIf:
        self.mipsCode+=f"li $t1, {ord(char)}\t# '{comment}'\nsb $t1, {stack}($a{n})\n"
      else:
        self.ifMips+=f"li $t1, {ord(char)}\t# '{comment}'\nsb $t1, {stack}($a{n})\n"
      stack+=1
    if not self.isInIf:
      self.mipsCode+=f"# add null terminator\nli $t1, 0\nsb $t1, {stack}($a{n})\n\n"
    else:
      self.ifMips+=f"# add null terminator\nli $t1, 0\nsb $t1, {stack}($a{n})\n\n"

  def translateConcatenation(self):
    if(not "concat_strings" in self.subroutine):
      self.subroutine["concat_strings"] = "concat_strings:\ncopy_first:\nlb $t0, 0($a0)\nbeq $t0, $zero, copy_second\nsb $t0, 0($a2)\naddi $a0, $a0, 1\naddi $a2, $a2, 1\nj copy_first\n\ncopy_second:\nlb $t0, 0($a1)\nbeq $t0, $zero, concat_done\nsb $t0, 0($a2)\naddi $a1, $a1, 1\naddi $a2, $a2, 1\nj copy_second\n\nconcat_done:\nli $t0, 0\nsb $t0, 0($a2)\njr $ra\n"
    if not self.isInIf:
      self.mipsCode+=f"jal concat_strings\n"
    else:
      self.ifMips+=f"jal concat_strings\n"

  def translateStrComp(self, varName1, varName1Type, varName2, varName2Type, operator, varName3, varName3Type):
    print("!!!!!!!")
    print(varName2)
    print(varName2Type)
    filtered2 = varName2.replace('\n', '#')
    filtered3 = varName3.replace('\n', '#')
    if not self.isInIf:
      self.mipsCode+=f"# {varName1} = {filtered2}{operator}{filtered3}\n"
    else:
      self.ifMips+=f"# {varName1} = {filtered2}{operator}{filtered3}\n"
    #varName1Scope = self.getScope(varName1)
    varName2Scope = 'e'
    varName3Scope = 'e'
    if varName2Type == 'IDENTIFIER':
      varName2Scope = self.getScope(varName2)
    if varName3Type == 'IDENTIFIER':
      varName3Scope = self.getScope(varName3)

    if varName1 != '$a2':
      if not self.isInIf:
        self.mipsCode+=f"la $a2, {varName1}\n\n"
      else:
        self.ifMips+=f"la $a2, {varName1}\n\n"
    else:
      if not self.isInIf and not self.isInIfCondition:
        self.mipsCode+=f"li $v0, 9\nli $a0, 1024\nsyscall\nmove $a2, $v0\nmove $t2, $a2\n\n"
      elif self.isInIf and not self.isInIfCondition:
        # self.ifMips+="#3\n"
        self.ifMips+=f"li $v0, 9\nli $a0, 1024\nsyscall\nmove $a2, $v0\nmove $t2, $a2\n\n"

    if varName3Scope != 'e':
      if varName3Scope == 0:
        self.mipsCode+=f"la $a1, {varName3}\n"
    else:
      if(varName3 == 'slay'):
        self.translateStringtoA('\\n', 1)  
      else: self.translateStringtoA(varName3[1:-1], 1)

    if varName2Scope != 'e':
      if varName2Scope == 0:
        self.mipsCode+=f"la $a0, {varName2}\n"
    else:
      if(varName2 == 'slay'):
        self.translateStringtoA('\\n', 0)  
      else:
        self.translateStringtoA(varName2[1:-1], 0)

    self.translateConcatenation()
    
  def translateAssignment(self, varName1, varName1Type, varName2, varName2Type, operator, varName3, varName3Type):
    if(not operator):
      if(varName1Type == 'CLOUT'):
        self.translateIntAssignment(varName1, varName2, varName2Type)
      elif(varName1Type == 'SIGMA'):
        self.translateStringAssigment(varName1, varName2, varName2Type)
    elif operator:
      if(varName1Type == 'SIGMA' and operator != '+'):
        self.debugInvalidStringOperation(operator)
      if('$' not in varName1 and varName1 in [varName2, varName3] and self.isValueAssigned(varName1, varName1Type)):
        self.debugNoValueAssigned(varName1)
      if(varName3Type == 'CLOUT_LITERAL' and operator == '/' and int(varName3) == 0):
        self.debugDivisionbyZero()
      if(varName1Type == 'CLOUT'):
        self.translateIntComp(varName1, varName1Type, varName2, varName2Type, operator, varName3, varName3Type)
      if(varName1Type == 'SIGMA'):
        self.translateStrComp(varName1, varName1Type, varName2, varName2Type, operator, varName3, varName3Type)

############## DEBUGGERS ###############
  def getLineError(self):
    codeCopy = self.code
    lexeme = self.currentLexeme
    if lexeme == '$': lexeme = ''
    print(f"lexeme is: {lexeme}")
    index = codeCopy.rfind(lexeme)
    
    if index != -1:
      # Remove the last occurrence by slicing
      codeCopy = codeCopy[:index] + codeCopy[index + len(lexeme):]
    
    codeCopy = codeCopy.rstrip("\n\t")
    print(f"codeCopy is: {codeCopy}")
    return codeCopy.count('\n')+1
  
  
    # print(f"current lexeme: {self.currentLexeme}")
    # line_error = self.line
    # print(f"Line error: {line_error}\n")
    # index = self.idx
    # print(f"index: {index}, char: {self.code[index-1:]}")
    # # if self.code[index] == '\n':
    # #     print("naa dire")
    # # else:
    # #   print("wala dire")
    # if index >= len(self.code): index = len(self.code)-1
    # while(index >=0):
    #   if self.code[index] == '\n':
    #     print(f"naa dire: {self.code[index-1]}")
    #     line_error-=1
    #     index-=1
    #   elif self.code[index] in ' \t':
    #     index-=1
    #   else: break

    # return line_error

  def debugMissingDataType(self):
    raise SyntaxError(f"Skibidi in Toilet {self.getLineError()}: Expected data type.")
    
  def debugVariableRedeclaration(self, varName):
    raise SyntaxError(f"Skibidi in Toilet {self.getLineError()}: Redemption arc of {varName}.")
  
  def debugUndeclaredVariable(self, varName):
    raise SyntaxError(f"Skibidi in Toilet {self.getLineError()}: `{varName}` is not it.")
  
  def debugTypeMismatch(self, varName1, datatype1, varName2, datatype2):
    raise SyntaxError(f"Skibidi in Toilet {self.getLineError()}: Negative aura between`{varName1}`: {datatype1} and `{varName2}`: {datatype2}.")
  
  def debugInvalidValue(self):
    raise SyntaxError(f"Skibidi in Toilet {self.getLineError()}: Invalid fanum tax.")
  
  def debugNoValueAssigned(self, varName):
    raise SyntaxError(f"Skibidi in Toilet {self.getLineError()}: No huzz assigned to {varName}.")
  
  def debugNoOperator(self):
    raise SyntaxError(f"Skibidi in Toilet {self.getLineError()}: Rizzler expected.")

  def debugInvalidStringOperation(self, operator):
    raise SyntaxError(f"Skibidi in Toilet {self.getLineError()}: Rizzler `{operator}` not supported on sigma.")

  def debugDivisionbyZero(self):
    raise SyntaxError(f"Skibidi in Toilet {self.getLineError()}: Division by zero")
  
  def debugInvalidPrint(self, token):
    raise SyntaxError(f"Skibidi in Toilet {self.getLineError()}: {token} can't be yeeted")
  
  def debugUnexpectedKeyword(self, lexeme):
    raise SyntaxError(f"Skibidi in Toilet {self.getLineError()}: Unexpected rizz: {lexeme}.")

############## SEMANTIC ANALYZERS ###############
  def isSameType(self, varName, firstTermLexeme, firstTermToken):
    varNameType = ""
    if varName not in ["CLOUT", "SIGMA"]:
      varNameType = self.symbol_table[varName, self.getScope(varName)]["datatype"]
    else: varNameType = varName
    if(varNameType == "CLOUT" and firstTermToken == "CLOUT_LITERAL"):
      return True
    if(varNameType == "SIGMA" and firstTermToken in ["SIGMA_LITERAL", "SLAY"]):
      return True
    if (varNameType in ["CLOUT", "SIGMA"] and firstTermToken != 'IDENTIFIER'):
      self.debugTypeMismatch(varName, varNameType, firstTermLexeme, firstTermToken)
    firstTermLexemeType = self.symbol_table[firstTermLexeme, self.getScope(firstTermLexeme)]["datatype"]
    if(varNameType == firstTermLexemeType):
      return True
    self.debugTypeMismatch(varName, varNameType, firstTermLexeme, firstTermLexemeType)

############## PARSERS ################
  def parseProgram(self):
    print(self.currentToken)
    # <Program> ::= <Statement> <Program> | 'SEMICOLON' <Program> | ε   
    if self.currentToken == "$":
      return
    if self.currentToken == 'SEMICOLON':
      self.match('SEMICOLON')
      self.parseProgram()
    elif self.currentToken in ['IDENTIFIER', 'CLOUT', 'SIGMA', 'IDENTIFIER', 'LET', 'YAP', 'SPILL', "IT'S"]:
      self.parseStatement()
      self.parseProgram()
    elif self.currentToken in ['SLAY', 'SIGMA_LITERAL', 'COOKED', 'CLOUT_LITERAL', 'WHAT', 'PLUS', 'MINUS', "MULTIPLY", "DIVIDE", "EQUAL", "NOT", "IF", "GREATER_THAN", "LESS_THAN", "OPEN_PARENTHESIS", "CLOSE_PARENTHESIS", "OPEN_CURLY_BRACE", "CLOSE_CURLY_BRACE"]:
      self.debugUnexpectedKeyword(self.currentLexeme)
    else: return # for ε

  def parseStatement(self):
    # <Statement> ::= <Declaration> | <Assignment> | <If> | <Print> | <Scan> | "IT'S" "GIVING" | "SEMICOLON"
    if self.currentToken in ['CLOUT', 'SIGMA']:
      self.parseDeclaration()
    elif self.currentToken == 'IDENTIFIER':
      self.parseAssignment()
    elif self.currentToken == 'LET':
      self.parseIf()
    elif self.currentToken == 'YAP':
      self.parsePrint()
    elif self.currentToken == 'SPILL':
      self.parseScan()
    elif self.currentToken == "IT'S":
      self.match("IT'S")
      self.match("GIVING")
      self.translateReturn()
    elif self.currentToken == 'SEMICOLON':
      self.match('SEMICOLON')
    else:
      self.debugUnexpectedKeyword(self.currentLexeme)

  def parseDeclaration(self):
    # <Declaration> ::= <Data_type> <Variable_list> 'SEMICOLON'
    datatype = self.parseDataType()
    self.parseVariableList(datatype)
    self.match('SEMICOLON')

  def parseDataType(self):
    # <Data_type> ::= 'CLOUT' | 'SIGMA'
    if self.currentToken == 'CLOUT':
      self.match('CLOUT')
      return 'CLOUT'
    elif self.currentToken == 'SIGMA':
      self.match('SIGMA')
      return 'SIGMA'
    else:
      self.debugMissingDataType()

  def parseVariableList(self, datatype):
    # <Variable_list> ::= <Variable> <Variable_list_prime>
    self.parseVariable(datatype)
    self.parseVariableListPrime(datatype)

  def parseVariable(self, datatype):
    print("HEHEHEHEHHEHEHEHEH")
    # <Variable> ::= 'IDENTIFIER' <Variable_prime>
    varName = self.currentLexeme
    self.match('IDENTIFIER')
    if self.isInScope(varName) and not self.isInIf:
      self.debugVariableRedeclaration(varName)
    else:
      print(f"meh: {self.stack} {self.scope}")
      self.insertSymbol(varName, datatype)
      self.translateDeclaration(datatype, varName)
    self.parsevariablePrime(varName)

  def parsevariablePrime(self, lexeme):
    # <Variable_prime> ::= 'EQUAL' <Expression> | ε
    if(self.currentToken == 'EQUAL'):
      self.match('EQUAL')
      self.parseExpression(lexeme)
      self.updateSymbolTableValue(lexeme)
    else: return  

  def parseExpression(self, varName=None):
    fromPrint = False
    # <Expression> ::= <Term><Expression_prime>
    firstTermLexeme, firstTermToken = self.parseTerm()
    print(f"First term: {firstTermLexeme}, {firstTermToken}")
    varNameType = varName
    if not varName:
      fromPrint = True
      varName, varNameType = self.findVarName(firstTermLexeme, firstTermToken)
    print("FIRST")
    self.isSameType(varNameType, firstTermLexeme, firstTermToken)
    print("SECOND")
    if(firstTermToken == 'IDENTIFIER' and self.symbol_table[firstTermLexeme, self.getScope(firstTermLexeme)]["value"] == False):
      self.debugNoValueAssigned(firstTermLexeme)
    operator, secondTermLexeme, secondTermToken = self.parseExpressionPrime()
    print(f"operator: {operator}")
    if(secondTermToken == 'IDENTIFIER' and self.symbol_table[secondTermLexeme, self.getScope(secondTermLexeme)]["value"] == False):
      self.debugNoValueAssigned(secondTermLexeme)
    print('third')
    if(operator):
      print("Naa")
      if firstTermLexeme == 'IDENTIFIER':
        self.isValueAssigned(firstTermLexeme, firstTermToken)
      if secondTermLexeme == 'IDENTIFIER':
        self.isValueAssigned(secondTermLexeme, secondTermToken)
      self.isSameType(varNameType, secondTermLexeme, secondTermToken)
    else:
      if not self.isInIf and not self.isInIfCondition:
        self.mipsCode+=f"li $v0, 9\nli $a0, 1024\nsyscall\nmove $a2, $v0\nmove $t2, $a2\n\n"
      elif self.isInIf and not self.isInIfCondition:
        # self.ifMips+="#4\n"
        self.ifMips+=f"li $v0, 9\nli $a0, 1024\nsyscall\nmove $a2, $v0\nmove $t2, $a2\n\n"
    print('Fourth')    
    if fromPrint:
      print('YEYEYEYEYEY')
      self.translateAssignment(varName, varNameType, firstTermLexeme, firstTermToken, operator, secondTermLexeme, secondTermToken)
      # print("end?")
    else:
      self.translateAssignment(varName, self.getType(varName), firstTermLexeme, firstTermToken, operator, secondTermLexeme, secondTermToken)
    if fromPrint:
      if(operator and not self.isInIf and not self.isInIfCondition):
        # if not self.isInIf:
        self.mipsCode+=f'\n# Print {firstTermToken}{operator}{secondTermToken}\n'
        # else:
        #   self.ifMips+=f'\n# Print {firstTermToken}{operator}{secondTermToken}\n'
      elif(not operator and not self.isInIf and not self.isInIfCondition):
        # if not self.isInIf:
        self.mipsCode+=f"\n# Print {firstTermToken}\n"
        # else:
        #   self.ifMips+=f"\n# Print {firstTermTokfen}\n"
      
      if(varName == '$a0'):
        if not self.isInIf and not self.isInIfCondition:
          self.mipsCode+=f"li $v0, 1\nsyscall\n\n"
        elif self.isInIf and not self.isInIfCondition:
          self.ifMips+=f"li $v0, 1\nsyscall\n\n"
      if(varName == '$a2'):
        if not self.isInIf:
          self.mipsCode+=f"move $a0, $t2\nli $v0, 4\nsyscall\n\n"
        else:
          self.ifMips+=f"move $a0, $t2\nli $v0, 4\nsyscall\n\n"
    print("here?")    
    if self.isInIfCondition:
      print("is it here?")
      if firstTermToken and secondTermToken and operator:
        print("in")
        # dataType1 = self.getType(firstTermLexeme)
        # dataType2 = self.getType(secondTermLexeme)
        # if firstTermToken == "IDENTIFIER" and secondTermToken == "IDENTIFIER":
        if ("CLOUT" in firstTermToken or "CLOUT" in self.getType(firstTermLexeme)) and ("CLOUT" in secondTermToken  or "CLOUT" in self.getType(secondTermLexeme)):
          if not self.firstTerm:
            self.translateIntComp(f"$t6", "register", firstTermLexeme, firstTermToken, operator, secondTermLexeme, secondTermToken)
            self.firstTerm = True
          else:
            self.translateIntComp(f"$t7", "register", firstTermLexeme, firstTermToken, operator, secondTermLexeme, secondTermToken)
            self.secondTerm = True
        
      elif not operator:
        if (firstTermToken == "IDENTIFIER"):
        # dataType = self.getType(firstTermLexeme)
        # print("here")
          if self.getType(firstTermLexeme) == "CLOUT":
            if not self.firstTerm:
              self.mipsCode += f"lw $t6, {firstTermLexeme}\n"
              self.firstTerm = True
            else:
              self.mipsCode += f"lw $t7, {firstTermLexeme}\n"
              self.secondTerm = True
        elif (firstTermToken == "CLOUT_LITERAL"):
          if not self.firstTerm:
            self.mipsCode += f"li $t6, {firstTermLexeme}\n"
            self.firstTerm = True
          else:
            self.mipsCode += f"li $t7, {firstTermLexeme}\n"
            self.secondTerm = True

    print("natapos b")

  
  def parseTerm(self):
    # <Term> ::= 'IDENTIFIER' | <Literal>
    if self.currentToken == 'IDENTIFIER' :
      lexeme = self.currentLexeme
      token = self.currentToken
      self.isInSymbolTable(lexeme)
      self.match('IDENTIFIER')
      return lexeme, token
    else:
      return self.parseLiteral()

  def parseLiteral(self):
    # <Literal> ::= 'MINUS' 'CLOUT_LITERAL' | 'CLOUT_LITERAL' | 'SIGMA_LITERAL' | 'SLAY'
    if self.currentToken == 'MINUS':
      self.match('MINUS')
      lexeme = self.currentLexeme
      token = self.currentToken
      self.match('CLOUT_LITERAL')
      return f"-{lexeme}", token
    if self.currentToken == 'CLOUT_LITERAL':
      lexeme = self.currentLexeme
      token = self.currentToken
      self.match('CLOUT_LITERAL')
      return lexeme, token
    if self.currentToken == 'SIGMA_LITERAL':
      lexeme = self.currentLexeme
      token = self.currentToken
      self.match('SIGMA_LITERAL')
      return lexeme, token
    if self.currentToken == 'SLAY':
      self.match('SLAY')
      return 'slay', 'SLAY'
    else: 
      self.debugInvalidValue()

  def parseExpressionPrime(self):
    # <Expression_prime> ::= <Operator> <Term> | ε
    if(self.currentToken in ['PLUS' , 'MINUS' , 'MULTIPLY' , 'DIVIDE']):
      operator = self.parseOperator()
      lexeme, token = self.parseTerm()
      return operator, lexeme, token
    else: return None, None, None

  def parseOperator(self):
    if(self.currentToken in ['PLUS' , 'MINUS' , 'MULTIPLY' , 'DIVIDE']):
      lexeme = self.currentLexeme
      self.match(self.currentToken)
      return lexeme
    else: 
      self.debugNoOperator()

  def parseVariableListPrime(self, datatype):
    # <Variable_list_prime> ::= 'COMMA' <Variable_list> | ε
    if(self.currentToken == 'COMMA'):
      self.match('COMMA')
      self.parseVariableList(datatype)
    else: return

  def parseAssignment(self):
    # <Assignment> ::= 'IDENTIFIER' 'EQUAL' <Expression> 'SEMICOLON'
    varName = self.currentLexeme
    self.match('IDENTIFIER')
    if not self.isInScope(varName):
      print("dito ba?")
      self.debugUndeclaredVariable(varName)
    self.match('EQUAL')
    self.updateSymbolTableValue(varName)
    # if self.isInIf:
    #   self.insertSymbol(varName, self.getType(varName))
    #   self.updateSymbolTableValue(varName)
    self.parseExpression(varName)
    self.match('SEMICOLON')

  def parsePrint(self):
    # <Print> ::= 'YAP' 'LESS_THAN' 'LESS_THAN' <Expression> 
    self.match('YAP')
    self.match('LESS_THAN')
    self.match('LESS_THAN')
    self.parseExpression()
    self.parsePrintPrime()
    self.match('SEMICOLON')

  def parsePrintPrime(self):
    # <Print_prime> ::= 'LESS_THAN' 'LESS_THAN' <Expression> <Print_prime>
    if(self.currentToken == 'LESS_THAN'):
      self.match('LESS_THAN')
      self.match('LESS_THAN')
      self.parseExpression()
      self.parsePrintPrime()
    else: return

  def parseScan(self):
    # <Scan> ::= 'SPILL' 'GREATER_THAN' 'GREATER_THAN' <IDENTIFIER> ';'
    self.match('SPILL')
    self.match('GREATER_THAN')
    self.match('GREATER_THAN')
    lexeme = self.currentLexeme
    self.match('IDENTIFIER')
    self.isInSymbolTable(lexeme)
    self.updateSymbolTableValue(lexeme)
    
    if(self.getType(lexeme) == "CLOUT"):
      if not self.isInIf:
        self.mipsCode+=f"\n# add scanning flag § (167)\nli $a0, 167\nli $v0, 11\nsyscall\n# return code: 0\nli $v0, 1\nli $a0, 0\nsyscall\n\n# scan {lexeme}\nli $v0, 5\nsyscall\nsw $v0, {lexeme}\n"
      else:
        self.ifMips+=f"\n# add scanning flag § (167)\nli $a0, 167\nli $v0, 11\nsyscall\n# return code: 0\nli $v0, 1\nli $a0, 0\nsyscall\n\n# scan {lexeme}\nli $v0, 5\nsyscall\nsw $v0, {lexeme}\n"
    if(self.getType(lexeme) == "SIGMA"):
      if not self.isInIf:
        self.mipsCode+=f"\n# add scanning flag § (167)\nli $a0, 167\nli $v0, 11\nsyscall\n# return code: 0\nli $v0, 1\nli $a0, 0\nsyscall\n\n# scan {lexeme}\nli $v0, 8\nla $a0, {lexeme}\nli $a1, 1024\nsyscall\n# Remove newline from {lexeme}\nla $a0, {lexeme}\njal remove_newline\n"
      else:
        self.ifMips+=f"\n# add scanning flag § (167)\nli $a0, 167\nli $v0, 11\nsyscall\n# return code: 0\nli $v0, 1\nli $a0, 0\nsyscall\n\n# scan {lexeme}\nli $v0, 8\nla $a0, {lexeme}\nli $a1, 1024\nsyscall\n# Remove newline from {lexeme}\nla $a0, {lexeme}\njal remove_newline\n"
      if(not "remove_newline" in self.subroutine):
        self.subroutine["remove_newline"] = f"\nremove_newline:\nlb $t0, 0($a0)\nbeq $t0, $zero, done\nli $t1, 10\nbeq $t0, $t1, replace\naddi $a0, $a0, 1\nj remove_newline\n\nreplace:\nli $t0, 0\nsb $t0, 0($a0)\n\ndone:\njr $ra\n\n"
    self.parseScanPrime()
    self.match('SEMICOLON')

  def parseScanPrime(self):
    # <Scan_prime> ::= 'GREATER_THAN' 'GREATER_THAN' 'IDENTIFIER' | ε
    if(self.currentToken == 'GREATER_THAN'):
      self.match('GREATER_THAN')
      self.match('GREATER_THAN')
      lexeme = self.currentLexeme
      self.match('IDENTIFIER')
      self.isInSymbolTable(lexeme)
      self.updateSymbolTableValue(lexeme)
      if(self.getType(lexeme) == "CLOUT"):
        if not self.isInIf:
          self.mipsCode+=f"\n# add scanning flag § (167)\nli $a0, 167\nli $v0, 11\nsyscall\n# return code: 0\nli $v0, 1\nli $a0, 0\nsyscall\n\n# scan {lexeme}\nli $v0, 5\nsyscall\nsw $v0, {lexeme}\n"
        else:
          self.ifMips+=f"\n# add scanning flag § (167)\nli $a0, 167\nli $v0, 11\nsyscall\n# return code: 0\nli $v0, 1\nli $a0, 0\nsyscall\n\n# scan {lexeme}\nli $v0, 5\nsyscall\nsw $v0, {lexeme}\n"
      if(self.getType(lexeme) == "SIGMA"):
        if not self.isInIf:
          self.mipsCode+=f"\n# add scanning flag § (167)\nli $a0, 167\nli $v0, 11\nsyscall\n# return code: 0\nli $v0, 1\nli $a0, 0\nsyscall\n\n# scan {lexeme}\nli $v0, 8\nla $a0, {lexeme}\nli $a1, 1024\nsyscall\n"
        else:
          self.ifMips+=f"\n# add scanning flag § (167)\nli $a0, 167\nli $v0, 11\nsyscall\n# return code: 0\nli $v0, 1\nli $a0, 0\nsyscall\n\n# scan {lexeme}\nli $v0, 8\nla $a0, {lexeme}\nli $a1, 1024\nsyscall\n"
      self.parseScanPrime()
    else: return

  def parseIf(self):
    #<If> ::= 'LET' 'HIM' 'COOK' <Condition> <Block> <Else_if> <Else>
    self.match('LET')
    self.match('HIM')
    self.match('COOK')
    self.isInIf = True
    self.block = "IF"
    self.ifMips += f"\n{self.block}{self.scope}:\n"
    self.parseCondition()
    self.parseBlock()
    self.parseElseIf()
    self.parseElse()
    if not self.hasElse:
      self.mipsCode += "j END_IF"
    self.mipsCode += f"\n{self.ifMips}\n\nEND_IF:\n"
    self.scope = 0
    self.isInIf = False
    self.hasElseIf = False
    self.hasElse = False
    self.ifConditionMips = ""
    self.ifMips = ""
    self.block = ""

  def parseElseIf(self):
    #<Else_if> ::= 'WHAT' 'IF' <Condition> <Block> <Else_if> | ε
    if(self.currentToken == 'WHAT'):
      self.match('WHAT')
      self.match('IF')
      self.block = "ELSE_IF"
      self.hasElseIf = True
      self.ifMips += f"\n{self.block}{self.scope}:\n"
      self.parseCondition()
      self.parseBlock()
      self.parseElseIf()
    else: return

  def parseElse(self):
    # <Else> ::= 'COOKED' <Block> | ε
    if(self.currentToken == 'COOKED'):
      self.match('COOKED')
      self.block = "ELSE"
      self.hasElse = True
      self.ifMips += f"\n{self.block}{self.scope}:\n"
      self.mipsCode += f"j {self.block}{self.scope}"
      self.parseBlock()
    else: return

  def parseCondition(self):
    # <Condition> ::= 'OPEN_PARENTHESIS' <Expression> (<Relational_operator> <Expression> | ε) 'CLOSE_PARENTHESIS'
    self.match('OPEN_PARENTHESIS')
    self.isInIfCondition = True
    self.parseExpression()
    if(self.currentToken in ['EQUAL' , 'LESS_THAN' , 'GREATER_THAN' , 'NOT']):
      self.hasRelationalOperator = True
      self.parseRelationalOperator()
      self.parseExpression()
    if self.firstTerm and self.secondTerm:
      self.mipsCode += f"{self.ifCondition} $t6, $t7, {self.block}{self.scope}\n"
    else:
      self.mipsCode += f"bne $t6, $zero, {self.block}{self.scope}\n"
    self.match('CLOSE_PARENTHESIS')
    self.ifCondition = ""
    self.isInIfCondition = False
    self.hasRelationalOperator = False
    self.firstTerm = False
    self.secondTerm = False

  def parseRelationalOperator(self):
    # <Relational_operator> ::= 'EQUAL' 'EQUAL' | <Less> | 'NOT' 'EQUAL' | <Great>
    if(self.currentToken == 'EQUAL'):
      self.match('EQUAL')
      self.match('EQUAL')
      self.ifCondition += "beq"
    elif(self.currentToken == 'LESS_THAN'):
      self.parseLess()
    elif(self.currentToken == 'NOT'):
      self.match('NOT')
      self.match('EQUAL')
      self.ifCondition += "bne"
    elif(self.currentToken == 'GREATER_THAN'):
      self.parseGreat()

  def parseLess(self):
    # <Less> ::= 'LESS_THAN' <Relational_prime>
    self.match('LESS_THAN')
    self.ifCondition += "bl"
    self.parseRelationalPrime()

  def parseGreat(self):
    # <Great> ::= 'GREATER_THAN' <Relational_prime>
    self.match('GREATER_THAN')
    self.ifCondition += "bg"
    self.parseRelationalPrime()
  
  def parseRelationalPrime(self):
    # <Relational_prime> ::= 'EQUAL' | ε
    if(self.currentToken == 'EQUAL'):
      self.match('EQUAL')
      self.ifCondition += "e"
    else: 
      self.ifCondition += "t"
      return

  def parseBlock(self):
    self.scopeCounter+=1
    self.scope = self.scopeCounter
    # <Block> ::= 'OPEN_CURLY_BRACE' <Program> 'CLOSE_CURLY_BRACE' | <Statement>
    if(self.currentToken == 'OPEN_CURLY_BRACES'):
      self.match('OPEN_CURLY_BRACES')
      self.parseBlockProgram()
      self.match('CLOSE_CURLY_BRACES')
    else:
      self.parseBlockStatement()
    c = self.countVarWithValue(self.scope)
    if (c != 0):
      self.ifMips += f"addi $sp, $sp, {c * 4}\n"
    self.ifMips += f"j END_IF\n"
    self.stack = -1 # MIPS stack should be empty here
    

  def parseBlockProgram(self):
    # <Block_program> ::= <Block_statement> <Block_program> | 'SEMICOLON' <Block_program> | ε
    if self.currentToken == "$":
      return
    if self.currentToken == 'SEMICOLON':
      self.match('SEMICOLON')
      self.parseBlockProgram()
    elif self.currentToken in ['IDENTIFIER', 'CLOUT', 'SIGMA', 'IDENTIFIER', 'YAP', 'SPILL', "IT'S"]:
      self.parseBlockStatement()
      self.parseBlockProgram()
    elif self.currentToken in ['LET', 'SLAY', 'SIGMA_LITERAL', 'COOKED', 'CLOUT_LITERAL', 'WHAT', 'PLUS', 'MINUS', "MULTIPLY", "DIVIDE", "EQUAL", "NOT", "IF", "GREATER_THAN", "LESS_THAN", "OPEN_PARENTHESIS", "CLOSE_PARENTHESIS", "OPEN_CURLY_BRACE", "CLOSE_CURLY_BRACE"]:
      self.debugUnexpectedKeyword(self.currentLexeme)
    else: return # for ε

  def parseBlockStatement(self):
    # <Block_statement> ::= <Declaration> | <Assignment> | <Print> | <Scan> | "IT'S" "GIVING" | "SEMICOLON"
    if self.currentToken in ['CLOUT', 'SIGMA']:
      self.parseDeclaration()
    elif self.currentToken == 'IDENTIFIER':
      self.parseAssignment()
    elif self.currentToken == 'YAP':
      self.parsePrint()
    elif self.currentToken == 'SPILL':
      self.parseScan()
    elif self.currentToken == "IT'S":
      self.match("IT'S")
      self.match("GIVING")
      self.translateReturn()
    elif self.currentToken == 'SEMICOLON':
      self.match('SEMICOLON')
    else:
      self.debugUnexpectedKeyword(self.currentLexeme)