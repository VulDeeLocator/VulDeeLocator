## coding: utf-8
'''
This python file is used to precess the vulnerability slices, including read the pkl file and split codes into corpus.
Run main function and you can get a corpus pkl file which map the same name slice file.
'''
from __future__ import print_function
from get_tokens import *
import os  
import stat
import pickle  

testcases = []

f = open("record/synthetic and academic datasets/testcases_train.pkl",'rb')  #get the testcase ids of train sets and test sets
testcases += pickle.load(f)  
f.close()

f = open("record/synthetic and academic datasets/testcases_test.pkl",'rb')
testcases += pickle.load(f)
f.close()

def get_sentences(slicepath, labelpath, corpuspath):
    """split sentences into corpus
    
    This function is used to split the slice file and split codes into words

    # Arguments
        slicepath: String type, the src of slice files
        labelpath: String type, the src of label files 
        corpuspath: String type, the src to save corpus 

    # Return
        [slices[], linenum[], vlinenum[]] 
    """

    for folder in os.listdir(slicepath):  
        filepath = os.path.join(labelpath, folder+"_Flawline.pkl")			
        f = open(filepath, 'rb')
        labellists = pickle.load(f)  
        f.close()
        
        temp_labellists = {}
        for key in labellists.keys():
            temp_labellists["/".join(key.split("/")[-5:])] = labellists[key]
        labellists = temp_labellists

        for testcase_1 in os.listdir(os.path.join(slicepath, folder)):
            for testcase_2 in os.listdir(os.path.join(slicepath, folder, testcase_1)):
                for testcase_3 in os.listdir(os.path.join(slicepath, folder, testcase_1, testcase_2)):
                    if not os.path.isdir(os.path.join(slicepath, folder, testcase_1, testcase_2, testcase_3)):
                        continue
                    if not testcase_1+testcase_2+testcase_3 in testcases:
                        continue
                    for fourfocus in os.listdir(os.path.join(slicepath, folder, testcase_1, testcase_2, testcase_3)):
                        if os.path.isdir(os.path.join(slicepath, folder, testcase_1, testcase_2, testcase_3, fourfocus)):
                            for filename in os.listdir(os.path.join(slicepath, folder, testcase_1, testcase_2, testcase_3, fourfocus)):
                                if filename.endswith(".final.ll"):
                                    print("\r"+testcase_1+testcase_2+testcase_3,end='')

                                    filepath = os.path.join(slicepath, folder, testcase_1, testcase_2, testcase_3, fourfocus, filename)
                                    if os.path.getsize(filepath) > 1:
						
                                        f = open(filepath, 'r')
                                        sentences = f.read().split("\n")
                                        f.close()
										
                                        if "/".join([testcase_1, testcase_2, testcase_3, fourfocus, filename]) in labellists:
                                            vlinenumlists = labellists["/".join([testcase_1, testcase_2, testcase_3, fourfocus, filename])]
                                        else:
                                            continue
                                    
                                        slice_corpus = []
                                        slice_linenum = []
                                        slice_vlinenum = []
                                        slice_func = []
                                        token_index = 0
                                        linenum_index = 0
                                        funcs = []
                                        variables = []
                                        
                                        if sentences[0] == '\r' or sentences[0] == '':
                                            del sentences[0]
                                        if sentences == []:
                                            continue
                                        if sentences[-1] == '' or sentences[-1] == '\r':
                                            del sentences[-1]

                                        for sentence in sentences:
                                            
                                            list_tokens = create_tokens(sentence.strip()) 
                                        
                                            for t_index in range(1,len(list_tokens)):
                                                if list_tokens[t_index].startswith("@"):
                                                    
                                                    if (list_tokens[0] == "call" and "define" in sentences[sentences.index(sentence)+1]) or (list_tokens[0] == "define" and "call" in sentences[sentences.index(sentence)-1]):
                                                        
                                                        if "good" in list_tokens[t_index] or "bad" in list_tokens[t_index]:
                                                            slice_func.append(str(list_tokens[t_index]))
                                                        
                                                        if list_tokens[t_index] in funcs:
                                                            list_tokens[t_index] = "func_"+str(funcs.index(list_tokens[t_index]))
                                                        else:
                                                            funcs.append(list_tokens[t_index])
                                                            list_tokens[t_index] = "func_"+str(len(funcs)-1)
                                                    elif list_tokens[0] == "define" or list_tokens[0] == "store":
                                                        if "good" in list_tokens[t_index] or "bad" in list_tokens[t_index]:
                                                            slice_func.append(str(list_tokens[t_index]))
                                                        if list_tokens[t_index] in funcs:
                                                            list_tokens[t_index] = "func_"+str(funcs.index(list_tokens[t_index]))
                                                        else:
                                                            funcs.append(list_tokens[t_index])
                                                            list_tokens[t_index] = "func_"+str(len(funcs)-1)
                                                    elif not "llvm" in list_tokens[t_index] and ("load" in list_tokens[:t_index] or "call" in list_tokens[:t_index]):
                                                        if list_tokens[t_index] in variables:
                                                            list_tokens[t_index] = "variable_"+str(variables.index(list_tokens[t_index]))
                                                        else:
                                                            variables.append(list_tokens[t_index])
                                                            list_tokens[t_index] = "variable_"+str(len(variables)-1)
                                        
                                            slice_corpus = slice_corpus + list_tokens
                
                                            linenum_index += 1
                                            slice_linenum.append(token_index)  
                                            if linenum_index in vlinenumlists:
                                                slice_vlinenum.append(token_index)

                                            token_index = token_index + len(list_tokens)
                                    
                                        slice_func = list(set(slice_func))
                                        if slice_func == []:
                                            slice_func = ['main']

                                        folder_path = os.path.join(corpuspath, (testcase_1+testcase_2+testcase_3))
                                        savefilepath = os.path.join(folder_path, fourfocus+'_'+filename[:-3]+'.pkl')
                                        if testcase_1+testcase_2+testcase_3 not in os.listdir(corpuspath):
                                            os.mkdir(folder_path)
                                            os.chmod(folder_path, stat.S_IRWXO)
                                        f = open(savefilepath, 'wb') 
                                        pickle.dump([slice_corpus ,slice_linenum, slice_vlinenum, slice_func], f)
                                        f.close()
                                    else:
                                        print('\n',filename)

if __name__ == '__main__':
    
    SLICEPATH = './data/SARD/data_source/'  #path of slices generated by synthetic and academic datasets
    LABELPATH = './data/SARD/label_source/'   #path of labels 
    CORPUSPATH = './data/SARD/corpus/'      #path of corpus                                                                                                                                                                                                                                                          

    get_sentences(SLICEPATH, LABELPATH, CORPUSPATH)

    print('\nsuccess!')
