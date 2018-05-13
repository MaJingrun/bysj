#-*-coding:utf-8-*-
# 对host进行聚类，以及提供一些处理host的方法
# 
# 
# 
# 

import fineGrainedCluster as fgc
import scipy.cluster.hierarchy as sch
import numpy as np
import sys
from multiprocessing import Pool
import time


import os

def getNormalHost(filePath):
    '''
    从filepath目录下的normal得到normal host，也就是非cdn，非ip的host
    '''
    hosts=[]
    if os.path.exists(filePath):
        with open(filePath+'/'+'normal','r') as f:
            lines=f.readlines()
            for line in lines:
                line=line.strip()
                hosts.append(line)
        
    
    return hosts

def findLikeHost(filePath):
    """
        先找到所有的三级域，再 
        找到二级域名相同，三级域名相似的host，看看能不能合并
    """
    hosts=getNormalHost(filePath)
    
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
    '''
    对host下的所有请求进行层次聚类
    '''
    # 因为一个host可能有多种格式类型的请求，
    # 对host进行聚类后提取的指纹会更加准确
    # 
    # 
    # #
    sample=[]

    #获取host所对应的全部请求
    requests=getRequests(host,requestPath)

    if len(requests)<2:
        return
    
    filePath=clusterPath+'/'+host+'/'
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    else:
        return

    #对请求进行解析，划分为四部分，计算距离时会用到
    for r in requests:
        featureList=fgc.Parse(r)
        sample.append(featureList)
            
    
    #请求数量过多时进行取样，以减少计算量，样本数视运行环境而定
    if len(sample)>sampleNum:
        dis=int(len(sample)/sampleNum)
        sample=sample[::dis]
        requests=requests[::dis]
    
    
    #计算距离矩阵并进行层次聚类
    distanceMatrix = fgc.GetDistanceMatrix(sample)
    distanceArray = np.array(distanceMatrix)
    
    encodedCluster = sch.linkage(distanceArray, method=metho)
    
    flatCluster = sch.fcluster(
        encodedCluster, t=t, criterion=cri)

    
    #将聚类结果进行存储
    for i in range(len(sample)):
        file=filePath+str(flatCluster[i])
        with open(file,'ab') as f:
            addInfo=requests[i]+'\n'
            add=addInfo.encode('utf-8')
            f.write(add)

    

    
def getRequests(host,requestPath):
    '''
    获取对应host请求的函数
    '''
    file = requestPath + '/request/'+host

    request=[]
    with open(file,'rb') as f:
        lines=f.readlines()
        for line in lines:
            r=line.decode('utf-8').strip()
            request.append(r)
    
    return request

def cluster(read,write,core,count,method,t,criterion):
    '''
    利用多进程进行聚类
    '''
    
    hosts=getNormalHost(read)

    '''
    #创建进程池进行多进程聚类，进程数视运行环境而定
    p=Pool(core)
    
    print(time.asctime( time.localtime(time.time()) )+' cluster start...')
    for host in hosts:
        p.apply_async(getClusterInHost,(host,read,write,count,method,t,criterion,))
    
    p.close()
    p.join()
    print(time.asctime( time.localtime(time.time()) )+' cluster over...')
    '''
    for host in hosts:
        getClusterInHost(host,read,write,count,method,t,criterion)



def main():

    #程序运行所需要的参数
    
    #读取数据的文件目录
    readFilePath=sys.argv[1]

    #聚类后写入文件的目录
    writeFilePath=sys.argv[2]

    #打算使用的进程数
    core=int(sys.argv[3])

    #样本取样的数量
    count=int(sys.argv[4])

    #聚类时所使用的距离计算策略
    method=sys.argv[5]

    #距离阈值
    t=float(sys.argv[6])

    #聚类标准
    criterion=sys.argv[7]


    cluster(readFilePath,writeFilePath,core,count,method,t,criterion)

if __name__ == '__main__':
    main()



        