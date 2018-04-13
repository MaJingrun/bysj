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
    temp=host
    hs=host.split('.')

    if len(hs)>3:
        temp=hs[-3]+'.'+hs[-2]+'.'+hs[-1]
    return temp

def getSignature(file):
    sig=[]

    with open(file,'r') as f:
        lines=f.readlines()    
        for line in lines:
            line=line.strip()
            sig.append(line)
    
    return sig
    

def main():
    d=hp.findLikeHost('result')
    hp.saveLikeHost(d)
    signatures={}
    
    for k in d.keys():
        for i in range(len(d[k])-1,-1,-1):
            
            file='signature/'+d[k][i]

            if os.path.exists(file):
           
                
                sig=getSignature(file)
                tempHost=reduceHost(d[k][i])

                if tempHost in signatures.keys():
                    signatures[tempHost]+=sig
                 
                else:
              
                    signatures[tempHost]=sig
            else:
                d[k].pop(i)
        
        for h in signatures.keys():
            signatures[h]=list(set(signatures[h]))

        for i in range(len(d[k])):
            d[k][i]=reduceHost(d[k][i])
      
        d[k]=list(set(d[k]))


        for i in range(len(d[k])-1,0,-1):
            mergeSig=list(set(signatures[d[k][i]] + signatures[d[k][i-1]]))
            oldLength=len(signatures[d[k][i]]) + len(signatures[d[k][i-1]])
            if len(mergeSig) < oldLength:
                pre=88888888
                tH=mergeHost(d[k][i],d[k][i-1],pre)
                d[k].pop(i)

            


    

if __name__ == '__main__':
    main()