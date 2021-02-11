## coding: utf-8
'''
This python file is used to split database into 80% train set and 20% test set, tranfer the original code into vector, creating input file of deap learning model.
'''
from __future__ import print_function
from gensim.models.word2vec import Word2Vec
import numpy as np
import pickle
import os
import gc

VECTOR_DIM = 30  
MAXLEN = 900   

def generate_corpus(model, sample):
    """generate corpus
    
    This function is used to create input of deep learning model
    # Arguments
        #w2vModelPath: String, the path of word2vec or doc2vec model     
        model : word2vec model
        samples: List, the samples                               
   
    # Return
        dl_corpus: the vectors of corpus                            
    """
    
    dl_corpus = []
    for word in sample:
        if word in model:
            dl_corpus.append(model[word])
        else:
            dl_corpus.append([0]*VECTOR_DIM)

    return [dl_corpus]

def get_dldata(filepath, dlTrainCorpusPath, dlTestCorpusPath, seed=2018, batch_size=16):
    """create deeplearning model dataset
    
    This function is used to create train dataset and test dataset

    # Arguments
        filepath: String, path of all vectors          
        dlTrainCorpusPath: String, path of train set    
        dlTestCorpusPath: String, path of test set     
        seed: seed of random                           
        batch_size: the size of mini-batch             
    
    """
	f = open("record/synthetic and academic datasets/testcases_train.pkl",'rb')  #get the testcase ids of train sets and test sets
	testcases += pickle.load(f)  
	f.close()

	f = open("record/synthetic and academic datasets/testcases_test.pkl",'rb')
	testcases += pickle.load(f)
	f.close()
	
    print("produce train dataset...")  
    N = 6
    num = list(range(N))
    for i in num:
        train_set = [[], [], [], [], [], []]
        for folder_train in folders_train[int(i*len(folders_train)/N) : int((i+1)*len(folders_train)/N)]:
            if not folder_train in os.listdir(filepath):
                continue
            print("\r"+str(folder_train), end='')
            for filename in os.listdir(os.path.join(filepath, folder_train)):
                f = open(filepath + folder_train + '/' + filename, 'rb')
                data = pickle.load(f)
                f.close()
                if len(data[0][0]) > MAXLEN:
                    data[2] = [x for x in data[2] if x <= MAXLEN]
                data[0] = cutdata(data[0][0])
                if data[0] == None:
                    continue        
                for n in range(len(data)):
                    train_set[n].append(data[n])
                train_set[-1].append(folder_train+"/"+filename)
        f_train = open(dlTrainCorpusPath + "train_" + str(i)+ "_0818.pkl", 'wb')
        pickle.dump(train_set, f_train)
        f_train.close()

        del train_set 
        gc.collect() 

    print("\nproduce test dataset...")
    N = 6
    num = list(range(N))
    for i in num:
        test_set = [[], [], [], [], [], []]
        for folder_test in folders_test[int(i*len(folders_test)/N) : int((i+1)*len(folders_test)/N)]:
            if not folder_test in os.listdir(filepath):
                continue
            print("\r"+str(folder_test), end='')
            for filename in os.listdir(os.path.join(filepath, folder_test)):
                f = open(filepath + folder_test + '/' + filename, 'rb')
                data = pickle.load(f)
                f.close()
                if len(data[0][0]) > MAXLEN:
                    data[2] = [x for x in data[2] if x <= MAXLEN]
                data[0] = cutdata(data[0][0])
                if data[0] == None:
                    continue        
                for n in range(len(data)):
                    test_set[n].append(data[n])
                test_set[-1].append(folder_test+"/"+filename)
            
        f_test = open(dlTestCorpusPath + "test_" + str(i)+ "_0124.pkl", 'wb')
        pickle.dump(test_set, f_test)
        f_test.close()

        del test_set
        gc.collect()
    return
    
def cutdata(data, maxlen=MAXLEN, vector_dim=VECTOR_DIM):
    """cut data to maxlen
    
    This function is used to cut the slice or fill slice to maxlen

    # Arguments
        data: The slice
        maxlen: The max length to limit the slice
        vector_dim: the dim of vector
    
    """
    if maxlen:
        fill_0 = [0]*vector_dim
        if len(data) > 900:
            pass
        if len(data) <=  maxlen:
            data = data + [fill_0] * (maxlen - len(data))
        else:
            data = data[:maxlen]
    return data

if __name__ == "__main__":
    
    CORPUSPATH = "./data/NVD/corpus/"
    VECTORPATH = "./data/vector/"
    W2VPATH = "w2v_model/wordmodel_min_iter5.model"
    
    print("turn the corpus into vectors...")
    model = Word2Vec.load(W2VPATH)
    for testcase in os.listdir(CORPUSPATH):
        print("\r" + testcase, end='')
        if testcase not in os.listdir(VECTORPATH):  
            folder_path = os.path.join(VECTORPATH, testcase)
            os.mkdir(folder_path)
        for corpusfile in os.listdir(CORPUSPATH + testcase):
            corpus_path = os.path.join(CORPUSPATH, testcase, corpusfile)
            f_corpus = open(corpus_path, 'rb')
            data = pickle.load(f_corpus)
            f_corpus.close()
            data.append(data[0])
            data[0] = generate_corpus(model, data[0])
            vector_path = os.path.join(VECTORPATH, testcase, corpusfile)
            f_vector = open(vector_path, 'wb')
            pickle.dump(data, f_vector)
            f_vector.close()
    print("\nw2v over...")
    
    print("spliting the train set and test set...")
    dlTrainCorpusPath = "data/dl_input/train/"
    dlTestCorpusPath = "data/dl_input/test/"
    get_dldata(VECTORPATH, dlTrainCorpusPath, dlTestCorpusPath)
    
    print("\nsuccess!")
