from rule import *
import ast
from Lexer.Lexer import Lexer
import json

def pretty(d):
   for key, value in d.items():
      print("{" + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))

class Grammar:

    def __init__(self , grammarPath , firstPath = '', followPath = ''):
        
        self.rules=[]
        self.followSets = {}
        self.firstSets = {}
        self.terminals = Lexer.tokens

        if(firstPath != ''):
            self.addFirstSetsFromSrc(firstPath)
        if(grammarPath != ''):    
            self.addRulesFromSrc(grammarPath)
        if(followPath != ''):
            self.addFollowSetsFromSrc(followPath)

    
        
    def addRulesFromSrc(self,grammarPath):
        file   = open( grammarPath , 'rt')
        ruleStrings = file.readlines()      # read the entire file into a string
        file.close()

        for ruleString in ruleStrings:
            #print(ruleString)
            if '::=' in ruleString:
                rule = getRule(ruleString) #extract as a rule dictionary {LHS : RHS}
                self.rules.append(rule) #append to rules list
            #print('added rule' + json.dumps(rule))

    def addFollowSetsFromSrc(self, followPath):
        file   = open( followPath , 'rt')
        lines = file.readlines()      # read the entire file into a string
        file.close()

        for line in lines:
            line = line.replace("FOLLOW(" , "")
            line = line.replace(")" , "")
            lineSplit = line.split("=")
            try :
                self.followSets[lineSplit[0]] = ast.literal_eval(lineSplit[1].strip())
            except:
                try:
                    self.followSets[lineSplit[0]] = ast.literal_eval(lineSplit[1].strip().replace('$' , '\'$\''))
                except: 
                    print("Error in getting data from FollowFile")
    
    def addFirstSetsFromSrc(self, firstPath):
        file   = open( firstPath , 'rt')
        lines = file.readlines()      # read the entire file into a string
        file.close()

        for line in lines:
            line = line.replace("FIRST(" , "")
            line = line.replace(")" , "")
            line = line.replace("EPSILON" , "\'EPSILON\'")
            lineSplit = line.split("=")
            try :
                self.firstSets[lineSplit[0]] = ast.literal_eval(lineSplit[1].strip())
            except:
                try:
                    self.firstSets[lineSplit[0]] = ast.literal_eval(lineSplit[1].strip().replace('$' , '\'$\''))
                except:
                    print("Error in getting data from FirstFile :" + lineSplit[0].strip().replace('$' , '\'$\''))
    
    def addRule(self, rule):
        self.rules.append(rule)

    def printRules(self):
        for rule in self.rules:
          print(json.dumps(rule, indent=1))

    def printFollowSets(self):
        print(self.followSets)

    def printFirstSets(self):
        print(self.firstSets)

    def validateFirstAndRules(self):
        for key,val in self.firstSets.items():
            print("{} = {}".format(key, val))
        for rule in self.rules:
            print(rule)
    
    #
    #   TO FIX
    #
    def getFirstFromRHS(self,rhs):
        elements = rhs.split()
        rslt = []

        if  elements == ['EPSILON']:
                return ['EPSILON']

        for element in elements:
            if element in self.terminals :
                rslt.append(element)
                while 'EPSILON' in rslt:
                    rslt.remove('EPSILON')
                break
            
            else:
                if element != 'EPSILON':
                    rslt.extend(self.firstSets[element])
                    if 'EPSILON' not in self.firstSets[element]:
                        while 'EPSILON' in rslt:
                            rslt.remove('EPSILON')
                        break
        
        

        if rslt == []:
            return ['EPSILON']
        else:
            return list(set(rslt))
            


