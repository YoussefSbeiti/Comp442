class Node:
    id = 0
    
    def __init__(self , value ='empty'):
        
        self.value = value

        self.parent = None

        self.children = []

        self.id = Node.id
        Node.id = Node.id+1
    
    def addChild(self, node):
        node.parent = self
        self.children.append(node)

    def addChildFromTheLeft(self, node):
        node.parent = self
        self.children.insert(0 , node)

    #def addToNodeFromLeft(self, node):
     #   if self.parent = None:
      #      self.parent = parent
        
    def __eq__(self, otherNode):
        return self is otherNode

    def nodeDOT(self , id = 0):
        return str(id) + "[label =\"" + self.value + "\"]"

    
    def treeDOT(self, dotObj): 
        #print(str(len(self.children)))  
        if len(self.children) == 0:
            dotObj.node(str(self.id) , self.value)
            if(self.parent):
                dotObj.edge(str(self.parent.id) , str(self.id))

        else:
            dotObj.node(str(self.id) , self.value)
            if(self.parent):
                dotObj.edge(str(self.parent.id) , str(self.id))
            for child in self.children:
                #print(child.children[0].value)
                #print(child.children)
                child.treeDOT(dotObj)

    def __str__(self):
        return "Node(" + self.value + ")"
