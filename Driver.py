import sys
#sys.path.insert(0,'/home/youssefsb/VS_workspace/Comp442/Comp442/parser/Grammar')

for path in sys.path:
    print(path)

import graphviz

from parser.Parser import Parser
from parser.Grammar.Grammar import Grammar 
from semanticAnalyzer.SemAnalyzer import SemAnalyzer

grammar = Grammar('parser/Grammar/outfile.grm' , 'parser/Grammar/outfile.grm.first' , 'parser/Grammar/outfile.grm.follow')
parser = Parser(grammar , 'testCases/bubblesort.src')


#dotFile = open('tree.gv' ,'w+')
#dotFile.write(parser.astDot.source)

#grammar.printFollowSets()
#parser._lex('../lexpositivegrading.outlextokens')
#grammar.printRules()
#parser.generateParseTable()
#parser.printParseTableHTML()

print(parser.parse())

#parser.astDot.

semAnalyzer = SemAnalyzer()

globalSymTable = semAnalyzer.analyzeTree(parser.astRoot)

globalSymTable.symTableAsHtml()
#print(str(globalSymTable.getNamesOfKind("Function")))
#print(parser.table)
