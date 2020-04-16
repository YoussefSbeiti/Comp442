from semanticAnalyzer.SymTable import *
from semanticAnalyzer.SemanticTranslationUtils import  _extractInfoFromMemDeclNode
from semanticAnalyzer.SemanticTranslationUtils import _extractParamsfromFparamsNode


class SymTableCreator:

    def __init__(self):
        self.globalSymTable = SymTable("Global")


    def createSymTable(self, progNode):

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
                member = _extractInfoFromMemDeclNode(memberNode)

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

        
    def _createFunctionSymTable(self , funcDefNode):
        
        if len(funcDefNode.children) == 4: # check if is free function
                funcName = funcDefNode.children[0].value
                funcType = funcDefNode.children[2].value + ":"   
                fParamsNode = funcDefNode.children[1]
                funcBodyNode = funcDefNode.children[3]
                functionSymTable = SymTable(funcName + " type: " + funcType)
                isGlobalFunc = True
                try:
                    params = _extractParamsfromFparamsNode(fParamsNode)
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
            
            params = _extractParamsfromFparamsNode(fParamsNode)

                 #add parameters to function symtable
            for param in params:
                
                paramName = param['name']
                paramStr = param['string']
                funcType += paramStr + ", "

            # try to get the class entry in the self.globalSymTable
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

        
       