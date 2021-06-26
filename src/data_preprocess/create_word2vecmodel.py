## coding: utf-8
'''
This python file is used to tranfer the words in corpus to vector, and save the word2vec model under the path 'w2v_model'.

'''

from __future__ import print_function
from gensim.models import Word2Vec
import pickle
import os
import gc
import os


'''
DirofCorpus class
-----------------------------
This class is used to make a generator to produce sentence for word2vec training

# Arguments
    dirname: The src of corpus files 
    
'''
class DirofCorpus(object):  
    def __init__(self, dirname):
        self.dirname = dirname
        self.iter_num = 0
    
    def __iter__(self):
        print("\nepoch: ", self.iter_num)
        for d in self.dirname:
            for fn in os.listdir(d):
                print("\r"+fn, end='')
                for filename in os.listdir(os.path.join(d, fn)):
                    sample = pickle.load(open(os.path.join(d, fn, filename), 'rb'))[0]
                    yield sample
                    
        self.iter_num += 1

'''
generate_w2vmodel function
-----------------------------
This function is used to learning vectors from corpus, and save the model

# Arguments
    decTokenFlawPath: String type, the src of corpus file 
    w2vModelPath: String type, the src of model file
    
'''
def generate_w2vModel(decTokenFlawPath, w2vModelPath, size=30, alpha=0.008, window=5, min_alpha=0.0005, sg=1, hs=0, negative=7, iter=3):
    print("training...")
    model = Word2Vec(sentences= DirofCorpus(decTokenFlawPath), size=size, alpha=alpha, window=window, min_count=1, max_vocab_size=None, sample=0.001, seed=1, workers=1, min_alpha=min_alpha, sg=sg, hs=hs, negative=negative, iter=iter)
    model.save(w2vModelPath)   
'''
evaluate_w2vmodel function
-----------------------------
This function is used to load model and evaluate it.

# Arguments
    w2vModelPath: String type, the src of model file 
    
'''
def evaluate_w2vModel(w2vModelPath):  
    print("\nevaluating...")
    model = Word2Vec.load(w2vModelPath)
    for sign in ['(', 'icmp', 'func_0', 'i32', '%2']:
        print(sign, ":")
        print(model.most_similar_cosmul(positive=[sign], topn=10))
    

def main():
    dec_tokenFlaw_path = ['./data/corpus/']

    for iter in [3, 5, 10, 15]:
        w2v_model_path = "w2v_model/wordmodel_min_iter"+str(iter)+".model"
        generate_w2vModel(dec_tokenFlaw_path, w2v_model_path, iter=iter)
        evaluate_w2vModel(w2v_model_path)
    

 
   
if __name__ == "__main__":
    main()
