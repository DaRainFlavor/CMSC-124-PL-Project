class Compiler:
  def __init__(self, code):
    self.mipsCode = "\n.text\n.globl main\nmain:\n"
    self.stack = -1; # -1 means global or not inside any ifs
       
    self.symbol_table = { 
      # (lexeme, line) : {datatype, value, stack}
      ('a', 5): {'datatype': 'CLOUT', 'value': True, 'stack': -1},
      ('b', 6): {'datatype': 'CLOUT', 'value': True, 'stack': -1},
      ('a', 6): {'datatype': 'CLOUT', 'value': True, 'stack': None},
    }

  def mipsStack(self, lexeme): # updates the stack in symbol table and mipsCode # does not return anything
    pass

  def isDeclared(self, lexeme): # print "{lexeme} undeclared" if not declared # return the stack number if declared else return none
    pass

  def parseProgram(self):
    # <Program> ::= <Statement> <Program> | 'SEMICOLON' <Program> | ε    
    if self.currentToken == "$":
      return
    if self.currentToken == 'SEMICOLON':
      self.match('SEMICOLON')
      self.parseProgram()
    elif self.currentToken in ['IDENTIFIER', 'CLOUT', 'SIGMA', 'IDENTIFIER', 'LET', 'YAP', 'SPILL', "IT'S"]:
      self.parseStatement()
      self.parseProgram()
    else: return

  def parseStatement(self):
    # <Statement> ::= <Declaration> | <Assignment> | <If> | <Print> | <Scan> | "IT'S" "GIVING" 
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
      self.mipsCode += f"\n# end\nli $v0, 10\nsyscall"

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
    elif self.current_token().type == 'SIGMA':
      self.match('SIGMA')
      return 'SIGMA'
    else:
      raise SyntaxError("Expected data type 'CLOUT' or 'SIGMA'")

  def parseVariableList(self, datatype):
    # <Variable_list> ::= <Variable> <Variable_list_prime>
    # if(self.currentToken == 'IDENTIFIER'):
      self.parseVariable(datatype)
      self.parseVariableListPrime(datatype)
    # else: raise SyntaxError(f"Error in line {self.line}: Expected identifier.")

  def parseVariableListPrime(self, datatype):
    # <Variable_list_prime> ::= 'COMMA' <Variable_list> | ε
    if(self.currentToken == 'COMMA'):
      self.match('COMMA')
      self.parseVariableList(datatype)
    else: return

  def parseVariable(self, datatype):
    # <Variable> ::= 'IDENTIFIER' <Variable_prime>
    lexeme = self.currentLexeme
    self.match('IDENTIFIER')
    if (lexeme, self.scope) in self.symbol_table:
      raise SyntaxError(f"Error in line {self.line}: Redeclaration of {lexeme}")
    else:
      self.symbol_table[lexeme, self.scope] = {"datatype": datatype, "value": None, "stack": self.stack}
      if (datatype == "CLOUT"):
        self.mipsData+=(f"{lexeme}: .word 0\n")
      
    self.parsevariablePrime(lexeme)

  def parsevariablePrime(self, lexeme):
    # <Variable_prime> ::= 'EQUAL' <Expression> | ε
    if(self.currentToken == 'EQUAL'):
      self.match('EQUAL')
      self.symbol_table[lexeme, self.scope]["value"] = 1
      self.parseExpression(lexeme)
    else: return
  


  def parseExpression(self, lexeme=None): # MUST return a list of expressions
    # if it is from print then lexeme should be equal to the firstTermLexeme
    firstTermLexeme, firstTermToken = self.parseTerm()
    nullParam = False
    if(lexeme is None):
      lexeme = firstTermLexeme
      nullParam = True
    lexemeType = self.symbol_table[lexeme, self.scope]["datatype"]
    if self.symbol_table[lexeme, self.scope]["value"] is None:
      raise SyntaxError(f"Error in line {self.line}: {lexeme} is undefined.")
    if(self.symbol_table[lexeme, self.scope]["datatype"] != "CLOUT"):
      if (firstTermToken == "INTEGER_LITERAL"):
        raise SyntaxError(f"Error in line {self.line}: Type mismatch among {lexeme} and {firstTermLexeme}")
      elif(self.symbol_table[firstTermLexeme, self.scope]["datatype"] == "CLOUT"):
        raise SyntaxError(f"Error in line {self.line}: Type mismatch among {lexeme} and {firstTermLexeme}")
      
    operator, secondTermLexeme, secondTermToken = self.parseExpressionPrime()
    self.symbol_table[lexeme, self.scope]["value"] = 1
    if(operator is None):
      if(firstTermToken == "IDENTIFIER"):
        if(self.symbol_table[firstTermLexeme, self.scope]["value"] == None):
          raise SyntaxError(f"Error in line {self.line}: {firstTermLexeme} is undefined.")
        if(nullParam):
          self.mipsCode+=f"\n# print {firstTermLexeme}\nlw $a0, {firstTermLexeme}\nli $v0, 1\nsyscall\n"
        else:
          self.mipsCode+=f"\n# {lexeme} = {firstTermLexeme}\nli $t0, {firstTermLexeme}\nsw $t0, {lexeme}\n"
      elif(firstTermToken in ['INTEGER_LITERAL' , 'STRING_LITERAL', 'SLAY']):
        if(firstTermToken == 'INTEGER_LITERAL'):
          if(nullParam):
            self.mipsCode+=f"\n# print {int(firstTermLexeme)}\nlw $a0, {int(firstTermLexeme)}\nli $v0, 1\nsycall\n"
          else:
            self.mipsCode+=f"\n# {lexeme} = {int(firstTermLexeme)}\nli $t0, {int(firstTermLexeme)}\nsw $t0, {lexeme}\n"
    elif(self.symbol_table[lexeme, self.scope]["datatype"] != "CLOUT"):
      if (secondTermToken == "INTEGER_LITERAL"):
        raise SyntaxError(f"Error in line {self.line}: Type mismatch among {lexeme} and {secondTermLexeme}")
      elif(self.symbol_table[secondTermLexeme, self.scope]["datatype"] == "CLOUT"):
        raise SyntaxError(f"Error in line {self.line}: Type mismatch among {lexeme} and {secondTermLexeme}")
    if(operator == "PLUS"):
      if nullParam: self.mipsCode+=f"\n# {firstTermLexeme} + {secondTermLexeme}"
      else: self.mipsCode+=f"\n# {lexeme} = {firstTermLexeme} + {secondTermLexeme}"
      self.mipsCode+=f"\nlw $t0, {firstTermLexeme}\nlw $t1, {secondTermLexeme}\n"
      if self.symbol_table[lexeme, self.scope]["datatype"] == "CLOUT":
        self.mipsCode+=f"\nadd $t2, $t0, $t1\n"
        if nullParam:
          self.mipsCode+=f"move $a0, $t2\nli $v0, 1\nsyscall\n"
        else:
          self.mipsCode+=f"sw $t2, {lexeme}\n"
    if(operator == "DIVIDE"):
      if(int(secondTermLexeme) == 0):
        raise SyntaxError(f"Error in line {self.line}: Division by zero.")
      pass

  def parseExpressionPrime(self):
    if(self.currentToken in ['PLUS' , 'MINUS' , 'MULTIPLY' , 'DIVIDE']):
      operator = self.parseOperator()
      lexeme, token = self.parseTerm()
      return operator, lexeme, token
    else: return None, None, None

  def parseOperator(self):
    if(self.currentToken in ['PLUS' , 'MINUS' , 'MULTIPLY' , 'DIVIDE']):
      token = self.currentToken
      self.match(self.currentToken)
      return token
    else: raise SyntaxError(f"Error in line {self.line}: Expected Operator in line {self.line}.") 

  def parseTerm(self):
    if self.currentToken == 'IDENTIFIER' :
      if (self.currentLexeme, self.scope) not in self.symbol_table:
        raise SyntaxError(f"Error in line {self.line}: {self.currentLexeme} is not declared.")
      lexeme = self.currentLexeme
      token = self.currentToken
      self.match('IDENTIFIER')
      return lexeme, token
    else:
      return self.parseLiteral()
    
  def parseLiteral(self):
    # <Literal> ::= 'INTEGER_LITERAL' | 'STRING_LITERAL' | 'SLAY'
    if self.currentToken == 'INTEGER_LITERAL':
      lexeme = self.currentLexeme
      token = self.currentToken
      self.match('INTEGER_LITERAL')
      return lexeme, token
    if self.currentToken == 'STRING_LITERAL':
      lexeme = self.currentToken
      token = self.currentToken
      self.match('STRING_LITERAL')
      return lexeme, token
    if self.currentToken == 'SLAY':
      self.match('SLAY')
      return None, 'SLAY'
    else: raise SyntaxError(f"Error in line {self.line}: Value expected.")

  def parseAssignment(self):
    # <Assignment> ::= 'IDENTIFIER' '=' <Expression> 'SEMICOLON'
    lexeme = self.currentLexeme
    self.match('IDENTIFIER')
    if (lexeme, self.scope) not in self.symbol_table:
      raise SyntaxError(f"Error in line {self.line}: {lexeme} is not declared.")
    self.match('EQUAL')
    self.symbol_table[lexeme, self.scope]["value"] = 1
    self.parseExpression(lexeme)
    self.match('SEMICOLON')


  def parseIf(self):
    pass

  def parsePrint(self):
    self.match('YAP')
    self.match('LESS_THAN')
    self.match('LESS_THAN')
    self.parseExpression()
    self.parsePrintPrime()
    self.match('SEMICOLON')

  def parsePrintPrime(self):
    if(self.currentToken == 'LESS_THAN'):
      self.match('LESS_THAN')
      self.match('LESS_THAN')
      self.parseExpression()
      self.parsePrintPrime()
    else: return


  def parseScan(self):
    print("Hey")
    # <Scan> ::= 'SPILL' '<' '<' <IDENTIFIER> ';'
    self.match('SPILL')
    self.match('GREATER_THAN')
    self.match('GREATER_THAN')
    lexeme = self.currentLexeme
    token = self.currentToken
    self.match(token)
    if (lexeme, self.scope) not in self.symbol_table:
      raise SyntaxError(f"Error in line {self.line}: {lexeme} is not declared.")
    
    self.symbol_table[lexeme, self.scope]["value"] = 1
    print(f"Hello {lexeme}")
    print(self.symbol_table)
    if(self.symbol_table[lexeme, self.scope]["datatype"] == "CLOUT"):
      self.mipsCode+=f"\n# add scanning flag\nla $a0, scanFlag\nli $v0, 4\nsyscall\n\n# scan {lexeme}\nli $v0, 5\nsyscall\nsw $v0, {lexeme}\n"
    self.parseScanPrime()
    self.match('SEMICOLON')

  def parseScanPrime(self):
    if(self.currentToken == 'GREATER_THAN'):
      self.match('GREATER_THAN')
      self.match('GREATER_THAN')
      lexeme = self.currentLexeme
      token = self.currentToken
      self.match('IDENTIFIER')
      self.symbol_table[lexeme, self.scope]["value"] = 1
      if (lexeme, self.scope) not in self.symbol_table:
        raise SyntaxError(f"Error in line {self.line}: {lexeme} is not declared.")
      self.symbol_table[lexeme, self.scope]["value"] == 1
      if(self.symbol_table[lexeme, self.scope]["datatype"] == "CLOUT"):
        self.mipsCode+=f"\n# add scanning flag\nla $a0, scanFlag\nli $v0, 4\nsyscall\n\n# scan {lexeme}\nli $v0, 5\nsyscall\nsw $v0, {lexeme}\n"
      self.parseScanPrime()
    else: return
