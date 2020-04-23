class MemoryReference:
    def __init__(self , label):
        self.label = label
        self.offsets = None
        
    def addOffsets(self, offsets):
        if self.offsets == None:
            self.offsets = []

        if type(offsets) is list:
            self.offsets.extend(offsets)
        elif type(offsets) is MemoryReference:
            self.offsets.append(offsets)

    def __str__(self):
        return "{Label: " + self.label + ", Offsets: " + str(self.offsets) +"}"
    
    def __repr__(self):
        return "{Label: " + str(self.label) + ", Offsets: " + str(self.offsets) + "}"
