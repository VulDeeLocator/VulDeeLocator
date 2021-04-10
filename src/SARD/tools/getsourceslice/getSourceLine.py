#coding:utf-8
import sys
import os
import re
import pickle

def getSourceSlicer(finalf,linelist):
    slicerfile = finalf.replace('.final.ll','.slicer.c')
    tmpdir = finalf[0:finalf.rfind('/')]
    lastdir = tmpdir[0:tmpdir.rfind('/')]
    files = os.listdir(lastdir)
    sourcefile = ''
    for mfile in files:
        if mfile.endswith('.c')  and finalf.find(mfile[:-2]) != -1:
            sourcefile = lastdir+'/'+mfile
    linecount = 0
    linedict = {}
    mdictpkl[slicerfile] = []
    funcandfocus[slicerfile] = []
    funcandfocus[slicerfile].append(0)
    funcnamelist = re.findall('#(.+)#',finalf)
    linenumlist = re.findall('_(\d+):',finalf)
    funcname = ''
    if(len(funcnamelist)):
        funcname = funcnamelist[0]
    linenum = 0
    if(len(linenumlist)):
        linenum = (int)(linenumlist[0])
    with open(sourcefile) as rf:
        for line in rf:
            linecount += 1
            if linecount in linelist:
                linedict[linecount] = line
    linec2 = 0
    with open(slicerfile,'w') as sf:
        for item in linelist:
            linec2 += 1
            if item == '{' or item == '}':
                sf.write(item+'\n')
            else:
                if item in linedict.keys():
                    linetow = linedict[item]
                    if linetow.find('/*#MFLAWTAG*/') != -1:
                        mdictpkl[slicerfile].append(linec2)
                    if linetow.find(funcname) != -1:
                        funcandfocus[slicerfile][0] = linec2
                    if item == linenum:
                        funcandfocus[slicerfile].append(linec2)
                    sf.write(linetow.replace('/*#MFLAWTAG*/',''))
    if(len(funcandfocus[slicerfile]) == 1):
        funcandfocus[slicerfile].append(funcandfocus[slicerfile][0]+1)

def processdbg(finalfile):
    mlist = []
    regex1 = re.compile('.+!dbg !(\d+)')
    with open(finalfile,'r') as dbgf:
        for line in dbgf:
            num = regex1.findall(line)
            if len(num) > 0:
                mlist.append(num[0])
            if line.find('{') != -1:
                mlist.append('{')
            if line.find('}') != -1:
                mlist.append('}')
    debugfile = finalfile.replace('.final.ll','.new.ll') 
    if not os.path.exists(debugfile):
        return
    comparedict = {}
    regex2 = re.compile('^!(\d+).+line:.(\d+),')
    with open(debugfile,'r') as debugf:
        for line in debugf:
            numdict = regex2.findall(line)
            if len(numdict) < 1:
                continue
            comparedict[numdict[0][0]] = numdict[0][1]
    linelist = []
    sourcefunclist = []
    for item in mlist:
        if item == '{' or item == '}':
            linelist.append(item)
        elif item in comparedict.keys():
            tmpline = int(comparedict[item])
            if linelist and tmpline in linelist:
                continue
            linelist.append(tmpline)

    linenumpkl =  finalfile.replace('.final.ll','.souline.pkl')
    pickle.dump(linelist,open(linenumpkl,'w'))
    getSourceSlicer(finalfile,linelist)




def getfinal(mpath):
    sondirs = os.listdir(mpath)
    for mdir in sondirs:
        npath = os.path.join(mpath,mdir)
        if os.path.isdir(npath):
            getfinal(npath)
        else:
            if npath.endswith('.final.ll'):
                processdbg(npath)

if __name__ == '__main__':
    slicerpath = sys.argv[1]
    mdictpkl = {}
    funcandfocus = {}
    getfinal(slicerpath)
    pickle.dump(mdictpkl,open('sourcedict.pkl','w'))
    pickle.dump(funcandfocus,open('funcandfocusLoc.pkl','w'))
