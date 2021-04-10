# -*- coding:utf-8 -*-

from optparse import OptionParser
import re
import os

def padding(x):
    s = str(x)
    while len(s) < 9:
        s = "0" + s
    return s[0:3] + '/' + s[3:6] + '/' + s[6:9] + '/'

def autoGetVulLine(rawPathHead,fileName):
    fileDict = {}
    flawFileDict = {}

    with open(fileName) as f:
        fileFlag = 0
        path = ''
        print fileName
        testID = 0
        flawLineList = set([])
        for line in f.readlines():
            testIDList = re.findall(' *<testcase id=\"(\d+)\" ',line)
            if testIDList:
                testID = int(testIDList[0])
                fileDict[testID] = []
            testIDList = re.findall('\A *</testcase>',line)
            if testIDList:
                testID = 0
            filePath = re.findall('<file path=\"(.+)\" language=\"',line)
            if not filePath:
                fileEndfileFlag = re.findall('</file>',line)
                flawLine = re.findall('<flaw line=\"(\d+)\" name=\"',line)
                mixLine = re.findall('<mixed line=\"(\d+)\" name=\"',line)
                if fileFlag == 1 and flawLine:
                    flawLineList.add(flawLine[0])
                elif fileFlag == 1 and mixLine:
                    flawLineList.add(mixLine[0])
                if fileFlag == 1 and fileEndfileFlag:
                    fileFlag = 0
                    if '0' in flawLineList:
                        flawLineList.remove('0')
                    if not flawLineList and testID != 0:
                        fileDict[testID].append(path)
                    elif testID != 0:
                        flawFileDict[testID] = path
                    path = ''
                    flawLineList.clear()
                continue
            elif not line.endswith('/>\n'):
                path = filePath[0]
                fileFlag = 1
            elif testID != 0:
                fileDict[testID].append(filePath[0])
                path = ''


    for key in flawFileDict.keys():
        cmd = ''
        if flawFileDict[key].find('shared/') != -1:
            continue
        if flawFileDict[key].find(padding(key) + os.path.split(flawFileDict[key])[1]) == -1:
            continue
        if not os.path.exists(os.path.join(rawPathHead,flawFileDict[key])):
            print os.path.join(rawPathHead,flawFileDict[key])
            continue
        if flawFileDict[key].endswith('.c'):
            cmd = 'clang -emit-llvm -w -c -g ' + os.path.join(rawPathHead,flawFileDict[key]) + ' -o ' + os.path.join(rawPathHead,flawFileDict[key])[:-2] + '.bc'
            cmd += ' -I /home/king/aproSARD/testcaseLib/'           
        elif flawFileDict[key].endswith('.cpp'):
            cmd = 'clang++ -emit-llvm -w -c -g ' + os.path.join(rawPathHead,flawFileDict[key]) + ' -o ' + os.path.join(rawPathHead,flawFileDict[key])[:-4] + '.bc'
            cmd += ' -I /home/king/aproSARD/testcaseLib/'
        print cmd
        os.system(cmd)
    for key in fileDict.keys():
        if key in flawFileDict.keys() and flawFileDict[key].find('shared/') != -1:
            continue
        cmd = 'llvm-link'
        cmd1 = ''
        fileNotExistFlag = 0
        counterNoFlawFile = 0
        for noFlawFile in fileDict[key]:
            if not os.path.exists(os.path.join(rawPathHead,noFlawFile)) or noFlawFile.find(padding(key) + os.path.split(noFlawFile)[1]) == -1:
                continue
            if noFlawFile.endswith('.c'):
                cmd1 = 'clang -emit-llvm -w -g -c ' + os.path.join(rawPathHead,noFlawFile) + ' -o ' + os.path.join(rawPathHead,noFlawFile)[:-2] + '.bc'
                cmd1 += ' -I /home/king/aproSARD/testcaseLib/' 
            elif noFlawFile.endswith('.cpp'):
                cmd1 = 'clang++ -emit-llvm -w -g -c ' + os.path.join(rawPathHead,noFlawFile) + ' -o ' + os.path.join(rawPathHead,noFlawFile)[:-4] + '.bc'
                cmd1 += ' -I /home/king/aproSARD/testcaseLib/'
            if noFlawFile.find('.c') != -1 and os.path.exists(os.path.join(rawPathHead,noFlawFile)):
                counterNoFlawFile += 1
                os.system(cmd1)
            elif not os.path.exists(os.path.join(rawPathHead,noFlawFile)):
                fileNotExistFlag = 1
                print key
                break
            if noFlawFile.endswith('.c') and noFlawFile.find(padding(key) + os.path.split(noFlawFile)[1]) != -1:
                cmd += ' ' + os.path.join(rawPathHead,noFlawFile)[:-2] + '.bc'
            elif noFlawFile.endswith('.cpp') and noFlawFile.find(padding(key) + os.path.split(noFlawFile)[1]) != -1:
                cmd += ' ' + os.path.join(rawPathHead,noFlawFile)[:-4] + '.bc'
        if cmd == 'llvm-link' or fileNotExistFlag:
            continue
        if key in flawFileDict.keys():
            if flawFileDict[key].endswith('.c'):
                cmd += ' ' + os.path.join(rawPathHead,flawFileDict[key])[:-2] + '.bc'
                print cmd + ' -o ' + os.path.join(rawPathHead,flawFileDict[key])[:-2] + '.bc'
                result = os.system(cmd + ' -o ' + os.path.join(rawPathHead,flawFileDict[key])[:-2] + '.bc')
            elif flawFileDict[key].endswith('.cpp'):
                cmd += ' ' + os.path.join(rawPathHead,flawFileDict[key])[:-4] + '.bc'
                result = os.system(cmd + ' -o ' + os.path.join(rawPathHead,flawFileDict[key])[:-4] + '.bc')
            
        
        if key not in flawFileDict.keys() or not fileDict[key]:
            continue
        if flawFileDict[key].endswith('.c'):
            result = os.system(cmd + ' "' + os.path.join(rawPathHead,flawFileDict[key])[:-2] + '.bc\" -o \"' + os.path.join(rawPathHead,os.path.join(os.path.split(flawFileDict[key])[0],'multiFinal.bc')) +'"')

        elif flawFileDict[key].endswith('.cpp'):
            result = os.system(cmd + ' "' + os.path.join(rawPathHead,flawFileDict[key])[:-4] + '.bc" -o "' + os.path.join(rawPathHead,os.path.join(os.path.split(flawFileDict[key])[0],'multiFinal.bc')) + '"')




if __name__ == '__main__':

    parser = OptionParser()
    (options, args) = parser.parse_args()
    if len(args) != 2:
        print 'Usage error.\n'
    else:
        autoGetVulLine(args[0],args[1])
