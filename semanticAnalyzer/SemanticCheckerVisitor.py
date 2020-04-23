from semanticAnalyzer.SymTable import *
from semanticAnalyzer.SemanticTranslationUtils import *
from semanticAnalyzer.SemanticTranslationUtils import  _extractInfoFromMemDeclNode
from semanticAnalyzer.SemanticTranslationUtils import _extractParamsfromFparamsNode
import re

class undeclaredTypeError(Exception):
    pass

class SemanticCheckerVisitor:
    def __init__(self , globalSymTable):
        
        self.ErrorFile = open('SemanticErrors.txt' , 'w+')
        self.globalSymTable = globalSymTable
        self.scopeStack = [[globalSymTable]]
        self.semanticStack = []

    def nodeHandler(self, node):
        node.visitCount += 1
        
        if node.error:
            if node.visitCount == 1:
                self._reportError(node.error)
                return

        if node.warning:
            if node.visitCount == 1:
                self._reportError(node.warning)

        if node.value == 'ClassDecl':
            className = node.children[0].value
            classSymTable = self.globalSymTable.getClassEntryByName(className)['link']
            inheritanceList = node.children[1].children

            for inheritedClass in inheritanceList:
                try:
                    parentSymTable = self.globalSymTable.getClassEntryByName(inheritedClass.value)['link']
                    #parentSymTable.getInheritenceList()
                    classSymTable.addInheritedClass(inheritedClass.value , parentSymTable)
                except (classNotInTableError, cyclicalDependencyError) as e:
                    
                    if e.__class__.__name__ == 'classNotInTableError': 
                        self._reportError({'message' : "Class " + inheritedClass.value + " does not exist" , "line":str(inheritedClass.line)})
                    elif e.__class__.__name__ == 'cyclicalDependencyError':
                        self._reportError({'message': "Cyclical dependencyError " , 'line': str(node.line)})


            if node.visitCount == 1:
                self.scopeStack.append([classSymTable])
            else:
                self.scopeStack.pop()


        if node.value == "MemberDecl":
            if node.visitCount == 1:
                memberNode = node                
                member = _extractInfoFromMemDeclNode(memberNode)

                classSymTable = self.scopeStack[-1][0]

                if member['kind'] == 'Function':
                    try:
                        typesToCheck = re.compile('\W+').split( member['type'])
                        typesToCheck.pop()
                        for typeToCheck in typesToCheck:
                            self._checkIfTypeExists(typeToCheck)
                        
                        classSymTable.checkFunctionForWarnings(member['name'] , member['type'])
                    except undeclaredTypeError:
                        self._reportError({"message" : "Undeclared type " + typeToCheck , 'line' : memberNode.line})
                        classSymTable.removeEntry(member["name"] , member["kind"] , member["type"])
                    except (overshadowedFunctionMemberWarning , overloadedFunctionWarning) as e:
                        if e.__class__.__name__ == 'overshadowedFunctionMemberWarning':
                            self._reportError({'message' : "shadowed member function " + member['name'] + " of type: " + member['type'] , 'line': memberNode.line} )
                        elif e.__class__.__name__ == 'overloadedFunctionWarning':
                            self._reportError({'message' : "overloaded member function " + member['name'] + " of type: " + member['type'] , 'line': memberNode.line})
                       
                else:
                    try:
                        self._checkIfTypeExists(member['type'])
                        classSymTable.checkVariableForWarnings(member['name'])
                    except overshadowedDataMemberWarning :
                        self._reportError({'message' : "shadowed data member " + member['name'] , 'line': memberNode.line})
                    except undeclaredTypeError:
                        self._reportError({'message' : "Undeclared type " + member['type'] , 'line': memberNode.line})
                        classSymTable.removeEntry(member["name"], member["kind"] , member["type"])

        if node.value == "LocalVarList":
            if node.visitCount == 1 :
                for varDeclNode in node.children:
                    try:
                        varType = varDeclNode.children[0].value
                        self._checkIfTypeExists(varType)
                    except undeclaredTypeError:
                        self._reportError({"message" : "Undeclared type " + varType ,"line" : varDeclNode.line})
                        for element in self.scopeStack[-1]:
                            element.removeEntry(varDeclNode.children[1].value, "Variable", varType )
        
        
    
        if node.value == "FuncDef":

            funcDefNode = node 
            if len(node.children) == 4:
                funcName = funcDefNode.children[0].value
                funcType = funcDefNode.children[2].value + ":"   
                fParamsNode = funcDefNode.children[1]
                funcBodyNode = funcDefNode.children[3]
        
                params = _extractParamsfromFparamsNode(fParamsNode)

                    #add parameters to function symtable
                for param in params:
                    
                    paramName = param['name']
                    paramStr = param['string']
                    funcType += paramStr + ", "

                if node.visitCount == 1:
                    scope1 = self.globalSymTable.getFunctionEntry(funcName , funcType)['link']
                    scope2 = self.globalSymTable
                    self.scopeStack.append([scope1, scope2]) 
                else:
                    self.scopeStack.pop()
            else:
                funcName = funcDefNode.children[2].value
                funcType = funcDefNode.children[4].value + ":"
                scopeClassName = funcDefNode.children[0].value
                fParamsNode = funcDefNode.children[3]
                funcBodyNode = funcDefNode.children[5]
                functionSymTable = None
                
                params = _extractParamsfromFparamsNode(fParamsNode)

                    #add parameters to function symtable
                for param in params:
                    
                    paramName = param['name']
                    paramStr = param['string']
                    funcType += paramStr + ", "

                # try to get the class entry in the globalSymTable
                try:
                    classSymTable = self.globalSymTable.getClassEntryByName(scopeClassName)['link']
                    functionSymTable = classSymTable.getFunctionEntry(funcName , funcType)['link']

                    ##print(classSymTable.table)
                except classNotInTableError:
                    #funcDefNode.error = {'message' : "class " + scopeClassName + " does not exist!" , "line": str(funcDefNode.line)}
                    
                    pass
                    #after finding class entry and linked symTable try to find the find the function entry( originally added from the header
                except functionNotInTableError:
                    ##print(funcType)
                        #funcDefNode.error = {'message':"function " + scopeClassName + "::" + funcName + "of type " + funcType +  " does not exist!", "line": str(funcDefNode.line)}
                    pass
                else:
                    
                    if node.visitCount == 1:
                        self.scopeStack.append( [self.globalSymTable, classSymTable, functionSymTable])
                    else:
                        self.scopeStack.pop()

        if node.value == 'FuncBody':
            if node.parent.value == "Prog":  #main function
                if node.visitCount == 1:
                    self.scopeStack.append([self.globalSymTable , self.globalSymTable.getEntriesOfKind('Main')[0]['link']])
                else:
                    self.scopeStack.pop()        

        if node.value == "Variable":
            if node.visitCount == 1:
                self.semanticStack.append("VARIABLE")

            if node.visitCount == 2:
                if self.semanticStack != []: 
                    print(str(self.semanticStack))
                    varResult = self.popStackUntil("VARIABLE")
                    self.semanticStack.append(varResult["type"])
                    ##print(varResult["popCount"])
                    for i in range(varResult['popCount']):
                        if self.scopeStack != []:
                            self.scopeStack.pop()
        
        if node.value == "Return":
            if node.visitCount == 1:
                self.semanticStack.append("RETURN")
            elif node.visitCount == 2:
                self.printCurrentScope()
                if self.scopeStack == []:
                    #print("Function doesn't exist")
                    return
                funcTable = self.scopeStack[-1][-1]
                returnType = funcTable.name.split("type:")[1].split(":")[0]
                inputType = self.popStackUntil("RETURN")
        
                    #print("error processing return")
                
                inputType = inputType[0]
                if " " + inputType != returnType :
                    self._reportError({"message" : "Return type " + inputType + " incorrect. Should be " + returnType , "line" : node.line})
        
        if node.value == "VarMember":
            
                ##print(str(self.scopeStack) + str(self.semanticStack) + " at line " + str(node.line) + "\n \n\n")
                #if self.semanticStack == [] or (self.semanticStack != [] and type(self.semanticStack[-1]) != dict):
                    if len(node.children) == 1:
                        if node.visitCount ==2:
                                varName  = node.children[0].value
                                varEntry = self._getVariableEntryFromScope(varName)
                                if varEntry: 
                                        varType = varEntry['Type']
                                        try:
                                            scopeElement = self.globalSymTable.getClassEntryByName(varType)['link']
                                        except classNotInTableError:
                                            if "[" in varType:
                                                varType = ''.join([i for i in varType if not i.isdigit()])
                                            self.scopeStack.append([])
                                            if node.numberOfSiblingsToTheRight() == 0:
                                                self.semanticStack.append({"type" : varType , "popCount" : node.numberOfSiblingsToTheLeft() + 1})
                                            pass
                                        else:
                                            ##print(str(scopeElement))
                                            scope = [self.globalSymTable , scopeElement]
                                            self.scopeStack.append(scope)
                                            if node.numberOfSiblingsToTheRight() == 0:
                                                ##print("here")
                                                self.semanticStack.append({"type" : varType , "popCount" : node.numberOfSiblingsToTheLeft() + 1})

                                #self.currentScope = 
                                else:
                                    self.semanticStack.append({"type" : "Undefined" , "popCount" : node.numberOfSiblingsToTheLeft()})
                                    self._reportError({"message" : "Undefined variable " + varName , 'line' : node.line}) 

                    else:
                        if node.children[1].value == "FuncCall":
                            if node.visitCount ==1:
                                self.scopeStack.append(self.scopeStack[-(1 + node.numberOfSiblingsToTheLeft())])
                                # for element in self.scopeStack[-1]:
                                #     #print(str(element))
                            elif node.visitCount == 2:
                                ##print(str(self.scopeStack[-1]))
                                self.scopeStack.pop()
                                funcName = node.children[0].value
                                funcCallNode = node.children[1]
                                paramNum = len(funcCallNode.children)
                                params = []
                                for i in range(paramNum):
                                    params.append(self.semanticStack.pop())
                                
                                funcType = ''
                                for param in params[::-1]:
                                    funcType += param + ", "
                                
                                #for element in self.scopeStack[-1]:
                                 #    #print(str(element))
                                ##print(funcType)
                                funcEntry = self._getFunctionFromScope(funcName, funcType)
                    
                                
                                if funcEntry:
                                    returnType = funcEntry['Type'].split(':')[0]
                                    ##print(returnType)
                                    ##print("here")
                                    try:
                                        scopeElement = self.globalSymTable.getClassEntryByName(returnType)['link']
                                    except classNotInTableError:
                                        self.scopeStack.append([])
                                        
                                        if node.numberOfSiblingsToTheRight() == 0:
                                            
                                            self.semanticStack.append({"type" : "Undefined" , "popCount" : node.numberOfSiblingsToTheLeft() + 1})
                                        pass
                                    else:
                                        ##print("here")
                                        scope = [self.globalSymTable , scopeElement]
                                        self.scopeStack.append(scope)
                                        if node.numberOfSiblingsToTheRight() == 0:
                                                self.semanticStack.append({"type" : returnType , "popCount" : node.numberOfSiblingsToTheLeft() + 1})
                                
                                else:
                                        self.semanticStack.append({"type" : "Undefined" , "popCount" : node.numberOfSiblingsToTheLeft()})
                                        self._reportError({"message" : "Undefined function " + funcName + " with params " + funcType, 'line' : node.line}) 
                        else:
                             if node.visitCount ==2:
                                arrName  = node.children[0].value
                                arrEntry = self._getVariableEntryFromScope(arrName)
                                if arrEntry: 
                                    arrType = arrEntry['Type'].replace("]" , "").replace("[" , "")
                                    ##print(varType)
                                    arrType = ''.join([i for i in arrType if not i.isdigit()])
                                    try:
                                        scopeElement = self.globalSymTable.getClassEntryByName(arrType)['link']
                                    except classNotInTableError:
                                        self.scopeStack.append([])
                                        if node.numberOfSiblingsToTheRight() == 0:
                                            self.semanticStack.append({"type" : arrType , "popCount" : node.numberOfSiblingsToTheLeft() + 1})
                                        pass

                                    else:
                                        ##print(str(scopeElement))
                                        scope = [self.globalSymTable , scopeElement]
                                        self.scopeStack.append(scope)
                                        if node.numberOfSiblingsToTheRight() == 0:
                                            ##print("here")
                                            self.semanticStack.append({"type" : arrType , "popCount" : node.numberOfSiblingsToTheLeft() + 1})
                                else:
                                    self.semanticStack.append({"type" : "Undefined" , "popCount" : node.numberOfSiblingsToTheLeft()})
                                    self._reportError({"message" : "Undefined variable " + arrName , 'line' : node.line}) 

        if node.value == "Term":
            if node.visitCount == 2:
                if len(node.children) == 3:
                    #print("Excecuting term" + str(self.semanticStack) + " at line " + str(node.line))
                    
                    ops = self.popStackUntil("TERM")
                    
                    if len(set(ops)) != 1:
                        self._reportError({"message" : "Incompatible types " + str(set(ops)) , "line": node.line})
                        self.semanticStack.append("Undefined")
                    elif len(set(ops)) == 1:
                        for op in set(ops):
                            self.semanticStack.append(op)
            elif node.visitCount == 1:
                if len(node.children) == 3:
                    self.semanticStack.append("TERM")

        if node.value == "ArithExpr":
            
            if node.visitCount == 2:
                if len(node.children) == 3:
                    #print("Excecuting arith" + str(self.semanticStack) + " at line " + str(node.line))
                    
                    ops = self.popStackUntil("ARITHEXPR")
                    
                    if len(set(ops)) != 1:
                        self._reportError({"message" : "Incompatible types " + str(set(ops)) , "line": node.line})
                        self.semanticStack.append("Undefined")
                    elif len(set(ops)) == 1:
                        for op in set(ops):
                            self.semanticStack.append(op)
            elif node.visitCount == 1:
                if len(node.children) == 3: 
                    self.semanticStack.append("ARITHEXPR")
        

        if node.value == "Assign":
            if node.visitCount == 2:
                if len(node.children) == 3:
                    #print("Excecuting assign:" + str(self.semanticStack) + " at line " + str(node.line))
                    
                    ops = self.popStackUntil("ASSIGN")
                    

                    if len(set(ops)) != 1:
                        self._reportError({"message" : "Incompatible types " + str(set(ops)) , "line": node.line})
            elif node.visitCount == 1:
                if len(node.children) == 3:
                    self.semanticStack.append("ASSIGN")
        

        if node.value == "relExpr":
            if node.visitCount == 2:
                if len(node.children) == 3:
                    #print("Excecuting comparison:" + str(self.semanticStack) + " at line " + str(node.line))
                    
                    ops = self.popStackUntil("RELEXPR")
                    
                    if len(set(ops)) != 1:
                        self._reportError({"message" : "Incompatible types " + str(set(ops)), "line": node.line})
            elif node.visitCount == 1:
                if len(node.children) == 3:
                    self.semanticStack.append("RELEXPR")
        
        #if node.value == "write":
         #   if node.visitCount == 2: 
          #      self.semanticStack.pop()                   

        if node.type == "intNum": 
            if node.visitCount == 1: 
                self.semanticStack.append("integer")

        if node.type == "floatNum":
            if node.visitCount == 1:
                self.semanticStack.append("float")               


    def _reportError(self , errorObj):
            self.ErrorFile.write(errorObj['message'] + " [ line:" + str(errorObj['line']) + "]\n")


    def popStackUntil(self,token):
            rslt = []
            i = 0
            x  = len(self.semanticStack)
            while i < x:
                element = self.semanticStack.pop()
                
                if element == token: #means marker has been found. Nodes beyond this marker do not belong to this node
                    break
                rslt.append(element)        
                i += 1
            return rslt


    def _checkIfTypeExists(self, typeStr):
            types = self.globalSymTable.getNamesOfKind("Class")
            types.extend(['integer' , 'float' , 'void'])
            if typeStr not in types:
                raise undeclaredTypeError


    def printCurrentScope(self):
            rslt = []
            if self.scopeStack != []:
                for element in self.scopeStack[-1]:
                    rslt.append(element.name)
            #print(str(rslt))


    def _getVariableEntryFromScope(self , name):
            if self.scopeStack != []:
                for element in self.scopeStack[-1][::-1]:
                    entry = element.getVariableOrParamEntry(name)
                    if entry:
                        return entry

    def _getFunctionFromScope(self, name, type):
            if self.scopeStack != []:
                for element in self.scopeStack[-1][::-1]:
                    entry = element.getFunctionEntryfromParams(name , type)
                    if entry:
                        return entry


                        

    def _cehckIfVariableInScope(self ,name , scope):
            scopeEntriesTotal = []
            for element in scope:
                #namesInScoep
                vars = element.getNamesOfKind("Variable")
                funcs = element.getNamesOfKind("Function")
                params = element.getNamesOfKind("Param")

