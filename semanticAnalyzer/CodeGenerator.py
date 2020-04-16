import random
from semanticAnalyzer.MoonGateway import MoonGateway

class CodeGenrator:
    
    def __init__(self , globalSymtable):
        self.stack = []
        self.globalSymtable = globalSymtable
        self.typeSizes = globalSymtable.getTypeSizesHashMap()
        self.moonGateway = MoonGateway()
        self.scopeStack = [[globalSymtable]]

    def nodeHandler(self, node):
        
        #if node.value == "FuncBody" and node.parent.value == "Prog":

        node.visitCount += 1

        if node.value == "FuncBody" and node.parent.value == "Prog":
            if node.visitCount == 1:
                mainSyamTbale = self.globalSymtable.getEntryByName("Main")['link']
                self.scopeStack.append([mainSyamTbale , self.globalSymtable])   
            else:
                self.scopeStack.pop()


        if node.value == "VarDecl":
            if node.visitCount == 1:
                variableName = node.children[1].value
                variableType = node.children[0].value
                variableTypeSize = self.typeSizes[variableType]
                self.moonGateway.reserveMemory(variableName , variableTypeSize)
                
        # if node.value == "Variable":
        #     if node.visitCount == 1:
        #         self.stack.append("VARIABLE")
        #     elif node.visitCount == 2:
        #         popCount = 0
        #         memLoc = {}
        #         varMembers = self.popStackUntil("VARIABLE")
        #         firstMember = varMembers.pop()
        #         memLoc["label"] = firstMember
        #         firstMemberType = self.getEntryFromCurrentScope(firstMember)['type']
        #         #might raise error
        #         firstMemberTypeSymTable = self.globalSymtable.getClassEntryByName(firstMemberType)
        #         self.scopeStack.append(firstMemberTypeSymTable)
        #         popCount += 1
        #         for member in varMembers[::-1]:
        #             self.getEntryFromCurrentScope(firstMember)['type']

        if node.value == "VarMember":
            if node.visitCount == 1:
                self.stack.append(node.children[0].value)
           
        if node.type == "intNum": 
            if node.visitCount == 1:
                literalLbl = self.moonGateway.storeLiteral(node.value) 
                self.stack.append(literalLbl)

        if node.value == "Assign":
         
            if node.visitCount == 1:
                self.stack.append("ASSIGN")
            elif node.visitCount == 2:
                print("Excecuting Assign " + str(self.stack))
                operands = self.popStackUntil("ASSIGN")
                rhsMoonLabel = operands[0]
                lhsMoonLabel = operands[1]

                #load rhs (ie right hand side value) label into register 1
                self.moonGateway.loadWord(1, rhsMoonLabel)
                #store register 1 contents into reserved word labeled lhs(ir variable name)
                self.moonGateway.storeWord(lhsMoonLabel,1)

        if node.value == "ArithExpr":
            if len(node.children) == 3: 
                if node.visitCount == 1:
                    self.stack.append(node.children[1].value)
                elif node.visitCount == 2:
                    operator = node.children[1].value              
                    operands = self.popStackUntil(operator)
                    rhsMoonLabel = operands[0]
                    lhsMoonLabel = operands[1]

                    if operator == "+":
                        resultLabel = self.moonGateway.add(lhsMoonLabel,rhsMoonLabel)
                    elif operator == "-":
                        resultLabel = self.moonGateway.subtract(rhsMoonLabel, lhsMoonLabel)

                    self.stack.append(resultLabel)
        
        if node.value == "Term":
            if len(node.children) == 3: 
                if node.visitCount == 1:
                    self.stack.append(node.children[1].value)
                elif node.visitCount == 2:
                    operator = node.children[1].value
                    operands = self.popStackUntil(operator)
                    rhsMoonLabel = operands[0]
                    lhsMoonLabel = operands[1]

                    if operator == "*":
                        resultLabel = self.moonGateway.multiply(lhsMoonLabel,rhsMoonLabel)
                    elif operator == "/":
                        resultLabel = self.moonGateway.divide(rhsMoonLabel, lhsMoonLabel)

                    self.stack.append(resultLabel)

        if node.value == "Write":
            if node.visitCount == 1:
                self.stack.append("WRITE")
            elif node.visitCount == 2:
                print("Excecuting Write: " + str(self.stack))
                op = self.popStackUntil("WRITE")[0]
                self.moonGateway.print(op)


    def variableNodeHandler(self,node):
        popCount = 0
        
    def varMemberNodeHandler(self, node):
         if node.visitCount == 2:
            memberName = node.children[0].value    
            memberEntry = self.getEntryFromCurrentScope(memberName) 
            
            if memberEntry['kind'] == "Variable":
                if len(node.children) == 1:
                    if node.numberOfSiblingsToTheLeft() == 0:
                        self.stack.append({"changeLabel" : True , "Label" : memberName, "Offset" : 0})
                    else:
                        self.stack.append({"changeLabel" : True , "Label" : memberName, "Offset" : 0})
            
            memberType = memberEntry['type']
            
            self.scopeStack.append([self.globalSymtable.getClassEntryByName(memberType)['link']])

            
                
                    

                
            


    def getEntryFromCurrentScope(self, name):
        currentScope = self.scopeStack[-1]
        for symTable in currentScope:
            foundEntry = symTable.getEntryByName(name)
            if foundEntry != None:
                return foundEntry

    def popStackUntil(self,token):
            rslt = []
            i = 0
            x  = len(self.stack)
            while i < x:
                element = self.stack.pop()
                
                if element == token: #means marker has been found. Nodes beyond this marker do not belong to this node
                    break
                rslt.append(element)        
                i += 1
            return rslt