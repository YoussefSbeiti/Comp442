from parser.AST.Node import Node

class AST:

    def __init__(self , TokensToNeglect):
        self.root = Node()
        self.TokensToNeglect = TokensToNeglect

    def makeNodeTerminal(self,terminal): 
        return Node(terminal)

    def makeNode(self, type, semStack):
            
        node = Node(type)
        i = 1
        x = len(semStack)

        while i < x:
            element = semStack.pop()
            
            if element.value == "Marker"+type: #means marker has been found. Nodes beyond this marker do not belong to this node
                node.line = element.line
                break

            if not element.value in self.TokensToNeglect:
                if not  (element.value in ["Assign" ] and element.children == []):
                    node.addChildFromTheLeft(element)

            i += 1
        if(type == 'Prog'):
            self.root = node

        return node

        #ProgNode
        # if type == 'Prog':
        #     #execute semAction
        #     progNode = Node('Prog')
        #     i = 1
        #     x = len(semStack)
        #     while i < x:
        #         element = semStack.pop()
        #         progNode.addChild(element)
        #         i += 1
        #     self.root = progNode
        #     return progNode

        # if type == 'ClassList':
        #     classListNode  = Node('ClassList')
        #     i = 1
        #     x = len(semStack)
        #     while i < x:
        #         element = semStack.pop()
        #         classListNode.addChild(element)
        #         i += 1
        #     return classListNode

        # if type == 'Class':
        #     i = 1
        #     classNode = Node('class')
        #     print('popping ' + str(len(semStack)) + 'elements from stack')
        #     x = len(semStack)
        #     while i < x:
        #         element = semStack.pop()
        #         print(i)
        #         print('popped element: ' + str(element))
        #         if not element.value in self.TokensToNeglect:
        #             classNode.addChild(element)
        #         i += 1
        #     return classNode

        # if type == 'MemberDecl':
        #     i=1
        #     memberNode = Node(type)
        #     x = len(semStack)
        #     while i < x:
        #         element = semStack.pop()
        #         if not element.value in self.TokensToNeglect:
        #             memberNode.addChild(element)
        #         i += 1
        #     return memberNode


        # if type == 'MemberList':
        #     i=1
        #     memberNode = Node(type)
        #     x = len(semStack)
        #     while i < x:
        #         element = semStack.pop()
        #         if not element.value in self.TokensToNeglect:
        #             memberNode.addChild(element)
        #         i += 1
        #     return memberNode

