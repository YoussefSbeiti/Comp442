from Grammar import *
from rule import rule

def grammarGenerator(srcPath):

    myfile   = open( srcPath , 'rt')
    ruleStrings = myfile.readlines()      # read the entire file into a string
    myfile.close()

    for ruleString in ruleStrings:
        rule = rule(ruleString)
        grammar.addRule(rule)



