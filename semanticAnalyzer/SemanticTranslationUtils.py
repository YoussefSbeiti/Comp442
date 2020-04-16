

def _extractInfoFromMemDeclNode(memberNode):
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
                rslt['params'] = _extractParamsfromFparamsNode(memberNode.children[2])
                for param in rslt['params']:
                    paramName = param['name']
                    paramStr = param['string'] 
                    rslt['type'] += paramStr + ", "
            else:
                rslt['name'] = memberNode.children[2].value
                rslt['type'] = memberNode.children[1].value
                rslt['kind'] = 'Variable'
            
            return rslt
              
        

def _extractParamsfromFparamsNode(fParamsNode):
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

