class LabelAlreadyExistsError(Exception):
    pass

class IllegalRegisterToWriteTo(Exception):
    pass

class IllegalRegisterToReadFrom(Exception):
    pass

class MoonGateway:
    def __init__(self):
        self.availableRegisters = set(range(0,15))
        self.labels = {}
        self.outFile = open("moon/outFile.m" , "w+")
        self.currentAddress = 0
        
        self.instructions = []
        self.dataDefinition = []

        self.literalId = 0
        self.labelId = 0

    #
    #Reserves a chunk of memory of size "bytes" with label "label"
    def reserveMemory(self, label, bytes):
            moonCode = label + "\tres\t" + str(bytes)
            self._addLabel(label , {
               'type' : "reservedMemory",
               'size' : bytes
            })
            self.dataDefinition.append(moonCode)
            self.currentAddress += bytes  

    #def writeToMemory(self, label, offsets, value):
        #self.loa          

    #Defines a word in memory with label "label" and stores "value"
    def defineWord(self, label, value):
        moonCode = label + "\tdw\t" + str(value)
        self.labels[label] = {
               'type' : "defined word",
               'size' : 4,
               'value' : value
            }
        self.dataDefinition.append(moonCode)
        self.currentAddress += 4
    
    #Loads a chunk of memory by Label into register and marks register as not available
    def loadWord(self, registerNumber, label):
        if registerNumber > 15:
            raise IllegalRegisterToWriteTo
        
        if registerNumber not in self.availableRegisters:
            raise IllegalRegisterToWriteTo

        moonCode = "\tlw\tr" + str(registerNumber) + "," + label + "(r0)"

        self.availableRegisters.remove(registerNumber)

        self.currentAddress += 4
        self.instructions.append(moonCode)

    #Stores word from register number "registerNumber" into memory at label "label" and marks register as available
    def storeWord(self, label, registerNumber):
        if registerNumber > 15:
            raise IllegalRegisterToReadFrom
        
        if registerNumber in self.availableRegisters:
            raise IllegalRegisterToReadFrom 
        
        moonCode = "\tsw\t" + label + "(r0)" + "," + "r" + str(registerNumber)  

        self.instructions.append(moonCode)
        self.currentAddress += 4

        self._freeRegisters([registerNumber])

    #adds values at addresses by Label and returns result label, handles register availability
    def add(self , op1Label, op2Label):
        self.loadWord(1 , op1Label)
        self.loadWord(2, op2Label)
        moonCode = "\tadd r3,r2,r1"
        self.instructions.append(moonCode)
        self.availableRegisters.remove(3)
        rsltLabel = self._generateLabel()
        self.reserveMemory(rsltLabel , 4)
        self.storeWord(rsltLabel, 3)
        self.currentAddress += 4
        self._freeRegisters([1,2,3])
        return rsltLabel

    #subtracts values at addresses by Label and returns result label, handles register availability
    def subtract(self , op1Label, op2Label):
        self.loadWord(1 , op1Label)
        self.loadWord(2, op2Label)
        moonCode = "\tsub r3,r2,r1"
        self.instructions.append(moonCode)
        print(str(self.availableRegisters))
        self.availableRegisters.remove(3)
        print(str(self.availableRegisters))
        rsltLabel = self._generateLabel()
        self.reserveMemory(rsltLabel , 4)
        self.storeWord(rsltLabel, 3)
        self.currentAddress += 4
        self._freeRegisters([1,2,3])
        return rsltLabel
    
    #subtracts values at addresses by Label and returns result label, handles register availability
    def multiply(self , op1Label, op2Label):
        self.loadWord(1 , op1Label)
        self.loadWord(2, op2Label)
        moonCode = "\tmul r3,r2,r1"
        self.instructions.append(moonCode)
        self.availableRegisters.remove(3)
        rsltLabel = self._generateLabel()
        self.reserveMemory(rsltLabel , 4)
        self.storeWord(rsltLabel, 3)
        self.currentAddress += 4
        self._freeRegisters([1,2,3])
        return rsltLabel
    
    #subtracts values at addresses by Label and returns result label, handles register availability
    def divide(self , op1Label, op2Label):
        self.loadWord(1 , op1Label)
        self.loadWord(2, op2Label)
        moonCode = "\tdiv r3,r2,r1"
        self.instructions.append(moonCode)
        self.availableRegisters.remove(3)
        rsltLabel = self._generateLabel()
        self.reserveMemory(rsltLabel , 4)
        self.storeWord(rsltLabel, 3)
        self.currentAddress += 4
        self._freeRegisters([1,2,3])
        return rsltLabel
    

    def print(self, label):
        self.loadWord(1, label)
        moonCode = "\tputc r1"
        self.instructions.append(moonCode)
        self.currentAddress += 4
        self._freeRegisters([1])
    
    def storeLiteral(self , value):
        self.literalId += 1
        self.defineWord("literal" + str(self.literalId) , value)
        return  "literal" + str(self.literalId)

    def _freeRegisters(self,registerNumbers):
        for registerNumber in registerNumbers:
            self.availableRegisters.add(registerNumber)
        
        self.availableRegisters = set(sorted(self.availableRegisters))

    def _addLabel(self, name , labelObj):
        if name in self.labels.keys():
            raise LabelAlreadyExistsError
        else: 
            self.labels[name] = labelObj

    def _generateLabel(self):
        self.labelId += 1
        return "label" + str(self.labelId)

    def writeToSrc(self):
        for str in self.dataDefinition:
            self.outFile.write(str + "\n")
        
        self.outFile.write("entry\n")
        for str in self.instructions:
            self.outFile.write(str + "\n")
        self.outFile.write("hlt")