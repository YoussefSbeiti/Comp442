def getRule(str):
        rule = {}
        splitStr = str.split("::=")
        rule['LHS'] = splitStr[0].replace(" " , "")
        rule['RHS'] = splitStr[1].rstrip("\n").replace('\'' , '')
        return rule

def getFirst(rhs):
    elements = rhs.split(" ")
    firstElement = elements[0]
    if firstElement in terminals:
        return firstElement
    else: return firstSets[firstElement]