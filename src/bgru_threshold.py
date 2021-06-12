## coding: utf-8
'''
This python file is used to train four class focus data in bgru model
'''

from __future__ import absolute_import
from __future__ import print_function
from keras import metrics
from keras.optimizers import SGD, RMSprop, Adagrad, Adam, Adadelta
from keras.models import Sequential, load_model, Model
from keras.layers import Input, Multiply
from keras.layers.core import Masking, Dense, Dropout, Activation, Lambda, Reshape
from keras.layers.recurrent import GRU, LSTM
from keras.layers.pooling import GlobalAveragePooling1D
from keras.engine.topology import Layer, InputSpec
from preprocess_dl_Input_version4 import *
from keras.layers.wrappers import Bidirectional, TimeDistributed
from collections import Counter
import keras.backend as K
import tensorflow as tf
import numpy as np
import pickle
import random
import time
import math
import os


RANDOMSEED = 2018  # for reproducibility
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

class NonMasking(Layer):
    """
	Non Masking Layer
    """
    
    def __init__(self, **kwargs):
        self.supports_masking = True
        super(NonMasking, self).__init__(**kwargs)
    
    def build(self, input_shape):
        input_shape = input_shape
    
    def compute_mask(self, input, input_mask=None):
        return None
    
    def call(self, x, mask=None):
        return x
        
    def compute_output_shape(self, input_shape):
        return input_shape
        
class KMaxPooling(Layer):
    """K-max pooling
    
    k-max pooling layer that extracts the k-highest activations from a sequence and calculate average
    base on Tensorflow backend.
    """
    def __init__(self, k=1, **kwargs):
        super(KMaxPooling,self).__init__(**kwargs)
        self.input_spec = InputSpec(ndim = 3)
        self.k = k
        
    def compute_output_shape(self, input_shape):
        return (input_shape[0], self.k, input_shape[1])
        
    def call(self, inputs):
        top_k = tf.nn.top_k(inputs, k=self.k, sorted=True, name=None)[0]
        shifted_output = tf.transpose(top_k, [0, 2, 1])
        return shifted_output

def build_model(maxlen, vector_dim, dropout=0.4):
    """build model
    
    Build the model according to the arguments.
    
    # Arguments                                         
        maxlen: The max length of a sample              
        vector_dim: The size of token's dim             
        dropout : the rate of dropout                   
        winlen : the length of average pooling windows  
    
    # Returns
        model : model just build
    """
    
    print('Build model...')

    inputs = Input(shape=(maxlen, vector_dim))
    mask_1 = Masking(mask_value=0.0, name='mask_1')(inputs)
    bgru_1 = Bidirectional(GRU(units=512, activation='tanh', recurrent_activation='hard_sigmoid', return_sequences=True), name='bgru_1')(mask_1)
    dropout_1 = Dropout(dropout, name='dropout_1')(bgru_1)
    bgru_2 = Bidirectional(GRU(units=512, activation='tanh', recurrent_activation='hard_sigmoid', return_sequences=True), name='bgru_2')(dropout_1)
    dropout_2 = Dropout(dropout, name='dropout_2')(bgru_2)
    dense_1 = TimeDistributed(Dense(1), name='dense1')(dropout_2)
    activation_1 = Activation('sigmoid', name='activation_1')(dense_1)
    unmask_1 = NonMasking()(activation_1)
	
    vulner_mask_input = Input(shape=(maxlen, maxlen), name='vulner_mask_input')  
    multiply_1 = Multiply(name='multiply_1')([vulner_mask_input, unmask_1])  
    reshape_1 = Reshape((1, maxlen ** 2))(multiply_1)  
    k_max_1 = KMaxPooling(k=1, name='k_max_1')(reshape_1)  
    average_1 = GlobalAveragePooling1D(name='average_1')(k_max_1) 
    
    print("begin compile")
    model = Model(inputs=[inputs, vulner_mask_input], outputs=average_1)
    model.compile(loss='binary_crossentropy', optimizer='adamax', metrics=['TP_count', 'FP_count', 'FN_count', 'precision','recall', 'fbeta_score'])
    model.summary()
 
    return model


def main(traindataSet_path, testdataSet_path, weightpath, resultpath, batch_size, maxlen, vector_dim, **kw):
    """Train model and test model
    
    Build the model and preprocess dataset for training, then train the model
    using the train dataset and save them to the weight path, test the test
    dataset and save the test result into result path.
    
    # Arguments                                      
        traindataSet_path: The path of train dataset    
        testdataSet_path: The path of test dataset      
        weightpath: The path to save the model          
        resultpath: The path to save the test result   
        batch_size: The size of minibatch               
        maxlen: The max length of a sample              
        vector_dim: The size of token's dim             
        **kw : the dict arguments for model, like layers and so on 
    # Returns
        None
    """

    model = build_model(maxlen, vector_dim, **kw)
    
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
    
    print("Train...")
    model.fit_generator(train_generator, steps_per_epoch=steps_epoch, epochs=4)

    model.save_weights(weightpath)
    
    #model.load_weights(weightpath)
    
    dataset = []
    linetokens = []
    vpointers = []
    funcs = []
    testcase = []
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
        testcase +=testcase_file
    print(len(dataset),len(testcase))

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
        
    batch_size = 64
    test_generator = generator_of_data(dataset, labels, linetokens, vpointers, batch_size, maxlen, vector_dim)
    all_test_samples = len(dataset)
    steps_epoch = int(all_test_samples / batch_size)
    get_bgru_output = K.function([model.layers[0].input, K.learning_phase()], [model.layers[7].output]) #一层BGRU时读取第5层，两层BGRU时读取第7层，三层BGRU时读取第9层
    TP, TN, FP, FN = 0, 0, 0, 0
    TP_l, TN_l, FP_l, FN_l = 0, 0, 0, 0
    TP_index = []
    results = {}
    dict_testcase2func = {}
    start = time.time()
	
    for i in range(steps_epoch):
        print("\r", i, "/", steps_epoch, end="")
        test_input = next(test_generator)
        layer_output = get_bgru_output([test_input[0][0],0])

        for j in range(batch_size):
            index = i*batch_size + j

            result = sample_threshold_windows(layer_output[0][j], linetokens[index], {'threshold_value':0.5, 'k':1})#result是漏洞行的行号
        
            if result:
                y_pred = 1
            else:
                y_pred = 0
                        
            if y_pred == 0 and labels[index] == 0:
                TN += 1
                TN_l += 1
                with open("result_analyze/TN/"+str(index)+".pkl","wb") as f:
                    pickle.dump(list([layer_output[0][j]]),f)
                with open("result_analyze/TN_testcase_id.txt",'a+') as ftn:
                    ftn.write(testcase[index]+'\n')
            if y_pred == 0 and labels[index] == 1:
                FN += 1
                FN_l += 1
                with open("result_analyze/FN/"+str(index)+".pkl","wb") as f:
                    pickle.dump(list([layer_output[0][j]]),f)
                with open("result_analyze/FN_testcase_id.txt",'a+') as ffn:
                    ffn.write(testcase[index]+'\n')
					
            if y_pred == 1 and labels[index] == 0:
                FP += 1
                FP_l += 1
                if not testcase[index].split("/")[0] in dict_testcase2func.keys():
                    dict_testcase2func[testcase[index].split("/")[0]]={}
                for func in funcs[index]:
                    if func in dict_testcase2func[testcase[index].split("/")[0]].keys():
                        dict_testcase2func[testcase[index].split("/")[0]][func].append("FP")
                    else:
                        dict_testcase2func[testcase[index].split("/")[0]][func] = ["FP"]
                with open("result_analyze/FP/"+str(index)+".pkl","wb") as f:
                    pickle.dump(list([layer_output[0][j]]),f)
                with open("result_analyze/FP_testcase_id.txt",'a+') as ffp:
                    ffp.write(testcase[index]+'\n')					
                    
            if y_pred == 1 and labels[index] == 1:
                TP += 1
                TP_index.append(index)
                flag_l = False
                for pred in result:
                    if linetokens[index][pred] in vpointers[index]:
                        flag_l = True
                        break
                if flag_l:
                    TP_l += 1
                else:
                    FN_l += 1
                if not testcase[index].split("/")[0] in dict_testcase2func.keys():
                    dict_testcase2func[testcase[index].split("/")[0]]={}
                for func in funcs[index]:
                    if func in dict_testcase2func[testcase[index].split("/")[0]].keys():
                        dict_testcase2func[testcase[index].split("/")[0]][func].append("TP")
                    else:
                        dict_testcase2func[testcase[index].split("/")[0]][func] = ["TP"]
                with open("result_analyze/TP/"+str(index)+".pkl","wb") as f:
                    pickle.dump(list([layer_output[0][j]]),f)
                with open("result_analyze/TP_testcase_id.txt",'a+') as ftp:
                    ftp.write(testcase[index]+'\n')
         
            results[testcase[index]] = result
    end = time.time()
    print(end - start)
        
    with open(resultpath+"_result.pkl", 'wb') as f:
        pickle.dump(results, f)
        
    with open(resultpath+"_dict_testcase2func.pkl", 'wb') as f:
        pickle.dump(dict_testcase2func, f)
        
    with open("TP_index_BGRU.pkl", 'wb') as f:
        pickle.dump(TP_index, f)
        
    with open(resultpath, 'a') as fwrite:
        fwrite.write('test_samples_num: '+ str(len(dataset)) + '\n')
        fwrite.write('train_dataset: ' + str(traindataSetPath) + '\n')
        fwrite.write('test_dataset: ' + str(filename) + '\n')
        fwrite.write('model: ' + weightPath + '\n')
        fwrite.write('TP:' + str(TP) + ' FP:' + str(FP) + ' FN:' + str(FN) + ' TN:' + str(TN) + '\n')
        FPR = FP / (FP + TN)
        fwrite.write('FPR: ' + str(FPR) + '\n')
        FNR = FN / (TP + FN)
        fwrite.write('FNR: ' + str(FNR) + '\n')
        accuracy = (TP + TN) / (len(dataset))
        fwrite.write('accuracy: ' + str(accuracy) + '\n')
        precision = TP / (TP + FP)
        fwrite.write('precision: ' + str(precision) + '\n')
        recall = TP / (TP + FN)
        fwrite.write('recall: ' + str(recall) + '\n')
        f_score = (2 * precision * recall) / (precision + recall)
        fwrite.write('fbeta_score: ' + str(f_score) + '\n')
		#location
        fwrite.write('TP_l:' + str(TP_l) + ' FP_l:' + str(FP_l) + ' FN_l:' + str(FN_l) + ' TN:' + str(TN_l) + '\n')
        FPR_l = FP_l / (FP_l + TN_l)
        fwrite.write('FPR_location: ' + str(FPR_l) + '\n')
        FNR_l = FN_l / (TP_l + FN_l)
        fwrite.write('FNR_location: ' + str(FNR_l) + '\n')
        accuracy_l = (TP_l + TN_l) / (TP_l + FP_l + FN_l + TN_l)
        fwrite.write('accuracy_location: ' + str(accuracy_l) + '\n')
        precision_l = TP_l / (TP_l + FP_l)
        fwrite.write('precision_location: ' + str(precision_l) + '\n')
        recall_l = TP_l / (TP_l + FN_l)
        fwrite.write('recall_location: ' + str(recall_l) + '\n')
        f_score_l = (2 * precision_l * recall_l) / (precision_l + recall_l)
        fwrite.write('fbeta_score_location: ' + str(f_score_l) + '\n')
        fwrite.write('--------------------\n')
        
    print("\nf1: ",f_score)
    
    
def sample_threshold_windows(value_sequence, linetokens, argv):
    """read the output of RNN deaplearning model output sequence and return the classify result
    
    Input the output of RNN model's top activation(sigmoid) layer,
    read them by time step, and judge the value according to the threshold
    value, count the average that value bigger than threshold, and return the
    classify result 1 or 0.
    
    # Arguments
        value_sequence: The output sequence from RNN model
        linetokens: The index of first token each line      
        argv: The dict of argument, contain 'k' 'threshold_value'
    
    # Returns
        linenum: The line predict to have vulnerability's line num      
    """
        
    if "threshold_value" in argv: 
        threshold_value = argv["threshold_value"]
    else:
        print("Error:Bad threshold value!")
        return -1
    if "k" in argv:
        k = argv["k"]
    else:
        k = 3
        
    value_sequence = list(value_sequence)
    vs = len(value_sequence)-1
    while value_sequence[vs] == value_sequence[-1]:
        vs -= 1
    value_sequence = value_sequence[:vs+2]
        
    for tokenindex in range(len(linetokens)):
        if len(value_sequence) <= linetokens[tokenindex]:
            linetokens = linetokens[:tokenindex]
            linetokens.append(len(value_sequence))
            break
    if len(value_sequence) > linetokens[-1]:
        linetokens.append(len(value_sequence))

    linenum = []
    for i in range(len(linetokens)-1):
        left = linetokens[i]
        right = linetokens[i+1]
        if left == right:
            right += 1
        window = value_sequence[left: right]
        window = [x[0] for x in window]
        window.sort(reverse = True)
        k_max = window[:k]
        if sum(k_max)/ len(k_max) > threshold_value:
            linenum.append(i)
    
    return linenum
    
def testrealdata(realtestpath, weightpath, batch_size, maxlen, vector_dim, dropout):
    """This function is used to judge the real data(data without label) is vulnerability or not

    # Arguments
    realdataSet_path: String type, the data path to load real data set
    weight_path: String type, the data path of model
    batch_size: Int type, the mini-batch size
    maxlen: Int type, the max length of data
    vector_dim: Int type, the number of data vector's dim
    dropout: Float type. the value of dropout
    
    """
    model = build_model(maxlen, vector_dim, dropout)
    model.load_weights(weightpath)
    
    for filename in os.listdir(realtestpath):
        print(filename)
        print("Loading data...")
        f = open(realtestpath+filename, "rb")
        realdata = pickle.load(f, encoding="latin1")
        f.close()

        labels = model.predict(x = realdata[0],batch_size = 1)
        for i in range(len(labels)):
            if labels[i][0] >= 0.5:
                print(realdata[1][i])

if __name__ == "__main__":
    batchSize = 64
    vectorDim = 30 
    maxLen = 900 
    dropout = 0.4  
    traindataSetPath = "./data/dl_input/train/"  
    testdataSetPath = "./data/dl_input/test/"
    #realtestdataSetPath = "./data/dl_input/realdata/"  
    weightPath = 'model/bgru_0.4_k=1.h5'  
    resultPath = "result/bgru_0.4_k=1.2" 
    #dealrawdata(raw_traindataSetPath, raw_testdataSetPath, traindataSetPath, testdataSetPath, batchSize, maxLen, vectorDim)
    main(traindataSetPath, testdataSetPath, weightPath, resultPath, batchSize, maxLen, vectorDim, dropout=dropout)
    #testrealdata(realtestdataSetPath, weightPath, batchSize, maxLen, vectorDim, dropout)
