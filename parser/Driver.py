from Grammar import *
from Parser import *

grammar = Grammar('../grammar.atocc' , '../first.txt' , '../follow.txt')
parser = Parser(grammar , '../polynomial.src')

#grammar.printRules()
parser.generateParseTable()
parser.printParseTableHTML()
parser.parse()
#print(parser.table)
