from semanticAnalyzer.SymTable import *
import re
from semanticAnalyzer.SymTableCreator import SymTableCreator
from semanticAnalyzer.SemanticCheckerVisitor import SemanticCheckerVisitor
from semanticAnalyzer.CodeGenerator import CodeGenrator

class SemAnalyzer:
    

    def __init__(self):
       
       self.globalSymTable  = None
       

    def traverseTree(self,node, visitor):
        visitor.nodeHandler(node)
        #print(node.value)
        if node.children != []:
            for child in node.children:
                self.traverseTree(child , visitor)
        
        visitor.nodeHandler(node)
        #print(node.value)
                
    
    
    def analyzeTree(self, progNode):

        symTableCreator = SymTableCreator()
        symTableCreator.createSymTable(progNode)
        self.globalSymTable = symTableCreator.globalSymTable

        semanticCheckerVisitor = SemanticCheckerVisitor(self.globalSymTable) 
        self.traverseTree(progNode , semanticCheckerVisitor)

        progNode.resetVisitCount()

        codeGenrator = CodeGenrator(self.globalSymTable)
        self.traverseTree(progNode , codeGenrator)
        codeGenrator.moonGateway.writeToSrc()

        return self.globalSymTable

    
   

        
