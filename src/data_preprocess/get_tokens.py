# -*- coding:utf-8 -*-
'''
Created on 2016年11月28日

@author: lenovo
'''
import re
import os
import string
import xlrd


def isphor(s, liter):    
    m = re.search(liter,s)
    if m is not None:
        return True
    else: 
        return False
        
def create_tokens(sentence):
    phla='[^$#!@.%_a-zA-Z0-9*]'
    space='\s'  
    spa=''  
    tokens=[]
    j=0
    i=0
    
    while(i<len(sentence)):
        if isphor(sentence[i],space):  
            if i>j:
                tokens.append(sentence[j:i])
                j=i+1
            else:
                j=i+1
                
        elif isphor(sentence[i],phla) or (sentence[i] == ":" and sentence[i-1] != ":") or (sentence[i] == "&" and sentence[i-1] != "&"):
            if (sentence[i] == ":" and sentence[i-1] != ":") or (sentence[i] == "&" and sentence[i-1] != "&"):
                tokens.append(sentence[j:i])
                tokens.append(sentence[i:i+2])
                j=i+2
                i=i+2
            elif sentence[i:i+3] == "...":
                tokens.append(sentence[j:i])
                tokens.append(sentence[i:i+3])
                j=i+3
                i=i+2
            elif i+1<len(sentence) and isphor(sentence[i+1],phla):
                tokens.append(sentence[j:i])
                tokens.append(sentence[i])
                tokens.append(sentence[i+1])
                j=i+2
                i=i+1      
            else:
                tokens.append(sentence[j:i])
                tokens.append(sentence[i])
                j=i+1
                
        i=i+1
    tokens.append(sentence[j:i])
        
    count=0
    count1=0
    sub0='\r'
    
    if sub0 in tokens:
        tokens.remove('\r')
        
    for sub1 in tokens:
        if sub1==' ':
            count1=count1+1
            
    for j in range(count1):
        tokens.remove(' ')
        
    for sub in tokens:
        if sub==spa:
            count=count+1
            
    for i in range(count):
        tokens.remove('')
        
    return tokens
