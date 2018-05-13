#-*- coding:utf-8 -*-
#
# 指纹提取部分，将聚类后的请求按每一类提取一个指纹
# 即，一个host可能对应多个指纹
# 这跟一个host可能有多种格式的请求是相关的
#
#
#
import signatureTest as st
import hostProcess as hp
from multiprocessing import Pool
import alignment as alignment
import os
import re
import time
import sys

def getSignature2(host,readPath,writePath,count):
    '''
    用smith waterman算法对请求进行序列比对，找到最合适的子序列，
    经过加工，生成签名
    '''
    
    sig=[]
    filePath=readPath+'/'+host+'/'
    if os.path.exists(filePath):
        files=os.listdir(filePath)
       
        for file in files:
            
            sample=[]
            with open(filePath+file,'rb') as f:
                lines=f.readlines()
                for line in lines:
                    line=line.decode('utf-8').strip()
                    sample.append(line)
            
            
            if len(sample)>count:
                dis=int(len(sample)/count)
                sample=sample[::dis]
            if len(sample)>1:
                symbol=alignment.water(sample[0],sample[1])
                for i in range(2,len(sample)):
                    symbol=alignment.water(symbol,sample[i])
                
                '''
                tokens=st.GetTokenList(sample)
                
                signature=st.GetSignature(tokens)
                '''
                symbol=symbol.replace(' ','(.*)')
                wildcard='(.*)?'
                signature=''
                signatureSplit=symbol.split('(.*)')
                
                for s in signatureSplit:
                    if s != '':
                        signature+=wildcard
                        signature+='('
                        signature+=re.escape(s)
                        signature+=')'
                signature+=wildcard

                sig.append(signature)
        
    
        sig=list(set(sig))
        
        sig.sort(key=lambda x:len(x))
        
        
        if len(sig)>0:
            
            filePath=writePath+'/'+host
            with open(filePath,'wb') as f:
                for s in sig:
                    s=s.encode('utf-8')
                    f.write(s)
                    f.write('\n'.encode('utf-8'))

def getSignature(host,readPath,writePath,count):
    
    sig=[]
    filePath=readPath+'/'+host+'/'
    if os.path.exists(filePath):
        files=os.listdir(filePath)
       
        for file in files:
            
            sample=[]
            with open(filePath+file,'rb') as f:
                lines=f.readlines()
                for line in lines:
                    line=line.decode('utf-8').strip()
                    sample.append(line)
            
            
            if len(sample)>count:
                dis=int(len(sample)/count)
                sample=sample[::dis]
            if len(sample)>2:
                
                tokens=st.GetTokenList(sample)
                
                signature=st.GetSignature(tokens)
                
                sig.append(signature)
        
    
        sig=list(set(sig))
        
        sig.sort(key=lambda x:len(x))
        
        
        if len(sig)>0:
            
            filePath=writePath+'/'+host
            with open(filePath,'w') as f:
                for s in sig:
                    f.write(s)
                    f.write('\n')

def generateSignature(read,write,hostPath,core,count):
    hosts=hp.getNormalHost(hostPath)

    '''

    p=Pool(core)
    print(time.asctime( time.localtime(time.time()) )+' get signatures...')
    for host in hosts:
        p.apply_async(getSignature2,(host,read,write,count,))
    
    p.close()
    p.join()
    print(time.asctime( time.localtime(time.time()) )+' signature over...')

    '''

    for host in hosts:
        getSignature2(host,read,write,count)

def main():
    read=sys.argv[1]
    write=sys.argv[2]
    hostPath=sys.argv[3]
    core=int(sys.argv[4])
    count=int(sys.argv[5])
    

    generateSignature(read,write,hostPath,core,count)

if __name__ == '__main__':
    main()          

