from Node import Node 
from graphviz import Digraph
    
dotFile = open('tree.gv' ,'w+')
tree  = Node('root')
node1 = Node('child1')
tree.addChild(node1)
tree.addChild(Node('child2'))



dot = Digraph()

tree.treeDOT(dot)

dotFile.write(dot.source)

dotFile.close()
