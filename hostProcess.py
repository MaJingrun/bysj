#-*-coding:utf-8-*-

import fineGrainedCluster as fgc
import scipy.cluster.hierarchy as sch
import numpy as np
import sys
from multiprocessing import Pool
import time


import os

def getNormalHost(filePath):
    hosts=[]
    if os.path.exists(filePath):
        with open(filePath+'/'+'normal','r') as f:
            lines=f.readlines()
            for line in lines:
                line=line.strip()
                hosts.append(line)
        
    
    return hosts

def findLikeHost():
    """
        先找到所有的三级域，再 
        找到二级域名相同，三级域名相似的host，看看能不能合并
    """
    hosts=getNormalHost()
    
    d={}
    for host in hosts:
        hs=host.split('.')
        if len(hs)>1:
            key=hs[-2]+'.'+hs[-1]

            #if len(hs)>3:
            #    host=hs[-3]+'.'+hs[-2]+'.'+hs[-1]
            if key in d.keys():
                if host not in d[key]:
                    d[key].append(host)
            else:
                d[key]=[host]
    
    
    return d

def saveLikeHost(d):
    with open('result/mergehost','w') as f:
        for key in d.keys():
            if len(d[key])>2:
                for host in d[key]:
                    f.write(host)
                    f.write('\n')


def getClusterInHost(host,requestPath,clusterPath,sampleNum,metho,t,cri):
    
    sample=[]

    
    requests=getRequests(host,requestPath)

    if len(requests)<2:
        return
    
    filePath=clusterPath+'/'+host+'/'
    if not os.path.exists(filePath):
        os.mkdir(filePath)
    else:
        return

    for r in requests:
        featureList=fgc.Parse(r)
        sample.append(featureList)
            
    
    if len(sample)>sampleNum:
        dis=int(len(sample)/sampleNum)
        sample=sample[::dis]
    
    
    
    distanceMatrix = fgc.GetDistanceMatrix(sample)
    distanceArray = np.array(distanceMatrix)
    
    encodedCluster = sch.linkage(distanceArray, method=metho)
    
    flatCluster = sch.fcluster(
        encodedCluster, t=t, criterion=cri)

    
    for i in range(len(sample)):
        file=filePath+str(flatCluster[i])
        with open(file,'ab') as f:
            addInfo=requests[i]+'\n'
            add=addInfo.encode('utf-8')
            f.write(add)

    

    
def getRequests(host,requestPath):
    file = requestPath + '/request/'+host

    request=[]
    with open(file,'rb') as f:
        lines=f.readlines()
        for line in lines:
            r=line.decode('utf-8').strip()
            request.append(r)
    
    return request

def cluster(read,write,core,count,method,t,criterion):
    hosts=getNormalHost(read)

    p=Pool(core)
    
    print(time.asctime( time.localtime(time.time()) )+' cluster start...')
    for host in hosts:
        p.apply_async(getClusterInHost,(host,read,write,count,method,t,criterion,))
    
    p.close()
    p.join()
    print(time.asctime( time.localtime(time.time()) )+' cluster over...')


def main():

    readFilePath=sys.argv[1]
    writeFilePath=sys.argv[2]
    core=int(sys.argv[3])
    count=int(sys.argv[4])
    method=sys.argv[5]
    t=int(sys.argv[6])
    criterion=sys.argv[7]


    cluster(readFilePath,writeFilePath,core,count,method,t,criterion)

if __name__ == '__main__':
    main()



        