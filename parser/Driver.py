from Grammar import *
from Parser import *

grammar = Grammar('../grammar.grm' , '../first.txt' , '../follow.txt')
parser = Parser(grammar , '../polynomial.src')

#parser._lex('../lexpositivegrading.outlextokens')
#grammar.printRules()
parser.generateParseTable()
parser.printParseTableHTML()
parser.parse()
#print(parser.table)
