# -*- coding:utf-8 -*-

from optparse import OptionParser
import re
import string
import os

def calcuWholeChild(entryID,nodeRelationDict):
    childSet = set(nodeRelationDict[entryID])
    flag = 1
    nodeSet = set(nodeRelationDict.keys())
    while 1:
        if flag == 0:
            break
        flag = 0
        flagSet = set(childSet)
        for nodeID in flagSet:
            if nodeID not in nodeSet:
                continue
            childSet = childSet | set(nodeRelationDict[nodeID])
        if childSet != flagSet:
            flag = 1
    return childSet



def extractCallgraph(nodeInfoDict,nodeRelationDict,mcallByDict):
    reRule1 = '^\s+Node0x(\w+) \[shape=record,label=\"{(.+)}\"];'
    reRule2 = '^\s+Node0x\w+ -> Node0x(\w+);'
    reRule3 = '^\s+Node0x(\w+) -> Node0x(\w+);'

    with open('callgraph.dot') as f:
        for line in f.readlines():
            defNode = re.findall(reRule1,line)
            if defNode:
                nodeID = defNode[0][0]
                nodeRelationDict[nodeID] = set([])
                nodeInfoDict[nodeID] = defNode[0][1] #save the name of node
                continue
            else :
                destNodeID = re.findall(reRule3,line)
                if destNodeID:
                    callNode = destNodeID[0][1]
                    nodeRelationDict[nodeID].add(callNode)
                    if nodeInfoDict[destNodeID[0][0]] != 'external node':
                        if callNode not in mcallByDict.keys():
                            mcallByDict[callNode] = []
                        mcallByDict[callNode].append(destNodeID[0][0])
                continue


def extractFuncBloc(inf,funcDict):
    reRule1 = 'define.+@([\w]+)\(.*\).*#\d+.*{'
    reRule2 = 'declare .+ @([a-z0-9A-Z_\.]+).+ #\d+'
    with open(inf,'r') as f:
        funcContent = ''
        funcName = ''
        funcDict['env'] = ''
        flag = 0
        for line in f.readlines():
            line = line.encode('utf-8')
            if line.startswith('attributes #'):
                break            
            defFunc = re.findall(reRule1,line)
            if not defFunc:
                defIncFunc = re.findall(reRule2,line)
                if defIncFunc:
                    continue
                if funcName == ''  and line != '\n' and (not re.findall('; Function Attrs:',line)):
                    if not line.startswith('@'):
                        funcDict['env'] += line
                if line.startswith('}') and funcName != '':
                    funcContent += line
                    funcContent = funcContent.encode('utf-8')
                    funcDict[funcName] = funcContent
                    funcContent = ''
                    funcName = ''
                elif funcName != '':
                    funcContent += line
                continue
            funcName = defFunc[0]
            funcContent += line


def replaceVarNumber(codeStr,baseCount):
    variList = re.findall(r'%(\d+)\W', codeStr)
    for var in variList:
        tempVar = string.atoi(var) + baseCount
        codeStr = re.sub('%'+ var +r'(\W)', '%' + str(tempVar) + r'\1', codeStr)
    return codeStr

def find_second_last(string,str):
    last_position = -1
    length = len(string)
    while True:
        position = string.find(str ,last_position + 1)
        if position == length - 1:
            return last_position
        last_position = position


def counteLargestNumInList(numStrList):
    numList = []
    for tempNum in numStrList:
        numList.append(int(tempNum))
    largestNum = 0
    for tempNum in numList:
        if tempNum > largestNum:
            largestNum = tempNum
    return largestNum



def sliceProduce(entryName, funcDict, assertFunc,useFuncList,baseCount = 0):
    nodeNametoIDDict = {v: k for k, v in nodeInfoDict.items()}
    funcNameSet = set(funcDict.keys())
    if entryName not in funcNameSet:
        return '',baseCount
    reRule = 'call.+@(\w+)\('
    reRule1 = 'define.+@([\w]+)\(.*\).*#\d+.*{'
    slicefinal = ''
    paraNumList = re.findall('%(\d+)',funcDict[entryName])

    entryLine = funcDict[entryName].split('\n')
    slideCounter = baseCount + counteLargestNumInList(paraNumList) + 1
    insertFlag = 0
    for line in entryLine:
        if line == '':
            continue
        
        if insertFlag != 0:
            insertFlag -= 1
            continue
        
        callFuncList = re.findall(reRule, line)
        if not callFuncList:
            if baseCount == 0:
                slicefinal += (line)
            else:
                slicefinal += (replaceVarNumber(line, baseCount))
            defineFuncList = re.findall(reRule1,line)
            if (len(defineFuncList) > 0 and defineFuncList[0] == assertFunc):
                slicefinal += " #_%$$KEY_FUNC$$%_#\n"
            else:
                slicefinal += "\n"
            continue
        for callFuncName in callFuncList:
            if baseCount == 0:
                slicefinal += (line + '\n')
            else:
                slicefinal += (replaceVarNumber(line, baseCount) + '\n')
            callFuncID = nodeNametoIDDict[callFuncName]
            if (callFuncID in nodeCoverDict[nodeNametoIDDict[assertFunc]] and entryName != assertFunc and entryName not in fatherchain and callFuncName != assertFunc) or callFuncName in useFuncList:
                continue
            useFuncList.append(callFuncName)
            ret = sliceProduce(callFuncName, funcDict, assertFunc, useFuncList, slideCounter)
            slicefinal += ret[0]
            slideCounter = ret[1]
    return slicefinal,slideCounter


def filterFuncBloc(nodeRelationDict,nodeCoverDict,funcBlocDict,assertFuncName): 
    nodeNametoIDDict = {v: k for k, v in nodeInfoDict.items()}
    if assertFuncName not in nodeNametoIDDict.keys():
    	return
    assertFuncID = nodeNametoIDDict[assertFuncName]
    for key in nodeRelationDict.keys():
        childSet = calcuWholeChild(key,nodeRelationDict)
        childSet.add(key)
        nodeCoverDict[key] = childSet
    for funcName in funcBlocDict.keys():
        if funcName == 'env':
            continue
        if funcName not in nodeNametoIDDict.keys():
        	continue
        funcID = nodeNametoIDDict[funcName]
        if funcID in nodeCoverDict[assertFuncID] or funcName in fatherchain:
            continue
        else:
            funcBlocDict.pop(funcName)

def getFunFromName(filename):
    idx1 = filename.rfind('#')
    idx2 = filename[0:idx1].rfind('#')
    return filename[idx2+1:idx1]

def getEntryFromDict(massertFunc,mnodeInfoDict,mcallByDict):
    assertNodeId = ''
    for item in mnodeInfoDict:
        if mnodeInfoDict[item] == massertFunc:
            assertNodeId = item
    keyset = set(mcallByDict.keys())
    tmpfun = assertNodeId
    for i in range(1): 
        if tmpfun in keyset and len(mcallByDict[tmpfun])>0:
            for fatherfun in mcallByDict[tmpfun]:
                if fatherfun != tmpfun and mnodeInfoDict[fatherfun] in funcList:
                    tmpfun = fatherfun
                    fatherchain.insert(0,mnodeInfoDict[tmpfun])
                    break
        else:
            break
    if tmpfun in mnodeInfoDict.keys():
        return nodeInfoDict[tmpfun] 

def getExistDefineFunc(infile):
    regex = 'define.+@([\w]+)\(.*\).*#\d+.*{'
    funcName = ''
    with open(infile) as f:
        for line in f:
            mFunc = re.findall(regex,line)
            if mFunc:
                funcList.append(mFunc[0])



if __name__ == '__main__':
    parser = OptionParser()
    (options, args) = parser.parse_args()
    nodeRelationDict = {} #key:nodeID u value:set(调用结点) v 
    nodeInfoDict = {} #key:nodeID value:nodename
    funcDict = {}  #保存函数名和函数体
    nodeCoverDict = {} #某一函数向下调用的所有函数
    callByDict = {} #key:v  value:u  v —> u
    funcList = [] #保存存在函数体的函数名
    fatherchain = [] #漏洞函数的调用函数（父函数）
    useFuncList = [] 
    if len(args) != 2:
        print 'Usage error, you need to declare source file and raw slice file.\n'
    else:
        slicefile = args[1] #flawtag.ll
        getExistDefineFunc(slicefile)

        extractCallgraph(nodeInfoDict,nodeRelationDict,callByDict)   

        extractFuncBloc(slicefile,funcDict)

        assertFunc = getFunFromName(slicefile)

        entryName = getEntryFromDict(assertFunc,nodeInfoDict,callByDict)

        #获取下方结点  nodeCoverDict包含所有子结点  funDict不包含无关函数
        filterFuncBloc(nodeRelationDict,nodeCoverDict,funcDict,assertFunc)

        print('entryName',entryName)

        useFuncList.append(entryName)
        ret = sliceProduce(entryName, funcDict, assertFunc,useFuncList)
        slicefinal = ret[0]
        fileName = slicefile[:-11]+'.final.ll'
        with open(fileName, 'w') as f:
            f.write(slicefinal )
            f.close()
