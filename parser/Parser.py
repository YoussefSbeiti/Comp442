from Lexer.Lexer import Lexer
import json
from tabulate import tabulate
import re

class Parser:
    def __init__(self , grammar, srcPath):
        lexer = Lexer()
        lexer.build()
        self.lexer = lexer.lexer
        file = open(srcPath , 'r')
        self.lexer.input(file.read())
        file.close()

        self.grammar = grammar
        self.table = {}

    def _lex(self , src):
        # Tokenize
        
        while True:
            tok = self.lexer.token()
            if not tok: 
                break      # No more input
            print(tok.type)

    
    def nextToken(self):
        tok = self.lexer.token() 
        if tok:
            return tok.type

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
        #print(json.dumps(self.table, indent = 1))
        #for nt,row in sorted(self.table.items()):
         #   print ("{" + str(nt) + str(row) + " }")
        
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
        stack = ['$']
        stack.append('<START>')
        #nextToken = self.nextToken() ##fix empty token
        a = self.nextToken()
        error= False;
        while stack[-1] != '$' :
            print('a =' + a +'|')
            x = stack[-1] 
            if x in self.grammar.terminals or x == 'EPSILON':
                print('found terminal: ' + x)
                if x == a or x == 'EPSILON':
                    print('popping rule')
                    stack.pop()
                    if x != 'EPSILON':
                        a = self.nextToken()
                else: error = True 
            else:
                print('found non terminal:' + x)
                if self.table[x][a] != 'empty':
                    print('found rule to use: ' + str(self.table[x][a]))
                    stack.pop();       
                    elements = self.table[x][a]['RHS'].split()[::-1]
                    stack.extend(elements)
                else: error = True
            print('currentStack' + str(stack))
        if a != '$' or error == True:
            return False 
        else : return True 



        

        