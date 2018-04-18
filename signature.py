import signatureTest as st
import hostProcess as hp
from multiprocessing import Pool
import alignment as alignment
import os
import re
import time
import sys

def getSignature2(host,readPath,writePath,count):
    
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
            with open(filePath,'w') as f:
                for s in sig:
                    f.write(s)
                    f.write('\n')

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

def generateSignature(read,write,core,count):
    hosts=hp.getNormalHost('result')

    p=Pool(core)
    print(time.asctime( time.localtime(time.time()) )+' get signatures...')
    for host in hosts:
        p.apply_async(getSignature2,(host,read,write,count,))
    
    p.close()
    p.join()
    print(time.asctime( time.localtime(time.time()) )+' signature over...')

def main():
    read=sys.argv[1]
    write=sys.argv[2]
    core=int(sys.argv[3])
    count=int(sys.argv[4])
    

    generateSignature(read,write,core,count)

if __name__ == '__main__':
    main()          

