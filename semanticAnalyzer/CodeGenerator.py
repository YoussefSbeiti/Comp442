import random
from semanticAnalyzer.MoonGateway import MoonGateway
from parser.AST.Node import Node
from semanticAnalyzer.MemoryReference import MemoryReference

class CodeGenrator:
    
    def __init__(self , globalSymTable):
        self.stack = []
        self.globalSymTable = globalSymTable
        self.typeSizes = globalSymTable.getTypeSizesHashMap()
        self.moonGateway = MoonGateway()
        self.scopeStack = [[globalSymTable]]

    def nodeHandler(self, node):
        
        #if node.value == "FuncBody" and node.parent.value == "Prog":

        node.visitCount += 1

        if node.value == "FuncBody" and node.parent.value == "Prog":
            if node.visitCount == 1:
                mainSyamTbale = self.globalSymTable.getEntryByName("Main")['link']
                self.scopeStack.append([mainSyamTbale , self.globalSymTable])   
            else:
                self.scopeStack.pop()

        if node.value == "If":
            if node.visitCount == 1:
                self.stack.append("THENBLOCK")

        if node.value == "ThenBlock":
            if node.visitCount == 1:
                elseLabel = self.moonGateway._generateLabel()
                relExprResult = self.popStackUntil("THENBLOCK")[0]
                self.moonGateway.bz(relExprResult, elseLabel)
                
                self.stack.append("ELSEBLOCK")
                self.stack.append(elseLabel)

            else:
                endLabel = self.moonGateway._generateLabel()
                self.moonGateway.j(endLabel)
                self.stack.append(endLabel)
        
        if node.value == "ElseBlock":
            if node.visitCount == 1:
                endLabel = self.stack.pop()
                elseLabel = self.stack.pop()
                self.moonGateway.writeLine(elseLabel) 
                self.stack.append(endLabel)
            else:
                endLabel = self.popStackUntil("ELSEBLOCK")[0]
                self.moonGateway.writeLine(endLabel)
        
        if node.value == "While":
            if node.visitCount == 1:
               self.stack.append("WHILEBLOCK")
               whileLabel = self.moonGateway._generateLabel()
               self.moonGateway.writeLine(whileLabel)
               self.stack.append(whileLabel)

        if node.value == "WhileBlock":
            if node.visitCount == 1:
                
                endLabel = self.moonGateway._generateLabel()
                
                artifacts  = self.popStackUntil("WHILEBLOCK")
                relExprResult = artifacts[0]
                whileLabel = artifacts[1]
                self.moonGateway.bz(relExprResult, endLabel)

                self.stack.append(whileLabel)
                self.stack.append(endLabel)

            else: 
                endLabel = self.stack.pop()
                whileLabel = self.stack.pop()
                self.moonGateway.j(whileLabel)
                self.moonGateway.writeLine(endLabel)
        
        if node.value == "RelExpr":
            if node.visitCount == 1:
                    self.stack.append(node.children[1].value)
            elif node.visitCount == 2:
                operator = node.children[1].value 
                print("Excecuting + " + str(self.stack))             
                operands = self.popStackUntil(operator)
                rhsMoonLabel = operands[0]
                lhsMoonLabel = operands[1]
                resultLabel = self.moonGateway.relOp(operator, lhsMoonLabel,rhsMoonLabel)
                
                self.stack.append(resultLabel)

        if node.value == "VarDecl":
            if node.visitCount == 1:
                variableName = node.children[1].value
                variableType = node.children[0].value
                variableTypeSize = self.typeSizes[variableType]
                if len(node.children) == 3: #case of an array
                    arrSize = 1
                    arrSizeListNode = node.children[2]
                    for arrSizeNode in  arrSizeListNode.children:
                        arrSize *= int(arrSizeNode.children[0].value)
                    self.moonGateway.reserveMemory(variableName , variableTypeSize * arrSize)
                else:
                    self.moonGateway.reserveMemory(variableName , variableTypeSize)

        if node.type == "intNum": 
            if node.visitCount == 1:
                literalMemRef = self.moonGateway.storeLiteral(node.value) 
                self.stack.append(literalMemRef)

        if node.value == "Assign":
         
            if node.visitCount == 1:
                self.stack.append("ASSIGN")
            elif node.visitCount == 2:
                print("Excecuting Assign " + str(self.stack))
                operands = self.popStackUntil("ASSIGN")
                rhsMoonMemLocation = operands[0]
                lhsMoonMemLocation = operands[1]

                self.moonGateway.loadWordToMemRef(lhsMoonMemLocation , rhsMoonMemLocation)
               
        if node.value == "ArithExpr":
            if len(node.children) == 3: 
                if node.visitCount == 1:
                    self.stack.append(node.children[1].value)
                elif node.visitCount == 2:
                    operator = node.children[1].value 
                    print("Excecuting + " + str(self.stack))             
                    operands = self.popStackUntil(operator)
                    rhsMoonLabel = operands[0]
                    lhsMoonLabel = operands[1]

                    if operator == "+":
                        
                        resultLabel = self.moonGateway.binaryOp(operator, lhsMoonLabel,rhsMoonLabel)
                    elif operator == "-":
                        resultLabel = self.moonGateway.binaryOp(operator,  lhsMoonLabel, rhsMoonLabel)

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
                        resultLabel = self.moonGateway.binaryOp(operator, lhsMoonLabel,rhsMoonLabel)
                    elif operator == "/":
                        resultLabel = self.moonGateway.binaryOp(operator, lhsMoonLabel, rhsMoonLabel)

                    self.stack.append(resultLabel)

        if node.value == "Write":
            if node.visitCount == 1:
                self.stack.append("WRITE")
            elif node.visitCount == 2:
                print("Excecuting Write: " + str(self.stack))
                op = self.popStackUntil("WRITE")[0]
                self.moonGateway.print(op)

        if node.value == "Read":
            if node.visitCount == 1:
                self.stack.append("READ")
            elif node.visitCount == 2:
                print("Excecuting READ: " + str(self.stack))
                op = self.popStackUntil("READ")[0]
                self.moonGateway.read(op)
        #if node.value == "IndexList":
         #   if node.visitCount == 1:
          #      self.stack.append("INDEXLIST")
          #  elif node.visitCount == 2:
           #     indecies = self.popStackUntil("INDEXLIST")
            #    self.stack.append(indecies)
        
        if node.value == "VarMember":
            self.varMemberNodeHandler(node)

        if node.value == "Variable":
            self._variableNodeHandler(node)
    
    def _variableNodeHandler(self,node):

        if node.visitCount == 1:
            self.stack.append("VARIABLE")
        else:
        
            print("Excecuting VARIABLE " + str(self.stack))
            varMembers = self.popStackUntil("VARIABLE")
            
            for i in range(len(node.children) - 1):
                self.scopeStack.pop()
            
            firstMember = varMembers.pop()
            variableMemoryRef = MemoryReference(firstMember.label)
            variableMemoryRef.addOffsets(firstMember.offsets)

            for member in varMembers:
                variableMemoryRef.addOffsets(member)

            self.stack.append(variableMemoryRef)

    def varMemberNodeHandler(self, node):
        if  len(node.children) == 2:
            if node.visitCount == 1:
                self.stack.append("INDEXEDVARIABLE")
            else:
                
                #print("In Node " + node.children[0].value)
                #print("Current Scope " + str(self.scopeStack[-1]))
                indiceLabels = self.popStackUntil("INDEXEDVARIABLE")
                arrName = node.children[0].value
                arrEntry = self.getEntryFromCurrentScope(arrName)
                arrType = arrEntry["Type"]

                arrBaseType = arrType.split("[" , 1)[0]
                baseTypeSize = self.typeSizes[arrBaseType]
                self.moonGateway.multiplyImmediateMemRef(indiceLabels[0] ,baseTypeSize)
                
                if node.numberOfSiblingsToTheLeft() == 0:
                    memoryRef = MemoryReference(arrName)
                    memoryRef.addOffsets(indiceLabels)
                    self.stack.append(memoryRef)
                else:
                    try: 
                        offset = arrEntry['offset']
                        memberOffsetIntoClassMemoryRef = self.moonGateway.storeLiteral(offset)
                        #memoryRef = MemoryReference(arrName)
                        #memoryRef.addOffsets([memberOffsetIntoClassMemoryRef, indiceLabels[0]])
                        self.stack.extend([memberOffsetIntoClassMemoryRef, indiceLabels[0]])
                    except:
                        pass
                   
                
                if node.numberOfSiblingsToTheRight() != 0:
                
                    try:
                        newScope = self.globalSymTable.getClassEntryByName(arrBaseType)["link"]
                        self.scopeStack.append([newScope])
                    except:
                        pass
        
        else:
            if node.visitCount == 2:
                
                #print("In Node " + node.children[0].value)
                #print("Current Scope  " + str(self.scopeStack[-1]))

                varName = node.children[0].value
                varEntry = self.getEntryFromCurrentScope(varName)
                varType = varEntry["Type"]
                

                if node.numberOfSiblingsToTheLeft() == 0:
                    self.stack.append(MemoryReference(varName))
                else:
                    varOffset = varEntry["offset"]
                    offsetValueMemoryRef = self.moonGateway.storeLiteral(varOffset)

                    self.stack.append(offsetValueMemoryRef)

                #update scope after leaving node
                if node.numberOfSiblingsToTheRight() != 0:
                    try:
                        newScope = self.globalSymTable.getClassEntryByName(varType)["link"]
                        self.scopeStack.append([newScope])
                    except:
                        pass

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