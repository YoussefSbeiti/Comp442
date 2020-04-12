from parser.Lexer.Lexer import Lexer
import json
from tabulate import tabulate
import re
from types import SimpleNamespace
from parser.AST.AST import AST
from graphviz import Digraph
from parser.Grammar.Grammar import Grammar

class Parser:
    def __init__(self , grammar, srcPath):
        
        lexer = Lexer()
        lexer.build()
        self.lexer = lexer.lexer
        #self.lexer.lineno += 1
        
        self.table = {}

        #semantic actions to be excecuted at a marker
        self.semanticActions = {}
        
        self.astDot = Digraph()
        self.astRoot = None

        file = open(srcPath , 'r')
        self.lexer.input(file.read())
        file.close()

        self.grammar = grammar
        self.generateParseTable()
        self.printParseTableHTML()
        #delete contents of wrror file
        open("parser/Artifacts/errors.txt", "w").close()

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
        token.type = 'EOF'
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
                    #if rule['LHS'] == '<semMarkerProg>':
                    #print('created entry<' + rule['LHS'] +', ' + terminal +'> = ' + str(rule) )
            
            
            for terminal in self.grammar.terminals:
                if terminal not in self.table[rule['LHS']].keys():
                    self.table[rule['LHS']][terminal] = 'empty'

    def printParseTableHTML(self):
        
        #print(sorted(self.grammar.terminals))
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

        #helper function to display stack
        def getStackAsString(stck):
            strin = '['
            for element in stck:
                strin += str(element) + ', '
            strin += ']'
            return strin

        #open outderivation file
        file   = open( 'parser/Artifacts/outDerivation.txt' , 'w+')    
        
        #push the EOF token to the stack
        stack = ['$']
        
        #push start rule
        stack.append('<START>')

        #create Semantic Stack
        semStack = []
        
        #get next token
        a = self.nextToken()
        error= False;
        
        #while final element of the parse stack is not $ aka stat symbol or if the next token is not the 'EOF' marker
        while stack[-1] != '$' and a.type != "EOF":

            

            #x = top()
            x = stack[-1] 

            #create a AST object             
            ast = AST([ ';' ,  '}' , '{' , 'main' , 'local' ,'class' , '(' , ')' , 'inherits' , ':' , ',' , 'do', 'end' , '.' , '[' , ']' , 'return'])

            #show stack and next token
            file.write('---------------------------------------------------------------\n')
            file.write('currentStack' + str(stack) + ". Token to read: " + str(a) + '\n')


            #if top element on stack is terminal or epsilon
            if x in self.grammar.terminals or x == 'EPSILON':
                
                
                #if top of parse stack matches token to read pop that terminal from stack
                if x == a.type or x == 'EPSILON':
                    
                    stack.pop()
                    file.write('popping terminal ' + x + '\n')

                   #if that terminal is not EPSILON 
                    if x != 'EPSILON':

                        #make node and add it to semStack
                        node = ast.makeNodeTerminal(a.value)
                        node.type = a.type
                        semStack.append(node)
                        #print('adding ' + str(node) + 'to semstack' )     
                        
                        #get next token to read
                        a = self.nextToken()
                #else: error
                else: 
                    print('found Terminal error')
                    a = self.skipError(a,stack)
                    error = True

            #else if top of stack is not a terminal
            else:
                #print('found non terminal:' + x)

                #if entry in parse table exists for the (rule , next token ) tuple | no error
                if self.table[x][a.type] != 'empty':

                    #check if it's a semAction and excecute
                    semAction = re.search('<semAction(.+?)>' , x)

                    if semAction:
                       
                        semAction = semAction.group(1)
                        #print('executing semAction' + semAction)
                        #print('current semStack = ' + getStackAsString(semStack))
                        semStack.append(ast.makeNode(semAction , semStack))

                    #check if it's a semAction and excecute
                    semMarker = re.search('<semMarker(.+?)>' , x)

                    if semMarker:
                       
                        semMarker = semMarker.group(1)
                        #print('found semMarker' + semMarker)
                        #print('current semStack = ' + getStackAsString(semStack))
                        semMarkerNode = ast.makeNodeTerminal("Marker" + semMarker)
                        semMarkerNode.line = self.lexer.lineno
                        semStack.append( semMarkerNode)


                    file.write('found rule to use: ' + self.table[x][a.type]['LHS'] + " -> " + self.table[x][a.type]['RHS'] + '\n')
                    file.write("popping " + stack.pop())       
                    
                    elements = self.table[x][a.type]['RHS'].split()[::-1]
                    
                    file.write("adding " + str(elements) + " to stack\n")
                    
                    stack.extend(elements)

                #else: error
                else: 
                    print('found non terminal error')
                    a = self.skipError(a,stack)
                    error = True

        
        if error == True or stack[-1] != '$':
            return False 
        else : 
            
            file.write("\n\nParsing successful!")
            file.close()


            #create root node for ast (Prog node)
            self.astRoot =  ast.makeNode('Prog' , semStack)    

            self.astRoot.treeDOT(self.astDot)

            #dotFile = open('tree.gv' ,'w+')
            #dotFile.write(self.astDot.source)
            
            self.astDot.render('tree.gv' )

            return True 


    def skipError(self , lookAhead , stack):
        file = open('parser/Artifacts/errors.txt' , 'a+')
        file.write("Syntax error for token " + str(lookAhead) + "\n")

        top = stack[-1]
        first = self.grammar.firstSets
        follow = self.grammar.followSets
        rtrnTok = lookAhead

        if top not in self.grammar.terminals:

            print("error in fulfilling rule " + top + 'with lookahead = ' + str(lookAhead) )

            if rtrnTok.type == 'EOF' or rtrnTok.type in self.grammar.followSets[top]:
                print('popping Token = ' +  top + ' to resume parse.')
                stack.pop()           
            else: 
                while (rtrnTok.type not in first[top] or 'EPSILON' in first[top] and rtrnTok.type not in follow[top]) and rtrnTok.type != "EOF":
                    rtrnTok = self.nextToken()
                    
                    print('finding sync token. Possibilities' +  str(first[top]) +  str(follow[top]) if 'EPSILON' in first[top] else '' )
                                    
                    print('current token = ' + str(rtrnTok))
                print('found ' +  ('Follow' if rtrnTok.type in follow[top] else 'First')  + ' token that matches Non Terminal: '+ top + '. Token is: ' + str(rtrnTok) )
        else : 
            
            while rtrnTok.type != top and rtrnTok.type != 'EOF':
                print('finding sync token... Possibilities: ' + top)
                print('current token = ' + str(rtrnTok))
                rtrnTok =  self.nextToken()
                #print('skipping token' + str(lookAhead))
                #print('here + lh' + str(lookAhead.type != '$' or lookAhead.type != top ))
            print('found token that matches terminal:' + str(rtrnTok))

        return rtrnTok   
        file.close()


        

        