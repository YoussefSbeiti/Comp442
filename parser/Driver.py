from Grammar import *
from Parser import *

grammar = Grammar('../grammar.atocc' , '../first.txt' , '../follow.txt')
parser = Parser(grammar , '../polynomial.src')

parser._lex()
#grammar.printRules()
#parser.generateParseTable()
#parser.printParseTableHTML()
#parser.parse()
#print(parser.table)
