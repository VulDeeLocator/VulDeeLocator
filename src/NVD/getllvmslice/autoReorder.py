# -*- coding:utf-8 -*-
from optparse import OptionParser
import os
import re


def reorder(targetPath, fileName, flag):
    if not os.path.exists(targetPath):
        return
    flawLineDict = {} #key:xxx_new.ll value:漏洞行号
    focusLineDict = {} #key:xxx_new.ll value:关注点行号
    dirList = os.listdir(targetPath) #point等目录下的文件
    flagZero = 0
    linenum = 0
    for targetfile in dirList:  #四类关注点下的文件
    	flagZero = 0
        if not targetfile.endswith('].ll') or targetfile.endswith('[9999].ll'):
            continue
        if targetfile.endswith('_[0].ll'):
            flagZero = 1
        if flagZero == 0:
            targetflag = re.findall('_\[(\d+)_(\d+)\].ll', targetfile) #保存行号和连续行数
            sliceName = re.sub('_\[\d+_\d+\].ll', '.new.ll', targetfile) #[xxx_yy].ll变为new.ll
            linenum = re.findall('_(\d+):',targetfile)[0];
        else:
            sliceName = targetfile[:-7] + '.new.ll' #[0].ll变为new.ll
            linenum = re.findall('_(\d+):',targetfile)[0];
        focusLineDict[sliceName] = linenum
        os.system('cp -f \"' + os.path.join(targetPath, targetfile) + '\" \"' + os.path.join(targetPath, sliceName)+ '\"') 
        if flagZero == 0 and sliceName in flawLineDict:
            for i in range(int(targetflag[0][1])): #添加漏洞行
                flawLineDict[sliceName].append(int(targetflag[0][0]) + i)
        elif flagZero == 0:
            flawLineDict[sliceName] = []
            for i in range(int(targetflag[0][1])): #添加漏洞行
                flawLineDict[sliceName].append(int(targetflag[0][0]) + i)
        elif sliceName in flawLineDict:
            flawLineDict[sliceName].append(0)
        else:
            flawLineDict[sliceName] = [0]

    #将xxx.new.ll文件中的漏洞行加上标签保存在xxx.flawtag.ll中，并且去掉注释内容,并在关注点位置加上标签
    for slicefile in flawLineDict.keys():
        lineCounter = 0
        sliceStr = ''
        sourcelinedbg = []
        linenum = focusLineDict[slicefile]
        with open(os.path.join(targetPath,slicefile),'r') as f:
            for line in f:
                if(line.startswith('!')):
                    pattern = '(.*) = !DILocation\(line: '+str(linenum)
                    dbg = re.findall(pattern,line)
                    if(len(dbg)):
                        sourcelinedbg.append(dbg[0])

        with open(os.path.join(targetPath,slicefile),'r') as f:
            for line in f:
                lineCounter += 1
                noteFlag = re.findall('\A +; x',line)
                if noteFlag: #去掉注释
                    continue
                for dbgline in sourcelinedbg:
                   if line.endswith(dbgline+'\n'):
                       line = line.replace('\n','')
                       line += ' #_%$$FOCUS_TAG$$%_#\n' #在关注点位置加上标签
                if lineCounter in flawLineDict[slicefile]:
                    line = line.replace('\n','')
                    line += ' #_%$$FLAW_TAG$$%_#\n' #在漏洞行位置加上标签
                sliceStr += line

        if(len(slicefile[:-7] + '.flawtag.ll') > 250): #避免文件名长度过长
            return
        with open(os.path.join(targetPath,slicefile[:-7] + '.flawtag.ll'),'w') as f: #处理完之后保存在xxx.flawtag.ll
            f.write(sliceStr)

    dirList = os.listdir(targetPath)
    for targetfile in dirList:
    	if fileName == 'multiFinal':
    	    flagMulti = 0
    	elif targetfile.find(fileName) == -1: #fileName是c文件名
    		flagMulti = 1
    	else:
    		flagMulti = 0
        if not targetfile.endswith('.flawtag.ll') or flagMulti == 1:
            continue
        if flag == 0: #c文件 flawtag.ll
            cmd = 'python2 reorderSlice.py ' + fileName + '.c "' + os.path.join(targetPath, targetfile) + '"'
            os.system(cmd)
        else:
            cmd = 'python2 reorderSlice.py ' + fileName + '.cpp "' + os.path.join(targetPath, targetfile) + '"'
            os.system(cmd)


def codeCompile(curpath, fileName):
    filePath = os.path.join(curpath, fileName)
    if filePath.find('/testcases/shared/') != -1:
        return
    flag = 0
    if filePath.find('/api/') == -1 and filePath.find('/arr/') == -1 and filePath.find(
            '/point/') == -1 and filePath.find('/bds/') == -1:
        flag = 1 #找bc文件
    if filePath.endswith('.bc') and fileName != 'multiFinal.bc' and flag == 1:
        cmd = 'opt -dot-callgraph "' + filePath + '"'
        os.system(cmd)
        print(cmd)
        if os.path.isfile(os.path.join(curpath, fileName[:-3] + '.c')):#c文件
            flag = 0
        else:
            flag = 1
        reorder(os.path.join(curpath, 'api'), fileName[:-3], flag);#第二个参数为c文件名 flag为0
        reorder(os.path.join(curpath, 'arr'), fileName[:-3], flag);
        reorder(os.path.join(curpath, 'point'), fileName[:-3], flag);
        reorder(os.path.join(curpath, 'bds'), fileName[:-3], flag);
        cmd = 'mv callgraph.dot '+curpath+'/'+fileName[:-3]+'_callgraph.dot'
        os.system(cmd)
        print(cmd)


def autoDetectorCodeFile(curPath):
    if not os.path.isdir(curPath):
        print curPath
        return
    dirList = os.listdir(curPath)
    for selectedDir in dirList:
        if os.path.isdir(os.path.join(curPath, selectedDir)):
            if os.path.exists(os.path.join(os.path.join(curPath, selectedDir),'multiFinal.bc')):
                codeCompile(os.path.join(curPath, selectedDir),'multiFinal.bc')
            else:
                autoDetectorCodeFile(os.path.join(curPath, selectedDir))
        else:
            codeCompile(curPath, selectedDir)


if __name__ == '__main__':
    # 若需要输入路径，请输入绝对路径
    parser = OptionParser()
    (options, args) = parser.parse_args()
    if len(args) > 1:
        print 'Usage error, you need to declare original path.'
    elif len(args) == 1:
        rawPath = args[0] #切片存放位置（总目录）
        autoDetectorCodeFile(rawPath)
