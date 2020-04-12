from semanticAnalyzer.SymTable import *
import re

class undeclaredTypeError(Exception):
    pass


class SemAnalyzer:
    

    def __init__(self):
        self.ErrorFile = open('SemanticErrors.txt' , 'w+')
        self.globalSymTable = SymTable("Global")
        
        self.scopeStack = [[self.globalSymTable]]
        self.semanticStack = []


    def createGlobalSymTable(self, progNode):

        classList = progNode.children[0]
        
        for classNode in classList.children:
            try:
                self.globalSymTable.addClass(classNode.children[0].value , self._createClassSymtable(classNode))
            except duplicateClassError:
                classNode.error = {"message" : "Duplicate class " + classNode.children[0].value , 'line' : classNode.line}
        funcList = progNode.children[1]

        for functionNode in funcList.children:
            self._createFunctionSymTable(functionNode)

        mainBody = progNode.children[2]
        mainSymTable = SymTable("Main")
        for varDeclNode in mainBody.children[0].children:
                varName = varDeclNode.children[1].value
                varTpye = varDeclNode.children[0].value
                if len(varDeclNode.children) == 3:
                        for arrSize in varDeclNode.children[2].children:
                            if arrSize.children == []:
                                varTpye += "[]"
                            else:
                                varTpye += "[" + arrSize.children[0].value + "]"
                try:
                    mainSymTable.addVariable(varName , varTpye)
                except duplicateVariableError:
                    varDeclNode.error = {'message':"Duplicate variable " + varName , "line" : str(varDeclNode.line)} 

        self.globalSymTable.entries.append({'name' : "Main" , "kind" : "Main" , "Type" : None , 'link' : mainSymTable})

    #
    #Create class SymbolTable with function entries as well as there corresponding symbol table
    #
    def _createClassSymtable(self, classNode):
        

        className = classNode.children[0].value
        classSymTable = SymTable(className)         

        #
        #Adding member elements: variable and functions
        #
        memberList = classNode.children[2].children
        for memberNode in memberList:
            member = self._extractInfoFromMemDeclNode(memberNode)

            if member['kind'] == 'Function':

                name = member['name']
                funcType = member['type']
                params = member['params']

                funcSymTable = SymTable(className + "::" +name + " type: " + funcType)
                
                for param in params:
                    funcSymTable.addParameter( param['name'] ,param['string'])
        
                try : 
                    classSymTable.addFunction(name , funcType , funcSymTable)
                except (duplicateFunctionError , overloadedFunctionWarning) as error:
                    if error.__class__.__name__ == 'duplicateFunctionError':               
                        memberNode.error = {'message' : "Duplicate Function " + name, 'line' : memberNode.line}
                    else:
                        memberNode.warning = {'message' : "Overloaded Function " + name , 'line' : memberNode.line}
            else: 
                name = member['name']
                memberType = member['type']
                try:
                    classSymTable.addVariable(name , memberType)
                except duplicateVariableError:
                    memberNode.error = {'message' : "Duplicate variable " + name , "line" : str(memberNode.line)} 

        return classSymTable
      
       

    def _extractInfoFromMemDeclNode(self,  memberNode):
            rslt = {}
            isFunction = False
            for memberElement in memberNode.children:
                if memberElement.value == 'fParams': # if it contains fparams node that means it's a function
                    isFunction = True
                    break
            
            if isFunction:
                rslt['name'] = memberNode.children[1].value
                rslt['kind'] = 'Function'
                rslt['type'] =  memberNode.children[3].value + ":"
                rslt['params'] = self._extractParamsfromFparamsNode(memberNode.children[2])
                for param in rslt['params']:
                    paramName = param['name']
                    paramStr = param['string'] 
                    rslt['type'] += paramStr + ", "
            else:
                rslt['name'] = memberNode.children[2].value
                rslt['type'] = memberNode.children[1].value
                rslt['kind'] = 'Variable'
            
            return rslt
              
        

    def _extractParamsfromFparamsNode(self , fParamsNode):
        params = []
        for paramNode in fParamsNode.children:
                    paramName = paramNode.children[1].value
                    paramType = paramNode.children[0].value
                    #self._checkIfTypeExists(paramType)
                    if len(paramNode.children) == 3:
                        for arrSize in paramNode.children[2].children:
                            if arrSize.children == []:
                                paramType += "[]"
                            else:
                                paramType += "[" + arrSize.children[0].value +"]"
                    params.append({'name' : paramName , "string" : paramType})
                    
        return params

    def _createFunctionSymTable(self , funcDefNode):
        
        if len(funcDefNode.children) == 4: # check if is free function
                funcName = funcDefNode.children[0].value
                funcType = funcDefNode.children[2].value + ":"   
                fParamsNode = funcDefNode.children[1]
                funcBodyNode = funcDefNode.children[3]
                functionSymTable = SymTable(funcName + " type: " + funcType)
                isGlobalFunc = True
                try:
                    params = self._extractParamsfromFparamsNode(fParamsNode)
                except:
                    pass
                 #add parameters to function symtable
                else:
                    for param in params:
                    
                        paramName = param['name']
                        paramStr = param['string']
                        functionSymTable.addParameter(paramName, paramStr)
                        funcType += paramStr + ", "

                #add function to global symtable
                try:
                    self.globalSymTable.addFunction(funcName , funcType , functionSymTable) 
                except (duplicateFunctionError , overloadedFunctionWarning) as error:
                    if error.__class__.__name__ == 'duplicateFunctionError':               
                        funcDefNode.error = {'message' : "Duplicate Function " + funcName, 'line' : funcDefNode.line}
                    else:
                        funcDefNode.warning = {'message' : "Overloaded Function " + funcName , 'line' : funcDefNode.line}
            
        else: # else if it's class function
            funcName = funcDefNode.children[2].value
            funcType = funcDefNode.children[4].value + ":"
            scopeClassName = funcDefNode.children[0].value
            fParamsNode = funcDefNode.children[3]
            funcBodyNode = funcDefNode.children[5]
            functionSymTable = None
            
            params = self._extractParamsfromFparamsNode(fParamsNode)

                 #add parameters to function symtable
            for param in params:
                
                paramName = param['name']
                paramStr = param['string']
                funcType += paramStr + ", "

            # try to get the class entry in the globalSymTable
            try:
                classSymTable = self.globalSymTable.getClassEntryByName(scopeClassName)['link']
                #print(classSymTable.table)
            except classNotInTableError:
                funcDefNode.error = {'message' : "class " + scopeClassName + " does not exist!" , "line": str(funcDefNode.line)}
            # after finding class entry and linked symTable try to find the find the function entry( originally added from the header)
            else:
                try:
                    functionSymTable = classSymTable.getFunctionEntry(funcName , funcType)['link']
                except functionNotInTableError:
                    funcDefNode.error = {'message':"function " + scopeClassName + "::" + funcName + " of type " + funcType +  " does not exist!", "line": str(funcDefNode.line)}
        
        if functionSymTable:
            varListNode = funcBodyNode.children[0]

            #Add variables to the function symtable (whether it's class function or free function)
            for varDeclNode in varListNode.children:
                varName = varDeclNode.children[1].value
                varTpye = varDeclNode.children[0].value
                if len(varDeclNode.children) == 3:
                        for arrSize in varDeclNode.children[2].children:
                            if arrSize.children == []:
                                varTpye += "[]"
                            else:
                                varTpye += "[" + arrSize.children[0].value +"]"
                try:
                    functionSymTable.addVariable(varName , varTpye)
                except duplicateVariableError:
                    varDeclNode.error = {'message':"Duplicate variable " + varName , "line" : str(varDeclNode.line)} 

    def _reportError(self , errorObj):
        self.ErrorFile.write(errorObj['message'] + " [ line:" + str(errorObj['line']) + "]\n")


    def traverseTree(self, node):
        self.nodeHandler(node)
        #print(node.value)
        if node.children != []:
            for child in node.children:
                self.traverseTree(child)
        
        self.nodeHandler(node)
        #print(node.value)
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
                member = self._extractInfoFromMemDeclNode(memberNode)

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
        
                params = self._extractParamsfromFparamsNode(fParamsNode)

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
                
                params = self._extractParamsfromFparamsNode(fParamsNode)

                    #add parameters to function symtable
                for param in params:
                    
                    paramName = param['name']
                    paramStr = param['string']
                    funcType += paramStr + ", "

                # try to get the class entry in the globalSymTable
                try:
                    classSymTable = self.globalSymTable.getClassEntryByName(scopeClassName)['link']
                    functionSymTable = classSymTable.getFunctionEntry(funcName , funcType)['link']

                    #print(classSymTable.table)
                except classNotInTableError:
                    #funcDefNode.error = {'message' : "class " + scopeClassName + " does not exist!" , "line": str(funcDefNode.line)}
                    
                    pass
                    #after finding class entry and linked symTable try to find the find the function entry( originally added from the header
                except functionNotInTableError:
                    #print(funcType)
                        #funcDefNode.error = {'message':"function " + scopeClassName + "::" + funcName + "of type " + funcType +  " does not exist!", "line": str(funcDefNode.line)}
                    pass
                else:
                    
                    if node.visitCount == 1:
                        self.scopeStack.append([classSymTable, functionSymTable, self.globalSymTable])
                    else:
                        self.scopeStack.pop()

        if node.value == 'FuncBody':
            if node.parent.value == "Prog":  #main function
                if node.visitCount == 1:
                    self.scopeStack.append([self.globalSymTable , self.globalSymTable.getEntriesOfKind('Main')[0]['link']])
                else:
                    self.scopeStack.pop()        

        if node.value == "Variable":
             if node.visitCount == 2:
                if self.semanticStack != []: 
                    varResult = self.semanticStack.pop()
                    self.semanticStack.append(varResult["type"])
                    #print(varResult["popCount"])
                    for i in range(varResult['popCount']):
                        if self.scopeStack != []:
                            self.scopeStack.pop()
        
        if node.value == "Return":
            if node.visitCount == 1:
                self.semanticStack.append("RETURN")
            elif node.visitCount == 2:
                funcTable = self.scopeStack[-1][::-1][-1]
                returnType = funcTable.name.split("type:")[1].split(":")[0]
                inputType = self.popStackUntil("RETURN")
                if len(inputType) != 1:
                    print("error processing return")
                else :
                    inputType = inputType[0]
                if " " + inputType != returnType :
                    self._reportError({"message" : "Return type " + inputType + " incorrect. Should be " + returnType , "line" : node.line})
        
        if node.value == "VarMember":
            
                #print(str(self.scopeStack) + str(self.semanticStack) + " at line " + str(node.line) + "\n \n\n")
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
                                            #print(str(scopeElement))
                                            scope = [self.globalSymTable , scopeElement]
                                            self.scopeStack.append(scope)
                                            if node.numberOfSiblingsToTheRight() == 0:
                                                #print("here")
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
                                #     print(str(element))
                            elif node.visitCount == 2:
                                #print(str(self.scopeStack[-1]))
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
                                 #    print(str(element))
                                #print(funcType)
                                funcEntry = self._getFunctionFromScope(funcName, funcType)
                    
                                
                                if funcEntry:
                                    returnType = funcEntry['Type'].split(':')[0]
                                    #print(returnType)
                                    #print("here")
                                    try:
                                        scopeElement = self.globalSymTable.getClassEntryByName(returnType)['link']
                                    except classNotInTableError:
                                        self.scopeStack.append([])
                                        
                                        if node.numberOfSiblingsToTheRight() == 0:
                                            
                                            self.semanticStack.append({"type" : "Undefined" , "popCount" : node.numberOfSiblingsToTheLeft() + 1})
                                        pass
                                    else:
                                        #print("here")
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
                                    #print(varType)
                                    arrType = ''.join([i for i in arrType if not i.isdigit()])
                                    try:
                                        scopeElement = self.globalSymTable.getClassEntryByName(arrType)['link']
                                    except classNotInTableError:
                                        self.scopeStack.append([])
                                        if node.numberOfSiblingsToTheRight() == 0:
                                            self.semanticStack.append({"type" : arrType , "popCount" : node.numberOfSiblingsToTheLeft() + 1})
                                        pass

                                    else:
                                        #print(str(scopeElement))
                                        scope = [self.globalSymTable , scopeElement]
                                        self.scopeStack.append(scope)
                                        if node.numberOfSiblingsToTheRight() == 0:
                                            #print("here")
                                            self.semanticStack.append({"type" : arrType , "popCount" : node.numberOfSiblingsToTheLeft() + 1})
                                else:
                                    self.semanticStack.append({"type" : "Undefined" , "popCount" : node.numberOfSiblingsToTheLeft()})
                                    self._reportError({"message" : "Undefined variable " + arrName , 'line' : node.line}) 

        if node.value == "Term":
            if node.visitCount == 2:
                if len(node.children) == 3:
                    print("Excecuting term" + str(self.semanticStack) + " at line " + str(node.line))
                    
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
                    print("Excecuting arith" + str(self.semanticStack) + " at line " + str(node.line))
                    
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
                    print("Excecuting assign:" + str(self.semanticStack) + " at line " + str(node.line))
                    
                    ops = self.popStackUntil("ASSIGN")
                    

                    if len(set(ops)) != 1:
                        self._reportError({"message" : "Incompatible types " + str(set(ops)) , "line": node.line})
            elif node.visitCount == 1:
                if len(node.children) == 3:
                    self.semanticStack.append("ASSIGN")
        

        if node.value == "relExpr":
            if node.visitCount == 2:
                if len(node.children) == 3:
                    print("Excecuting comparison:" + str(self.semanticStack) + " at line " + str(node.line))
                    
                    ops = self.popStackUntil("RELEXPR")
                    
                    if len(set(ops)) != 1:
                        self._reportError({"message" : "Incompatible types " + str(set(ops)), "line": node.line})
            elif node.visitCount == 1:
                if len(node.children) == 3:
                    self.semanticStack.append("RELEXPR")
        
        if node.value == "write":
            if node.visitCount == 2: 
                self.semanticStack.pop()                   

        if node.type == "intNum": 
            if node.visitCount == 1: 
                self.semanticStack.append("integer")

        if node.type == "floatNum":
            if node.visitCount == 1:
                self.semanticStack.append("float")               
    
    def _getVariableEntryFromScope(self , name):
        if self.scopeStack != []:
            for element in self.scopeStack[-1][::-1]:
                entry = element.getVariableOrParamEntry(name)
                if entry:
                    return entry

    def _getFunctionFromScope(self,name, type):
        if self.scopeStack != []:
            for element in self.scopeStack[-1][::-1]:
                entry = element.getFunctionEntryfromParams(name , type)
                if entry:
                    return entry


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
                    


    def _cehckIfVariableInScope(self ,name , scope):
        scopeEntriesTotal = []
        for element in scope:
            #namesInScoep
            vars = element.getNamesOfKind("Variable")
            funcs = element.getNamesOfKind("Function")
            params = element.getNamesOfKind("Param")

    def analyzeTree(self, progNode):

        self.createGlobalSymTable(progNode)
        
        self.traverseTree(progNode)

        return self.globalSymTable

    
    def _checkIfTypeExists(self , typeStr):
        types = self.globalSymTable.getNamesOfKind("Class")
        types.extend(['integer' , 'float' , 'void'])
        if typeStr not in types:
            raise undeclaredTypeError
        
