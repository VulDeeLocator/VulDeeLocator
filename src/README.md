## Step 1: Data preprocess##

1. process_dataflow.py: Get the corpus of slices generated from the SARD dataset; process_dataflow_NVD.py: get the corpus of slices generated from the NVD dataset. The input is slices generated from the SARD dataset and the NVD dataset and the output is corpus files.

2. create_word2vecmodel.py: Train the word2vec model. The input is the corpus files and the output is the trained model.

3. get_dl_input.py. Get the vectors of tokens in the corpus files. The input is the corpus file and the trained word2vec model and the output is the vector file.

## Step 2: Model training ##

1. bgru_threshold.py: Train the BGRU model which can locate the vulnerabilities and evaluate it. The input is the training dataset and the test dataset, and the output is the trained BGRU model.

2. bgru_raw.py: Train the original BGRU model.
