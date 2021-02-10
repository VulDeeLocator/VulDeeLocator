Steps:
1、data_preprocess

（1）process_dataflow.py : get corpus of slices generated from SARD datasets；
     process_dataflow_NVD.py : get corpus of slices generated from NVD datasets.
	 The input is slices generated from SARD datasets and NVD datasets. The output is corpus files.

（2）create_word2vecmodel.py : train the word2vec model；
	 The input is the corpus files.The output is trained model.

（3）get_dl_input.py : get the vectors of tokens in the corpus files；
	 The input is the corpus file and trained word2vec model. The output is the vector file.

2、train the model
   
（1）bgru_threshold.py: train the BGRU model which can locate the vulnerabilities and evaluate it .
	 The input is the train datasets and test datasets,and the output is the trained BGRU model.

（2）bgru_raw.py :original BGRU model.
