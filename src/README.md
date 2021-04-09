## Step 1: Source2slice

"xxxxx0.py" or "xxxxx0" is used to deal with patched files,another one is used to deal with vulnerable files.

1. NVD files

 (1). allCompilexxx.py或allCompilexxx0.py
python allCompilexxx.py(或allCompilexxx0.py) xxx.xls ,"xxx" means name of software. This file is used to compile the source code file to get .bc file,and also extract four      kinds of focus. source_root is the directory of source code files,diff_root is the directory of diff files,slicer_root is the directory of output files. And also hole_line.txt is output of this step,and then renamed as "xxx-hole_line.txt".

 (2). autoReorder.py
python2 autoReorder.py ../../newslice(或newslice0)/ , "newslice" is the directory of slice files. This file is used to reorder the sentences extracted from source code file. The output is .final.ll file in the directory of newslice,that is llvm slice.

 (3). getFlawLoc.py
python2 getFlawLoc.py ../../newslice(或newslice0)/, "newslice" is the directory of slice files. This file is used to get slice2flawline.pkl, which contains the linenum of vullines.

 (4). addFlawtag.py
python addFlawtag.py xxx-hole_line.txt, "xxx" means name of software. This file is used to get the source code slices(.slicer.c) corresponding to the llvm slices in the directory of newslice.

 (5). getSourceLine.py
python getSourceLine.py ../../newslice（或newslice0）/, this file is used to the slice2flawline.pkl,which contains the linenum of vullines corresponding to the .slicer.c files.

2. SARD files

 (1). getVulLineForCounting.py
python getVulLineForCounting.py ../../000 ../../xxx.xml, this file is used to get the linenums of vulline in source code file. The input is source code file and xxx.xml file. The output is xxx.txt file, and renamed as SARD-hole_line.txt.

 (2). multiFileCompile.py
python multiFileCompile.py ../../000/ ../../xxx.xml, this file is used to compile source code file to get .bc file.

 (3). get-llvmwithline.cpp
./get-llvmwithline SARD-hole_line.txt, this file is used to extract four kinds of focus, and output file is in the directory of "000".

 (4). autoReorder.py
python2 autoRecorder.py ../../000/, the same as NVD files.

 (5). getFlawLoc.py
python2 getFlawLoc.py ../../000/, the same as NVD files.

 (6). addFlawtag.py
python addFlawtag.py SARD-hole_line.txt, the same as NVD files. 

 (7). getSourceLine.py
python getSourceLine.py ../../000/, the same as NVD files.

## Step 2: Data preprocess

1. process_dataflow.py: Get the corpus of slices generated from the systhetic and academic dataset; process_dataflow_NVD.py: get the corpus of slices generated from the real-world dataset. The input is slices generated from the systhetic and academic dataset and the real-world dataset and the output is corpus files.

2. create_word2vecmodel.py: Train the word2vec model. The input is the corpus files and the output is the trained model.

3. get_dl_input.py. Get the vectors of tokens in the corpus files. The input is the corpus file and the trained word2vec model and the output is the vector file.

## Step 2: Model training ##

1. bgru_threshold.py: Train the BGRU model which can locate the vulnerabilities and evaluate it. The input is the training dataset and the test dataset, and the output is the trained BGRU model.

2. bgru_raw.py: Train the original BGRU model.
