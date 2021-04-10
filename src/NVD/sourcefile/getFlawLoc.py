# -*- coding:utf-8 -*-
from optparse import OptionParser
import os
import re
import pickle


slice2FlawDict = {'test':[0]}
focusandfuncofslice = {}


def getFlawLine(curpath, fileName):
    filePath = os.path.join(curpath, fileName)
    if filePath.find('/shared/') != -1:
        return
    if filePath.endswith('.final.ll'):
    	counter = 0
        content = ''
        flawLineList = []
        focusandfuncList = []
        with open(filePath,'r') as f:
            for line in f.readlines():
        	counter += 1
        	line = line.encode('utf-8')
        	if line.endswith(' #_%$$FLAW_TAG$$%_#\n'):
        	    flawLineList.append(counter)
        	    line = line[:-20] + '\n'
                if line.endswith(' #_%$$KEY_FUNC$$%_#\n'):
                    focusandfuncList.append(counter)
                    line = line[:-20] + '\n'
                if line.endswith(' #_%$$FOCUS_TAG$$%_#\n'):
                    focusandfuncList.append(counter)
                    line = line[:-21] + '\n'
        	content += line
        with open(filePath,'w+') as f:
        	f.write(content)
        slice2FlawDict[filePath] = flawLineList
        focusandfuncofslice[filePath] = focusandfuncList




def autoDetectorCodeFile(curPath):
    if not os.path.isdir(curPath):
        return
    dirList = os.listdir(curPath)
    for selectedDir in dirList:
        if os.path.isdir(os.path.join(curPath, selectedDir)):
            autoDetectorCodeFile(os.path.join(curPath, selectedDir))
        else:
            getFlawLine(curPath, selectedDir)


if __name__ == '__main__':

    parser = OptionParser()
    (options, args) = parser.parse_args()
    if len(args) > 1:
        print 'Usage error, you need to declare original path.\n'
    elif len(args) == 1:
        rawPath = args[0]
        autoDetectorCodeFile(rawPath)
    slice2FlawDict.pop('test')

    output = open('slice2flawline_NO.pkl', 'wb')
    pickle.dump(slice2FlawDict, output)
    output.close()

    output = open('funcandfocusLoc.pkl','wb')
    pickle.dump(focusandfuncofslice,output)
    output.close()
