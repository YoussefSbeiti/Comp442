from tabulate import tabulate 

class classNotInTableError(Exception):
    pass

class functionNotInTableError(Exception):
    pass

class duplicateVariableError(Exception):
    pass

class duplicateFunctionError(Exception):
    pass

class InvalidParamName(Exception):
    pass

class overshadowedDataMemberWarning(Exception):
    pass

class overshadowedFunctionMemberWarning(Exception):
    pass

class cyclicalDependencyError(Exception):
    pass

class duplicateClassError(Exception):
    pass

class overloadedFunctionWarning(Exception):
    pass

class overshadowedVariableMemberWarning(Exception):
    pass

class SymTable:
    def __init__(self , name = ""):
        self.entries = []
        self.name = name

    def addVariable(self, name, varType):
        

        entryValue = {'name' : name,
                                'kind': 'Variable',
                                'Type' : varType,
                                'link' :  None}

        for entry in self.entries:
            if (entry['kind'] == 'Variable' or entry['kind'] == 'Param') and entry['name'] == name:
                raise duplicateVariableError
                return

        self.entries.append(entryValue)

    def addFunction(self,name, funcType, link):
    
        entryValue = { 'name' : name,
                        'kind': 'Function',
                        'Type' : funcType,
                        'link' :  link}
        
        for entry in self.entries:
            if entry['name'] == name and entry['kind'] == 'Function' :
                if entry['Type'].split(':')[1] == funcType.split(':')[1]:
                #error += "Function with name " + name + " with the same param list already exists in this scope" 
                    raise duplicateFunctionError
                    return
                    
                else: 
                    self.entries.append(entryValue)
                    raise overloadedFunctionWarning
                    
        
        self.entries.append(entryValue)
        paramNames = link.getNamesOfKind('Param')
        erronousParams = set(paramNames).intersection(set(self.getNamesOfKind("Variable")))
        
        #print(bool(erronousParams))
        #if bool(erronousParams):
         #   raise InvalidParamName("Invalid param names: " + str(list(erronousParams)))
         #   return 

        #self.checkForFunctionShadownWarning(name , funcType)

    def getEntryByName(self , name):
        rslt = []
        for entry in self.entries:
            if entry['name'] == name:
                rslt.append(entry)
        return rslt

    def getFunctionEntry(self, name , funcType):
        for entry in self.entries:
            if entry['kind'] == 'Function':
                if entry['name'] == name:
                    if entry['Type'].split() == funcType.split():
                        return entry
        
        raise functionNotInTableError

    def getFunctionEntryfromParams(self, name , params):
        for entry in self.entries:
            if entry['kind'] == 'Function':
                if entry['name'] == name:
                    print(name)
                    print(entry['Type'].split(':')[1] == params)
                    if entry['Type'].split(':')[1] == params:
                        return entry
        

    def addParameter(self, name , paramType):
         self.entries.append({   'name' : name,
                                'kind': 'Param',
                                'Type' : paramType,
                                'link' :  None})
        

    def addClass(self, name , link):

        for entry in self.entries:
            if entry['kind'] == 'Class' and entry['name'] == name:
                raise duplicateClassError
                return

        self.entries.append({   'name' : name,
                                'kind': 'Class',
                                'Type' : None,
                                'link' :  link})
    
    def addInheritedClass(self, name, link):
    
        #set(self.getNamesOfKind("Variable")).intersection(set(link.getNamesOfKind("Variable")))
        parentInheritedClasses = link.getInheritanceList()
        for entry in  parentInheritedClasses:
            if entry['name'] == self.name:
                raise cyclicalDependencyError
                return

        self.entries.append({   'name' : name,
                                'kind': 'ParentClass',
                                'Type' : None,
                                'link' :  link})

    def getAllClassEntries(self):
        rslt = []
        for entry in self.entries:
            if entry['kind'] == 'Class':
                rslt.append(entry)
        return rslt

    def getInheritanceList(self):
        rslt = []
        for entry in self.entries:
            if entry['kind'] == 'ParentClass':
                rslt.append(entry)
        return rslt

    def getClassEntryByName(self, className):
        for entry in self.entries:
            if entry['kind'] == 'Class':
                if entry['name'] == className: 
                    return entry
        
        raise classNotInTableError


    def getAllParamEntries(self):
        rslt = []
        for entry in self.entries:
            if entry['kind'] == 'Param':
                rslt.append(entry)
        return rslt

    def __str__(self):
        rslt = "-------------------------------------\n"
        rslt += "Table Name: " + self.name + "\n"
        rslt += "------------------------------------\n"
        rows = []
        for entry in self.entries:
            rows.append([entry['name'] , entry['kind'] , str(entry['Type']) , str(entry['link'])])
        
        rslt+=tabulate(rows, headers = ['Name' , 'Kind', 'Type' , 'Link'], tablefmt="orgtbl")

        return rslt

    def __repr__(self):
        rslt = ''
        for entry in self.entries:
            rslt += str(entry)
        
        return rslt

    def symTableAsHtml(self):
        rows = []
        for entry in self.entries:
            rows.append([entry['name'] , entry['kind'] , str(entry['Type']) , str(entry['link'])])
        
        file = open('symTable.html' , "w+")
        file.write(tabulate(rows, headers = ['Name' , 'Kind', 'Type' , 'Link'], tablefmt="orgtbl"))      # read the entire file into a string
 

    def nameExistsInTable(self, name):
        for entry in self.entries:
            if entry['name'] == name:
                return True
        else: return False


    def getNameColumn(self):
        return list(filter(lambda name: name != None , list(map(lambda entry: entry['name'] , self.entries))))

    def getNamesOfKind(self , kind):
        return list(filter(lambda name: name != None , list(map(lambda entry: entry['name'] if entry['kind'] == kind else None, self.entries))))
    
    def getEntriesOfKind(self , kind):
        return list((filter(lambda name: name != None , list(map(lambda entry: entry if entry['kind'] == kind else None, self.entries)))))

    def checkVariableForWarnings(self , name):
        entriesToCheck = []
        parentEntries = self.getInheritanceList()
        for entry in parentEntries:
            entriesToCheck.extend(entry['link'].getEntriesOfKind('Variable'))
        for entryToCheck in entriesToCheck:        
                if entryToCheck['name'] == name and entryToCheck['kind'] == 'Variable':
                        raise overshadowedDataMemberWarning

    def getVariableOrParamEntry(self , name):
        for entry in self.entries:
            if entry['name'] == name and (entry['kind'] == 'Variable' or entry['kind'] == 'Param'):
                return entry


    #TO FIX: chained inheritance
    def checkFunctionForWarnings(self, name , funcType):
        isOverShadowed = False
        isOverLoaded = False
        entriesToCheck = []
        parentEntries = self.getInheritanceList()
        for entry in parentEntries:
            entriesToCheck.extend(entry['link'].getEntriesOfKind('Function'))
        for entryToCheck in entriesToCheck:        
                if entryToCheck['name'] == name and entryToCheck['kind'] == 'Function':
                    if entryToCheck['Type'].split(':')[1] == funcType.split(':')[1]:
                        isOverShadowed = True
                    else:
                        isOverLoaded = True
                        
        if isOverShadowed:
            raise overshadowedFunctionMemberWarning
        elif isOverLoaded:
            raise overloadedFunctionWarning

    
    def removeEntry(self ,name , kind, type):
        for entry in self.entries:
            if entry['name'] == name and entry['kind']== kind and entry['Type'] == type:
                print("Entry " + name + " of type " + type + " and kind " + kind + " was removed." )
                self.entries.remove(entry)
                return
        print("could not find entry to remove")
