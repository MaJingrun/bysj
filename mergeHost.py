#-*-coding:utf-8-*-
#
#   这个程序用来合并指纹
#   将域名相似的指纹合并起来
#   例如 dns.weixin.qq.com 和 short.weixin.qq.com
#   会被合并成为 weixin.qq.com
# 

import hostProcess as hp
import os

def mergeHost(host1,host2,pre):

    hs1=host1.split('.')
    hs2=host2.split('.')

    if ( hs1[-2] + '.' + hs1[-1] ) != ( hs2[-2] + '.' + hs2[-1] ):
        return ''
    else:
        return pre + '.' + hs1[-2] + '.' + hs1[-1]

def reduceHost(host):
    '''
        将域名多于三级域的前面的去掉
    '''
    temp=host
    hs=host.split('.')

    if len(hs)>3:
        temp=hs[-3]+'.'+hs[-2]+'.'+hs[-1]
    return temp

def getSignature(file):
    '''
        从file文件读取签名，file文件位于signature文件夹下面
    '''
    sig=[]

    with open(file,'r') as f:
        lines=f.readlines()    
        for line in lines:
            line=line.strip()
            sig.append(line)
    
    return sig

def getHostPath(host):
    '''
        生成合并以后的指纹存放的地址
    '''
    hs=host.split('.')
    path=''
    for i in range(len(hs)-1,0,-1):
        path=path+hs[i]+'/'
    
    return path


def saveSignature(signatures):
    '''
        将合并后的指纹以文件的形式保存下来
    '''
    for host in signatures.keys():
        path='mergedSignature/'+getHostPath(host)
        if not os.path.exists(path):
            os.makedirs(path)
        file=path+host
        with open(file,'w') as f:
            for sig in signatures[host]:
                f.write(sig)
                f.write('\n')
    

def main():
    d=hp.findLikeHost('result')
    hp.saveLikeHost(d)
    signatures={}
    
    for k in d.keys():
        for i in range(len(d[k])-1,-1,-1):
            
            file='signature/'+d[k][i]

            #有些域名由于样本太少会出现没有签名的情况，如果没有签名的话就将此域名删掉
            if os.path.exists(file):
           
                
                sig=getSignature(file)

                #将dns.weixin.qq.com类似的域名变成只有三级域名的 weixin.qq.com
                tempHost=reduceHost(d[k][i])

                if tempHost in signatures.keys():
                    signatures[tempHost]+=sig
                 
                else:
              
                    signatures[tempHost]=sig
            else:
                d[k].pop(i)
        
        for h in signatures.keys():
            #去重处理
            signatures[h]=list(set(signatures[h]))
            signatures[h].sort(key=lambda x :len(x),reverse=True)


        '''
        for i in range(len(d[k])):
            d[k][i]=reduceHost(d[k][i])
      
        d[k]=list(set(d[k]))


        for i in range(len(d[k])-1,0,-1):
            mergeSig=list(set(signatures[d[k][i]] + signatures[d[k][i-1]]))
            oldLength=len(signatures[d[k][i]]) + len(signatures[d[k][i-1]])
            if len(mergeSig) < oldLength:
                pre=88888888
                tH=mergeHost(d[k][i],d[k][i-1],str(pre))
                pre-=1

                d[k].pop(i)
        '''
    saveSignature(signatures)
    for host in signatures.keys():
        if len(signatures[host])>3:
            print(host)

            


    

if __name__ == '__main__':
    main()