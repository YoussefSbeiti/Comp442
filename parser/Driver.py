from Grammar import *
from Parser import *

grammar = Grammar('../outfile.grm' , '../outfile.grm.first' , '../outfile.grm.follow')
parser = Parser(grammar , '../testCases/multRelexpr.src')

#grammar.printFollowSets()
#parser._lex('../lexpositivegrading.outlextokens')
#grammar.printRules()
parser.generateParseTable()
parser.printParseTableHTML()
print(parser.parse())
#print(parser.table)
