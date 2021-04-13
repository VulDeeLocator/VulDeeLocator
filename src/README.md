## Environment

Source2slice: clang-6.0 + llvm + dg (dg: https://github.com/mchalupa/dg)

Data preprocess and Model training: python3.6 + tensorflow1.6 + keras2.1.2 + gensim3.4

## Step 1: Source2slice

"xxxxx0.py" or "xxxxx0" is used to deal with patched files, another one is used to deal with vulnerable files.

### 1. NVD files

 (1). allCompilexxx.py (or allCompilexxx0.py)
 
> python allCompilexxx.py (or allCompilexxx0.py) xxx.xls, "xxx" means name of software. 

This file is used to compile the source code file to get .bc file, and also extract four      kinds of focuses (i.e., sSyVCs). source_root is the directory of source code files, diff_root is the directory of diff files, slicer_root is the directory of output files. hole_line.txt is the  output of this step, which is renamed as "xxx-hole_line.txt".

 (2). autoReorder.py
 
> python2 autoReorder.py ../../newslice (or newslice0)/, "newslice" is the directory of slice files. 

This file is used to reorder the statements extracted from the source code file. The output is .final.ll file in the directory of newslice, which is an llvm slice.

 (3). getFlawLoc.py
 
> python2 getFlawLoc.py ../../newslice (or newslice0)/, "newslice" is the directory of slice files. 

This file is used to get slice2flawline.pkl, which contains the line number of vulnerale lines.

 (4). addFlawtag.py
 
> python addFlawtag.py xxx-hole_line.txt, "xxx" means name of software. 

This file is used to get the source code slices (.slicer.c) corresponding to the llvm slices in the directory of newslice.

 (5). getSourceLine.py
 
> python getSourceLine.py ../../newslice（or newslice0）/ 

This file is used to the slice2flawline.pkl, which contains the line number of vulnerable lines corresponding to the .slicer.c files.

### 2. SARD files

 (1). getVulLineForCounting.py
 
> python getVulLineForCounting.py ../../000 ../../xxx.xml 

This file is used to get the line numbers of vulnerable lines in the source code file. The input is the source code file and xxx.xml file. The output is xxx.txt file, which is renamed as SARD-hole_line.txt.

 (2). multiFileCompile.py
 
> python multiFileCompile.py ../../000/ ../../xxx.xml 

This file is used to compile the source code file to .bc file.

 (3). get-llvmwithline.cpp
 
> ./get-llvmwithline SARD-hole_line.txt 

This file is used to extract four kinds of focuses. The output file is in the directory of "000".

 (4). autoReorder.py
 
> python2 autoRecorder.py ../../000/ 

This is the same as NVD files.

 (5). getFlawLoc.py
 
> python2 getFlawLoc.py ../../000/

This is the same as NVD files.

 (6). addFlawtag.py
 
> python addFlawtag.py SARD-hole_line.txt

This is the same as NVD files. 

 (7). getSourceLine.py
 
> python getSourceLine.py ../../000/

This is the same as NVD files.

## Step 2: Data preprocess ##

1. process_dataflow.py: Get the corpus of slices generated from the systhetic and academic dataset. 
process_dataflow_NVD.py: Get the corpus of slices generated from the real-world dataset. 
The input is slices generated from the systhetic and academic dataset and the real-world dataset and the output is corpus files.

2. create_word2vecmodel.py: Train the word2vec model. The input is the corpus files and the output is the trained model.

3. get_dl_input.py. Get the vectors of tokens in the corpus files. The input is the corpus file and the trained word2vec model and the output is the vector file.

## Step 3: Model training ##

1. bgru_threshold.py: Train the BGRU model which can locate the vulnerabilities and evaluate it. The input is the training dataset and the test dataset, and the output is the trained BGRU model.

2. bgru_raw.py: Train the original BGRU model.
