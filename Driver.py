import sys
#sys.path.insert(0,'/home/youssefsb/VS_workspace/Comp442/Comp442/parser/Grammar')

import graphviz

from subprocess import call

from parser.Parser import Parser
from parser.Grammar.Grammar import Grammar 
from semanticAnalyzer.SemAnalyzer import SemAnalyzer

grammar = Grammar('parser/Grammar/outfile.grm' , 'parser/Grammar/outfile.grm.first' , 'parser/Grammar/outfile.grm.follow')
parser = Parser(grammar , 'testCases/mainOnly.src')
semAnalyzer = SemAnalyzer()

parser.parse()
globalSymTable = semAnalyzer.analyzeTree(parser.astRoot)
print(str(globalSymTable.getTypeSizesHashMap()))
globalSymTable.symTableAsHtml()

call(["moon/moon", "moon/outFile.m", "moon/lib.m" ])