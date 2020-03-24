from Grammar import *
from Parser import *

grammar = Grammar('../outfile.grm' , '../outfile.grm.first' , '../outfile.grm.follow')
parser = Parser(grammar , '../testCases/mainOnly.src')


#dotFile = open('tree.gv' ,'w+')
#dotFile.write(parser.astDot.source)

#grammar.printFollowSets()
#parser._lex('../lexpositivegrading.outlextokens')
#grammar.printRules()
#parser.generateParseTable()
#parser.printParseTableHTML()

print(parser.parse())
#print(parser.table)
