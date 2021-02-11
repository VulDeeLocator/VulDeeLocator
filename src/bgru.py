## -*- coding: utf-8 -*-
'''
This python file is used to train four class focus data in blstm model
'''

from keras.preprocessing import sequence
from keras.optimizers import SGD, RMSprop, Adagrad, Adam, Adadelta
from keras.models import Sequential, load_model
from keras.layers.core import Masking, Dense, Dropout, Activation
from keras.layers.recurrent import LSTM,GRU
from preprocess_dl_Input_version4_rawbgru import *
from keras.layers.wrappers import Bidirectional
from collections import Counter
import tensorflow as tf
import numpy as np
import pickle
import random
import time
import math
import os

RANDOMSEED = 2018 
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

def build_model(maxlen, vector_dim, layers, dropout):
    print('Build model...')
    model = Sequential()
    
    model.add(Masking(mask_value=0.0, input_shape=(maxlen, vector_dim)))
    
    for i in range(1, layers):
        model.add(Bidirectional(GRU(units=256, activation='tanh', recurrent_activation='hard_sigmoid', return_sequences=True)))
        model.add(Dropout(dropout))
        
    model.add(Bidirectional(GRU(units=256, activation='tanh', recurrent_activation='hard_sigmoid')))
    model.add(Dropout(dropout))
    
    model.add(Dense(1, activation='sigmoid'))
          
    model.compile(loss='binary_crossentropy', optimizer='adamax', metrics=['TP_count', 'FP_count', 'FN_count', 'precision', 'recall', 'fbeta_score'])
    
    model.summary()
 
    return model


def main(traindataSet_path, testdataSet_path, realtestpath, weightpath, resultpath, batch_size, maxlen, vector_dim, layers, dropout):
    print("Loading data...")
    
    model = build_model(maxlen, vector_dim, layers, dropout)
    
    #model.load_weights(weightpath)
    dataset = []
    labels = []
    linetokens = []
    vpointers = []
    funcs = []
    print("Loading data...")

    for filename in os.listdir(traindataSet_path):
        if(filename.endswith(".pkl") is False):
            continue
        print(filename)
        f = open(os.path.join(traindataSet_path,filename),"rb")
        dataset_file, linetokens_file, vpointers_file, func_file, corpus_file, testcase_file = pickle.load(f,encoding = 'iso-8859-1')
        f.close()
        dataset += dataset_file
        linetokens += linetokens_file
        vpointers += vpointers_file
        funcs += func_file
    print(len(dataset))
    
    for vp in range(len(vpointers)):
        if vpointers[vp] != []:
            label = 1
            for func in funcs[vp]:
                if "good" in func:
                    label = 0
                    vpointers[vp] = []
                    break
        else:
            label = 0
        labels.append(label)
    
    train_generator = generator_of_data(dataset, labels, linetokens, vpointers, batch_size, maxlen, vector_dim)    
    all_train_samples = len(dataset)
    steps_epoch = int(all_train_samples / batch_size)
    print("start")
    t1 = time.time()
    model.fit_generator(train_generator, steps_per_epoch=steps_epoch, epochs=4)
    t2 = time.time()
    train_time = t2 - t1

    model.save_weights(weightpath)

    model.load_weights(weightpath)
    dataset = []
    linetokens = []
    vpointers = []
    funcs = []
    testcases = []
    print("Test...")
    for filename in os.listdir(testdataSet_path):
        if(filename.endswith(".pkl") is False):
            continue
        print(filename)
        f = open(os.path.join(testdataSet_path,filename),"rb")
        dataset_file, linetokens_file, vpointers_file, funcs_file, corpus_file, testcase_file = pickle.load(f,encoding = 'iso-8859-1')
        f.close()
        dataset += dataset_file
        linetokens += linetokens_file
        vpointers += vpointers_file
        funcs += funcs_file
        testcases +=testcase_file
    print(len(dataset),len(testcases))

    labels = []
    for vp in range(len(vpointers)):
        if vpointers[vp] != []:
            label = 1
            for func in funcs[vp]:
                if "good" in func:
                    label = 0
                    break
        else:
            label = 0
        labels.append(label)

    batch_size = 1
    test_generator = generator_of_data(dataset, labels,linetokens, vpointers, batch_size, maxlen, vector_dim)
    all_test_samples = len(dataset)
    steps_epoch = int(math.ceil(all_test_samples / batch_size))

    t1 = time.time()
    result = model.evaluate_generator(test_generator, steps=steps_epoch)
    t2 = time.time()
    test_time = t2 - t1

    score, TP, FP, FN, precision, recall, f_score= result[0]
    f = open("./BGRU/result_analyze/TP_index_blstm.pkl",'wb')
    pickle.dump(result[1], f)
    f.close()
    
    f_TP = open("./BGRU/result_analyze/TP_filenames.txt","a+")
    for i in range(len(result[1])):
        TP_index = result[1][i]
        f_TP.write(str(testcases[TP_index])+'\n')
		
    f_FP = open("./BGRU/result_analyze/FP_filenames.txt","a+")
    for j in range(len(result[2])):
        FP_index = result[2][j]
        f_FP.write(str(testcases[FP_index])+'\n')	
  
    f_FN = open("./BGRU/result_analyze/FN_filenames.txt","a+")
    for k in range(len(result[2])):
        FN_index = result[2][k]
        f_FN.write(str(testcases[FN_index])+'\n')

    TN = all_test_samples - TP - FP - FN
    fwrite = open(resultpath, 'a')
    fwrite.write('cdg_ddg: ' + ' ' + str(all_test_samples) + '\n')
    fwrite.write("TP:" + str(TP) + ' FP:' + str(FP) + ' FN:' + str(FN) + ' TN:' + str(TN) +'\n')
    FPR = float(FP) / (FP + TN)
    fwrite.write('FPR: ' + str(FPR) + '\n')
    FNR = float(FN) / (TP + FN)
    fwrite.write('FNR: ' + str(FNR) + '\n')
    Accuracy = float(TP + TN) / (all_test_samples)
    fwrite.write('Accuracy: ' + str(Accuracy) + '\n')
    precision = float(TP) / (TP + FP)
    fwrite.write('precision: ' + str(precision) + '\n')
    recall = float(TP) / (TP + FN)
    fwrite.write('recall: ' + str(recall) + '\n')
    f_score = (2 * precision * recall) / (precision + recall)
    fwrite.write('fbeta_score: ' + str(f_score) + '\n')
    fwrite.write('train_time:' + str(train_time) +'  ' + 'test_time:' + str(test_time) + '\n')
    fwrite.write('--------------------\n')
    fwrite.close()

    dict_testcase2func = {}
    for i in testcases:
        if not i in dict_testcase2func:
            dict_testcase2func[i] = {}
    TP_indexs = result[1]
    for i in TP_indexs:
        if funcs[i] == []:
            continue
        for func in funcs[i]:
            if func in dict_testcase2func[testcases[i]].keys():
                dict_testcase2func[testcases[i]][func].append("TP")
            else:
                dict_testcase2func[testcases[i]][func] = ["TP"]
    FP_indexs = result[1]
    for i in FP_indexs:
        if funcs[i] == []:
            continue
        for func in funcs[i]:
            if func in dict_testcase2func[testcases[i]].keys():
                dict_testcase2func[testcases[i]][func].append("FP")
            else:
                dict_testcase2func[testcases[i]][func] = ["FP"]
    f = open(resultpath+"_dict_testcase2func.pkl",'wb')
    pickle.dump(dict_testcase2func, f)
    f.close()

def testrealdata(realtestpath, weightpath, batch_size, maxlen, vector_dim, layers, dropout):
    model = build_model(maxlen, vector_dim, layers, dropout)
    model.load_weights(weightpath)
    
    print("Loading data...")
    for filename in os.listdir(realtestpath):
        print(filename)
        f = open(realtestpath+filename, "rb")
        realdata = pickle.load(f,encoding="latin1")
        f.close()
    
        labels = model.predict(x = realdata[0],batch_size = 1)
        for i in range(len(labels)):
            if labels[i][0] >= 0.5:
                print(realdata[1][i])


if __name__ == "__main__":
    batchSize = 64
    vectorDim = 30
    maxLen = 900
    layers = 2
    dropout = 0.2
    traindataSetPath = "./data/dl_input/SARD+NVD/train/"
    testdataSetPath = "./data/dl_input/SARD+NVD/test/"
    realtestdataSetPath = "data/"
    weightPath = './model/BRGU_0.2_2_raw'
    resultPath = "./BGRU/result_RAW/BGRU_0.2_2"
    #dealrawdata(raw_traindataSetPath, raw_testdataSetPath, traindataSetPath, testdataSetPath, batchSize, maxLen, vectorDim)
    main(traindataSetPath, testdataSetPath, realtestdataSetPath, weightPath, resultPath, batchSize, maxLen, vectorDim, layers, dropout)
    #testrealdata(realtestdataSetPath, weightPath, batchSize, maxLen, vectorDim, layers, dropout)
