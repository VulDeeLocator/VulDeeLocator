#encoding: utf-8
import os
import xlrd
import pickle
import sys
import re

def copy_diff(appname,cveid,path):
    cvedir = diff_root+appname+'/'+cveid
    diff = diff_root+'diff/'+cveid+'.txt'
    cfile = source_root+appname+'/'+path
    if not os.path.exists(cfile):
        return
    if not os.path.exists(cvedir):
        os.makedirs(cvedir)
    os.system('cp '+cfile+' '+cvedir)
    os.system('cp '+diff+' '+cvedir)

def getfunc(excelfilename,sheet_index=0):
    app_list=[]
    hole_path=[]
    mdict = {}
    cvedict = {}
    cveverdict = {}
    workbook = xlrd.open_workbook(excelfilename)
    sheet = workbook.sheet_by_index(sheet_index)
    nrows = sheet.nrows
    ncols = sheet.ncols
    f = open("./holefunct.txt","w");
    for line in range(1,nrows):
        func = []
        app_version = sheet.cell(line,4).value
        path = sheet.cell(line,2).value
        mfunc = sheet.cell(line,3).value
        cveid = sheet.cell(line,0).value.replace(' ','')
        path.replace(' ','')
        if cveid not in cvedict.keys():
            cvedict[cveid] = []
        if cveid not in cveverdict.keys():
            cveverdict[cveid] = []
        cveverdict[cveid].append(app_version)
        copy_diff(app_version,cveid,path)
        if app_version not in app_list:
            app_list.append(app_version)
        func = mfunc.split(',')
        for fun in func:
            hole_path.append(source_root+app_version+'/'+path+'/'+fun)
            cvedict[cveid].append(source_root+app_version+'/'+path+'/'+fun)
            cpath = path[path.rfind('/')+1:]
            f.write(cveid+" "+app_version+" "+cpath+" "+fun+"\n")
    f.close()
    for key in app_list:
        mdict[key] = []
    for term in hole_path:
        for key in app_list:
            index = term.find(key)
            if index != -1 and term[index+len(key)] == '/':
                mdict[key].append(term)
    names=[]
    return hole_path,app_list,mdict,cvedict,cveverdict

def get_fileline_dict(appname):
    appname_diff_root = diff_root+appname
    processdiff(appname_diff_root)
    return

def processdiff(curent_path):
    files = os.listdir(curent_path)
    for file in files:
        fi_d = os.path.join(curent_path,file)            
        if os.path.isdir(fi_d):
          processdiff(fi_d)                  
        else:
            if fi_d.find('.c') != -1 :
                getline(fi_d)

def getline(cfile):
    if os.path.exists(cfile):
        cvepart = re.findall('.+(CVE-\d+-\d+)',cfile)
        if not cvepart:
            return
        cvefile = os.path.split(cfile)[0] + '/' + cvepart[0] + '.txt'
        finalflawline = []

        flawlineinslicer=[]
        flawlinenum = 0
        countslicernum = 0
        cveslicertag = []
        with open(cvefile) as cvef:
            cvelinenum = 0
            for line in cvef:
                nospacecline = line.replace(' ','').replace('\n','').replace('\r','').replace('\t','')
                if nospacecline.startswith('--') and not nospacecline.startswith('---'):
                    break
                if not nospacecline.startswith('+'):
                    cvelinenum += 1
                if nospacecline.startswith('@@'):
                    cveslicertag.append(cvelinenum)
            cveslicertag.append(cvelinenum)
        tagnum = len(cveslicertag)
        #finallinelist[tmplinelist[codeline]]
        finallinelist = []
        #finallinenumlist[linenum[linenum]]
        finallinenumlist = []
        
        for mj in range(0,tagnum-1):
            with open(cvefile) as f:
                tmplinelist = []
                tmplinenumlist = []
                tmplinenum = 0
                for line in f:
                    tmpline = line.replace(' ','').replace('\n','').replace('\r','').replace('\t','')
                    if not tmpline.startswith('+'):
                        tmplinenum += 1
                    if not tmpline.startswith('+') and tmplinenum > cveslicertag[mj]+1 and tmplinenum < cveslicertag[mj+1]:
                        if tmpline.startswith('-'):
                            if len(tmpline) > 1:
                                tmplinenumlist.append(tmplinenum-cveslicertag[mj]-1)
                            tmplinelist.append(tmpline[1:])
                        else:
                            tmplinelist.append(tmpline)
                if len(tmplinenumlist) == 0:
                    tmplinenumlist.append(-1)
                finallinelist.append(tmplinelist)
                finallinenumlist.append(tmplinenumlist)
        
        slicernumlen = len(finallinelist)
        matchline = []
        for mk in range(0,slicernumlen):
            tmplist = finallinelist[mk][0]
            tmpmatchline = []
            with open(cfile) as cf:
                linecount = 0
                for cline in cf:
                    linecount += 1
                    nospacecfile =cline.replace(' ','').replace('\n','').replace('\r','').replace('\t','')
                    if nospacecfile==tmplist:
                        tmpmatchline.append(linecount)
            matchline.append(tmpmatchline)
        flawlinelist = []
        for outi in range(0,slicernumlen):
            tmplinelist = finallinelist[outi]
            tmplinenumlist = finallinenumlist[outi]
            tmpmatchlist = matchline[outi]
            if tmplinenumlist[0] == -1:
                continue
            
            for inneri in range(0,len(tmpmatchlist)):
                startline = tmpmatchlist[inneri]
                linenum = 0
                switchtag = 0
                inslicerline = 0
                lasttag = 1
                with open(cfile) as incfile:
                    for inline in incfile:
                        linenum += 1
                        if linenum == startline:
                            switchtag = 1
                        if inslicerline == len(tmplinelist):
                                lasttag = 0
                                break
                        if switchtag == 1:
                            tmpnospaceline = inline.replace(' ','').replace('\n','').replace('\r','').replace('\t','')
                            if not tmpnospaceline==tmplinelist[inslicerline] and tmplinelist[inslicerline] != '':
                                lasttag = 0
                            inslicerline += 1
                        if inslicerline == len(tmplinelist) and lasttag == 1:
                            for infl in range(0,len(tmplinenumlist)):
                                flawlinelist.append(startline+tmplinenumlist[infl]-1)
            scfile = cfile[cfile.rfind('/')+1:]
            if not flawlinelist:
                flawlinelist.append(0)
            if scfile not in lineinfo_dict.keys():
                lineinfo_dict[scfile] = []
            for item in flawlinelist:
                lineinfo_dict[scfile].append(item)
            lineinfo_dict[scfile] = list(set(lineinfo_dict[scfile]))
    return

def delhead(deldir):
    files = os.listdir(deldir)
    for item in files:
        if item.endswith('.h'):
            rmf = os.path.join(deldir,item)
            os.system('rm '+rmf)             

def finalcompile(cveid,appname,lineinfo_dict,sourcefilelist):
    basedir = os.path.join(source_root,appname)
    # compile command of the software
    compilehead = 'clang-6.0 -c -MMD -emit-llvm -g -I '+basedir+' -I '+basedir+'/libavcodec '+\
    ' -I '+basedir+'/libavformat '+' -I '+basedir+'/libavfilter '+\
    ' -I '+basedir+'/libswscale '+' -I'+basedir+'/libswresample '+' -I '+basedir+'/libavutil '+'-include '+basedir+'/libavutil/internal.h\
	-I /usr/include/glib-2.0/  $(pkg-config --cflags glib-2.0) '
    for item in sourcefilelist:
        filename = os.path.split(item)[1]
        print('\nfilename\n')
        print(filename)
        print(os.path.split(item))
        print('\ntemplist:\n')
        tmplist = []
        if filename in  lineinfo_dict.keys():
            tmplist = lineinfo_dict[filename]
        else:
            tmplist.append(0)
        print(tmplist)
        subfilename = filename.split('.')[0]
        ndst = os.path.join(os.path.join(os.path.join(slicer_root,cveid),appname),subfilename)
        if not os.path.exists(ndst):
            os.makedirs(ndst)
        cpcmd = 'cp '+ item +' '+ndst
        os.system(cpcmd)
        ndstfile = os.path.join(ndst,filename)
        dstbc = ndstfile.replace('.c','.bc')
        comcmd = compilehead + ndstfile + ' -o '+ dstbc
        os.system(comcmd)
        os.system(compilehead+ndstfile)
        c_of_d = filename.replace('.c','.d')
        with open(c_of_d,"r") as file_of_d:
            temp = file_of_d.readline()
            for cheads in file_of_d.readlines():
                chead = cheads.replace('\\','')
                chead = chead.replace(' ','')
                chead = chead.replace('\r','')
                chead = chead.replace('\n','')
                if chead.endswith('.h'):
                    os.system('cp '+chead+' '+ndst)            
        with open('tmp.txt','w') as f:
            for linenum in tmplist:
                slicerinfo = ndstfile+' '+str(linenum)+' \n'
                f.write(slicerinfo)
                hole_line.write(slicerinfo)
                print(slicerinfo)
        slicercmd = './get-llvmwithline tmp.txt'
        print(slicercmd)
        os.system(slicercmd)
        delhead(ndst)
        os.system('rm *.bc *.sliced *.d')



if __name__ == '__main__':
    source_root='/home/king/aproffmpeg/source/'
    diff_root='/home/king/aproffmpeg/diff/'
    slicer_root = '/home/king/aproffmpeg/newslicerffmpeg/'

    excel_file = sys.argv[1]

    flawfunc,app_versionname,outdict,cvedict,cveverdict = getfunc(excel_file)
    hole_line = open("./hole_line.txt","w")
    for key in cvedict.keys():
        print(key)
        print(cvedict[key])
        print(cveverdict[key])
        for ver in cveverdict[key]:
            if os.path.exists(source_root+ver):# and ver == "ffmpeg-0.6":
                print('in\n')
                lineinfo_dict ={}
                get_fileline_dict(ver)
                print('\nlineinfo_dict\n')
                print(lineinfo_dict)
                print('\nnullset\n')
                nullset = set()
                for item in outdict[ver]:
                    if item in cvedict[key]:
                        nullset.add(os.path.split(item)[0])
                        print(os.path.split(item))
                print(nullset)
                print('\n')
                finalcompile(key,ver,lineinfo_dict,nullset)
    hole_line.close()
