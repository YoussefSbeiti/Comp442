from semanticAnalyzer.MemoryReference import MemoryReference

class LabelAlreadyExistsError(Exception):
    pass

class IllegalRegisterToWriteTo(Exception):
    pass

class IllegalRegisterToReadFrom(Exception):
    pass

class MoonGateway:
    def __init__(self):
        self.availableRegisters = set(range(1,12))
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
    
    #Loads a chunk of memory by memory reference into register and marks register as not available
    def loadWord(self, registerNumber, memReference):

        offsetReg = self._storeMemRefOffsetsInRegister(memReference) 
        label = memReference.label
        moonCode = "\tlw\tr" + str(registerNumber) + "," + label + "(r" + str(offsetReg) + ")"
        
        if offsetReg != 0:
            self._freeRegisters([offsetReg])

        self.instructions.append(moonCode)

    #Stores word from register number "registerNumber" into memory reference and marks register as available
    def storeWord(self, memReference, registerNumber):
        
        print(memReference)
        offsetReg = self._storeMemRefOffsetsInRegister(memReference)
        label = memReference.label

        moonCode = "\tsw\t" + label + "(r" + str(offsetReg) + ")" + "," + "r" + str(registerNumber)  

        self.instructions.append(moonCode)

        if offsetReg != 0:
            self._freeRegisters([offsetReg])
               
    #adds values at addresses by Label and returns result label, frees up registers used in the process
    def binaryOp(self ,operator, op1Label, op2Label):
        registersToUse = self.getNextFreeRegisters(3)
        self.loadWord(registersToUse[0] , op1Label)
        self.loadWord(registersToUse[1], op2Label)
        
        if operator == "+":
            moonCode = "\tadd r" + str(registersToUse[2]) + ",r" + str(registersToUse[0]) + ",r" + str(registersToUse[1])
        elif operator == "-":
            moonCode = "\tsub r" + str(registersToUse[2]) + ",r" + str(registersToUse[0]) + ",r" + str(registersToUse[1])
        elif operator == "*":
            moonCode = "\tmul r" + str(registersToUse[2]) + ",r" + str(registersToUse[0]) + ",r" + str(registersToUse[1])
        elif operator == "/":
            moonCode = "\tdiv r" + str(registersToUse[2]) + ",r" + str(registersToUse[0]) + ",r" + str(registersToUse[1])
        elif operator == "or":
            moonCode = "\tor r" + str(registersToUse[2]) + ",r" + str(registersToUse[0]) + ",r" + str(registersToUse[1])
        elif operator == "and":
            moonCode = "\tdiv r" + str(registersToUse[2]) + ",r" + str(registersToUse[0]) + ",r" + str(registersToUse[1])

        self.instructions.append(moonCode)
        label = self._generateLabel()
        rsltMemRef = MemoryReference(label)
        self.reserveMemory(label , 4)
        self.storeWord(rsltMemRef, 3)
        self.currentAddress += 4
        self._freeRegisters(registersToUse)
        return rsltMemRef

    def relOp(self, operator, op1Label, op2Label):
        registersToUse = self.getNextFreeRegisters(3)
        self.loadWord(registersToUse[0] , op1Label)
        self.loadWord(registersToUse[1], op2Label)
        
        if operator == "<":
            moonCode = "\tclt r" + str(registersToUse[2]) + ",r" + str(registersToUse[0]) + ",r" + str(registersToUse[1])
        elif operator == ">":
            moonCode = "\tcgt r" + str(registersToUse[2]) + ",r" + str(registersToUse[0]) + ",r" + str(registersToUse[1])
        elif operator == ">=":
            moonCode = "\tcge r" + str(registersToUse[2]) + ",r" + str(registersToUse[0]) + ",r" + str(registersToUse[1])
        elif operator == "<=":
            moonCode = "\tcle r" + str(registersToUse[2]) + ",r" + str(registersToUse[0]) + ",r" + str(registersToUse[1])
        elif operator == "==":
            moonCode = "\tceq r" + str(registersToUse[2]) + ",r" + str(registersToUse[0]) + ",r" + str(registersToUse[1])
        elif operator == "!=":
            moonCode = "\tcne r" + str(registersToUse[2]) + ",r" + str(registersToUse[0]) + ",r" + str(registersToUse[1])
        
        self.instructions.append(moonCode)
        label = self._generateLabel()
        rsltMemRef = MemoryReference(label)
        self.reserveMemory(label , 4)
        self.storeWord(rsltMemRef, 3)
        self.currentAddress += 4
        self._freeRegisters(registersToUse)
        return rsltMemRef

    def bz(self, conditionMemRef, labelToBranchTo):
        registers = self.getNextFreeRegisters(1)
        self.loadWord(registers[0], conditionMemRef)
        moonCode = "\tbz r" + str(registers[0]) + ", " + labelToBranchTo 
        self.instructions.append(moonCode)
        self._freeRegisters(registers)

    def j(self, label):
        moonCode = "\tj " + label
        self.instructions.append(moonCode)

    def writeLine(self, line):
        self.instructions.append(line)

    #adds Immediate value to register
    def addImmediateRegister(self, registerNum, value):
        self.availableRegisters.remove(registerNum)
        moonCode = "\taddi r2,r" + str(registerNum) + "," + str(value)
        self.instructions.append(moonCode)

    def loadZeroToRegister(self, regNumber):
        moonCode = "\tadd r"+ str(regNumber) + ", r0,r0"
        self.instructions.append(moonCode)

    def getNextFreeRegisters(self, numOfRegisters):
        registers = []
        for i in range(numOfRegisters):
            registers.append(self._getNextAvailableRegister())
        return registers

    def addMemRefToRegister(self,regNumber, memRef):
        tempRegister = self._getNextAvailableRegister()
        self.loadWord(tempRegister , memRef)
        moonCode = "\tadd r" + str(regNumber) + ", r" + str(regNumber) + ", r" + str(tempRegister)
        self.instructions.append(moonCode)
        self._freeRegisters([tempRegister])

    def multiplyImmediateMemRef(self, wordLocation, value): 
        registers = self.getNextFreeRegisters(1)
        self.loadWord(registers[0],wordLocation)
        moonCode = "\tmuli r" + str(registers[0]) + ",r" + str(registers[0]) + "," + str(value)
        self.instructions.append(moonCode)
        self.storeWord(wordLocation, registers[0])
        self.currentAddress += 4
        self._freeRegisters(registers)

    def loadWordToMemRef(self, destMemRef, srcMemRef):
        #load rhs (ie right hand side value) label into register 1
        registers = self.getNextFreeRegisters(1)
        self.loadWord(registers[0], srcMemRef)
        #store register 1 contents into reserved word labeled lhs(ir variable name)
        self.storeWord(destMemRef,registers[0])

        self._freeRegisters(registers)

    def print(self, label):
        registers = self.getNextFreeRegisters(1)
        self.loadWord(registers[0], label)
        moonCode = "\tsw -8(r14),r" + str(registers[0]) + "\n"
        moonCode += "\taddi r" + str(registers[0]) +", r0,buf" + "\n"
        moonCode += "\tsw -12(r14),r" + str(registers[0]) + "\n"
        moonCode += "\tjl r15, intstr\n"
        moonCode += "\tsw -8(r14),r13\n"
        moonCode += "\tjl r15,putstr"
        
        self.instructions.append(moonCode)
        self._freeRegisters(registers)
    
    def read(self,memRef):
        registers = self.getNextFreeRegisters(1)
        #moonCode = "\tsw -8(r14),r" + str(registers[0]) + "\n"
        moonCode = "\taddi r" + str(registers[0]) +", r0,buf" + "\n"
        moonCode += "\tsw -8(r14),r" + str(registers[0]) + "\n"
        moonCode += "\tjl r15,getstr\n"
        moonCode += "\tjl r15, strint\n"
        self.instructions.append(moonCode)
        self.storeWord(memRef, 13)
        self._freeRegisters(registers)

    def _processMemReference(self, memReference):
        tempRegNum =  next(iter(self.availableRegisters))
        offsetLabel = memReference.offsetLabel
        if offsetLabel:
            self.loadWord(tempRegNum , {"label" : offsetLabel , "offsetLabel" : None})
            return tempRegNum
        else :
            return 0
    
    def _storeMemRefOffsetsInRegister(self , memReference):
        if memReference.offsets:
            totalOffsetRegister = self._getNextAvailableRegister()
            self.loadZeroToRegister(totalOffsetRegister) # get register to hold the offset calculation
            for offset in memReference.offsets: # iterate through the offsets which could be integers(for immediate add) or memoryReferences
                self.addMemRefToRegister(totalOffsetRegister, offset)
            return totalOffsetRegister
        else:
            return 0

    def _getNextAvailableRegister(self):
        regNumber = next(iter(self.availableRegisters))
        self.availableRegisters.remove(regNumber)
        return regNumber

    def storeLiteral(self , value):
        self.literalId += 1
        self.defineWord("literal" + str(self.literalId) , value)
        return  MemoryReference("literal" + str(self.literalId))

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
        self.outFile.write("\taddi r14,r0,topaddr\n")
        for str in self.instructions:
            self.outFile.write(str + "\n")
        self.outFile.write("hlt\n")
        self.outFile.write("\tbuf\tres 20 \n")
        