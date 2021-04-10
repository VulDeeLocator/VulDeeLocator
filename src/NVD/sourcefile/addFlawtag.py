import sys
def addtag(sourcetxt):
    with open(sourcetxt) as f:
        for line in f:
            spl = line.split()
            cfile = spl[0]
            linenum = int(spl[1])
            countline = 0
            txt = ''
            with open(cfile,'r') as processfile:
                for item in processfile:
                    countline += 1
                    if countline == linenum and item.find('/*#MFLAWTAG*/')==-1:
                        item =  '/*#MFLAWTAG*/' + item
                    txt += item
            with open(cfile,'w') as wf:
                wf.write(txt)
            print(cfile)

if __name__ == '__main__':
    sourcetxt = sys.argv[1]
    addtag(sourcetxt)
