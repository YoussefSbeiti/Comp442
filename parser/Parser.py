from Lexer.Lexer import Lexer
import json
from tabulate import tabulate
import re
from types import SimpleNamespace

class Parser:
    def __init__(self , grammar, srcPath):
        lexer = Lexer()
        lexer.build()
        self.lexer = lexer.lexer
        self.lexer.lineno += 1
        
        file = open(srcPath , 'r')
        self.lexer.input(file.read())
        file.close()

        self.grammar = grammar
        self.table = {}

        #delete contents of wrror file
        open("errors.txt", "w").close()

    def _lex(self, outfile):
        # Tokenize
        file = open(outfile , 'w+')
        while True:
            tok = self.lexer.token()
            if not tok: 
                break      # No more input
            file.write(tok.type)
        file.close()
    
    def nextToken(self):
        
        tok = self.lexer.token() 
        token = SimpleNamespace()
        token.value = 'EOF'
        token.type = '$'
        if tok:
            if 'COMMENT' in tok.type:
                 tok = self.nextToken()
            return tok
    
        else: return token

    def generateParseTable(self):
         for rule in self.grammar.rules:
            if rule['LHS'] not in self.table.keys():
                self.table[rule['LHS']] = {}
            rhs = rule['RHS']
            rhsFirst = self.grammar.getFirstFromRHS(rhs)
            for terminal in rhsFirst:
                if terminal != 'EPSILON':
                    self.table[rule['LHS']][terminal] = rule
                    #print('created entry<' + rule['LHS'] +', ' + terminal +'> = ' + str(rule) )

            if 'EPSILON' in self.grammar.getFirstFromRHS(rule['RHS']):
                for terminal in self.grammar.followSets[rule['LHS']]:
                    self.table[rule['LHS']][terminal] = rule
                    #print('created entry<' + rule['LHS'] +', ' + terminal +'> = ' + str(rule) )
            
            
            for terminal in self.grammar.terminals:
                if terminal not in self.table[rule['LHS']].keys():
                    self.table[rule['LHS']][terminal] = 'empty'

    def printParseTableHTML(self):
        
        print(sorted(self.grammar.terminals))
        rows = []
        for nt, row in self.table.items():
            rowlst = [nt]
            
            for terminal in sorted(row.keys()):
                ruleStr = terminal + '|| empty'
                rule = self.table[nt][terminal]
                if rule != 'empty':
                    ruleStr = terminal + "||" + rule['LHS'] + "->" + rule['RHS']
                    ruleStr = ruleStr.replace(">" , "&gt;").replace("<" , "&lt;")
                rowlst.append(ruleStr)
            rows.append(rowlst)
        for row in rows:
            row[0] = row[0].replace(">" , "&gt;")
            row[0] = row[0].replace("<" , "&lt;")
        file   = open( 'parseTable.html' , 'w+')
        file.write(tabulate(rows, headers = sorted(self.grammar.terminals), tablefmt="html"))      # read the entire file into a string
        
        
        file.close()

    def parse(self):
        #open outderivation file
        file   = open( 'outDerivation.txt' , 'w+')    
        
        #push the EOF token to the stack
        stack = ['$']
        #push start rule
        stack.append('<START>')
        
        #get next token
        a = self.nextToken()
        error= False;
        
        while stack[-1] != '$' and a.type != "$":
            #x = top()
            x = stack[-1] 
            
            #show stack and next token
            file.write('---------------------------------------------------------------\n')
            file.write('currentStack' + str(stack) + ". Token to read: " + str(a) + '\n')

            if x in self.grammar.terminals or x == 'EPSILON':
                #print('found terminal: ' + x)
                if x == a.type or x == 'EPSILON':
                    
                    file.write('popping terminal ' + stack.pop() + '\n')
                    
                    if x != 'EPSILON':
                        a = self.nextToken()
                    
                else: 
                    print('found Terminal error')
                    a = self.skipError(a,stack)
                    error = True 
            else:
                #print('found non terminal:' + x)
                if self.table[x][a.type] != 'empty':
                    
                    file.write('found rule to use: ' + self.table[x][a.type]['LHS'] + " -> " + self.table[x][a.type]['RHS'] + '\n')
                    file.write("popping " + stack.pop())       
                    
                    elements = self.table[x][a.type]['RHS'].split()[::-1]
                    
                    file.write("adding " + str(elements) + " to stack\n")
                    
                    stack.extend(elements)
                else: 
                    print('found non terminal error')
                    a = self.skipError(a,stack)
                    error = True
        
        if error == True or stack[-1] != '$':
            return False 
        else : 
            file.write("\n\nParsing successful!")
            file.close()
            return True 

    
    def skipError(self , lookAhead , stack):
        file = open('errors.txt' , 'a+')
        file.write("Syntax error for token " + str(lookAhead) + "\n")

        top = stack[-1]
        first = self.grammar.firstSets
        follow = self.grammar.followSets
        rtrnTok = lookAhead

        if top not in self.grammar.terminals:

            print("when error top of stack is NT")

            if rtrnTok.type == '$' or rtrnTok.type in self.grammar.followSets[top]:
                print('popping stack to resume parse. Token = ' +  str(rtrnTok))
                stack.pop()           
            else: 
                while (rtrnTok.type not in first[top] or 'EPSILON' in first[top] and rtrnTok.type not in follow[top]) and rtrnTok.type != "$":
                    rtrnTok = self.nextToken()
                    
                    print('finding sync token. Possibilities' +  str(first[top]) +  str(follow[top]) if 'EPSILON' in first[top] else '' )
                                    
                    print('current token = ' + str(rtrnTok))
                print('found ' +  ('Follow' if rtrnTok.type in follow[top] else 'First')  + ' token that matches Non Terminal: '+ top + '. Token is: ' + str(rtrnTok) )
        else : 
            
            while rtrnTok.type != top and rtrnTok.type != '$':
                print('finding sync token... Possibilities: ' + top)
                print('current token = ' + str(rtrnTok))
                rtrnTok =  self.nextToken()
                #print('skipping token' + str(lookAhead))
                #print('here + lh' + str(lookAhead.type != '$' or lookAhead.type != top ))
            print('found token that matches terminal:' + str(rtrnTok))

        return rtrnTok   
        file.close()


        

        