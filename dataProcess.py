#-*- coding:utf-8 -*-
import re
import sys
import os

def reduceRequest(request):
    requestPage=''
    requestMethod=''

    splitBlank=request.split(' ')
    temp=''.join(splitBlank)

    requestMethod=splitBlank[0]
    requestPage=temp.replace(requestMethod,'',1).replace('HTTP/1.1','')
    
    newParameters=''
    if '?' in requestPage:
        rs=requestPage.split('?')
        page=rs[0]
        pages=page.split('/')
        t=''.join(rs)
        p=t.replace(page,'')
        #parameters='?'+rs[1]
        newP='?'
        parameters=p.split('&')
        for parameter in parameters:
            if parameter != '':
                if '=' in parameter:
                    kv=parameter.split('=')
                    newP+='&'+kv[0]+'=(.*)'
                else:
                    newP+='&'+parameter+'(.*)'
        newParameters=newP.replace('?&','?')


    else:
        pages=requestPage.split('/')

    newR=requestMethod+' '
    for i in range(len(pages)-1):
        newR=newR+pages[i]+'/'
    newR=newR+newParameters+' HTTP/1.1'
    return newR

def getFileNames(filePath):
    
    #文件名存在一个文本文件FileList中，将其中的文件名读取出来
    names=[]

    if os.path.exists(filePath):
        names=os.listdir(filePath)

    return names


def getSampleList(filePath):
    #依次读取每个文件，得到所有完整数据的样本
    '''
        每个sample的组织样式是这样的
        [
            2017-12-14 00:02:12.825 221.130.199.88 51895:80 6] busstype:007003000	url:http://openbox.mobilem.360.cn/GameFloatWindow/gameList?&ver=v2 	dir:1	http_header:,
            POST /GameFloatWindow/gameList?&ver=v2 HTTP/1.1,
            Host: openbox.mobilem.360.cn,
            Connection: Keep-Alive,
            User-Agent: Dalvik/1.6.0 (Linux; U; Android 4.4.2; SM-G900H Build/KOT49H)
        ]

        sampleList是这样的
        [ sample1, sample2, sample3, ...... ]
    '''
    fileNames=getFileNames(filePath)
    sampleList=[]

    i=0
    for name in fileNames:
        
        with open(filePath+'/'+name,'rb') as f:
            lines=f.readlines()
            sample=[]

            pattern=r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3})'
            for line in lines:
                try:
                    temp=line.decode('utf-8')                
                except:
                    try:
                        temp=line.decode('gbk')
                    except:
                        try:
                            temp=line.decode('latin1')
                        except:
                            i+=1
                            print(line)
                            continue
                    
                        
                temp=temp.strip() 
                if re.match(pattern,temp):
                    if len(sample)>1:
                        sampleList.append(sample)
                        
                    sample=[]
                    sample.append(temp)
                elif temp=='':
                    continue
                else:
                    sample.append(temp) 

    return sampleList

def getHost(sample):   
      
    for item in sample:
        if item.startswith('Host: '):
            t1=item.replace('Host: ','')
            t2=t1.split(':')
            host=t2[0]
            host=host.lower()

           
            return host
    
    return ''

def getBusstype(sample):
    
    for item in sample:
        if 'busstype:' in item:
            id = item[item.find('busstype:') + 9:item.find('busstype:') + 18]
            return id
    
    return ''

def getRequest(sample):
    
    request=('OPTIONS ','POST ','GET ','HEAD ','PUT ','TRACE ')
    
    for item in sample:
        if item.startswith(request):
            return item
    
    return ''

def getTimeStamp(sample):
    pattern=r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3})'
    for item in sample:
        if re.match(pattern,item):
            return item[:23]
    return ''
    

def getHostAndRequest(samples):
    
    d={}
    for sample in samples:
        host = getHost(sample)
        request = getRequest(sample)
        if host != '' and request != '':
            if host in d.keys():
                    d[host].append(request)
            else:
                d[host] = [request]
        else:
            pass
    
    for host in d.keys():
        d[host]=list(set(d[host]))
        
    return d

def getHBs(samples):
    
    '''
        得到所有样本中的(host，busstype)对
        例如('app.lizhi.fm','008003000')
    '''

    hbs=[]

    for sample in samples:
        
        host=getHost(sample)
        busstype=getBusstype(sample)


        if host!='' and busstype!='':
            hbs.append((host,busstype))
    
    return list(set(hbs))

def isCdn(host,cdnlist):
    for cdn in cdnlist:
        cdn=cdn.replace('*.','.')
        if cdn in host:
            return True
    
    return False 

def classHBsByHost(hbs):
    
    '''
        对host进行分类
        1.ip类 
        2.cdn类
        3.正常类
    '''
    
    ip=[]
    cdn=[]
    normal=[]
    pattern=r'((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))'

    cdnlist=[]
    with open('cdnlist.txt','r') as f:
        lines=f.readlines()
        for line in lines:
            line=line.replace('*.','.')
            cdnlist.append(line.strip())

    for hb in hbs:
        
        '''
        t=hb[0].split('.')
        if len(t)>1:
            d=t[-2]+'.'+t[-1]
        else:
            d='##################'
        '''
        
        if re.match(pattern,hb[0]):
            ip.append(hb)
        elif isCdn(hb[0],cdnlist):
            cdn.append(hb)
        else:
            normal.append(hb)
    
    return ip,cdn,normal

def getReducedSample(samples):
    q=[]
    for sample in samples:
        host=getHost(sample)
        busstype=getBusstype(sample)
        timeStamp=getTimeStamp(sample)
        q.append((timeStamp,host,busstype))
    
    return q
        
        

def saveHBs(hbs):
    with open('hbs','w') as f:
        for hb in hbs:
            f.write(hb[0]+' '+hb[1])
            f.write('\n')

def saveHost(ip,cdn,normal,filePath='result'):
    if not os.path.exists(filePath):
        os.mkdir(filePath)
    with open(filePath+'/'+'ip','w') as f:
        for host in ip:
            f.write(host)
            f.write('\n')
    
    with open(filePath+'/'+'cdn','w') as f:
        for host in cdn:
            f.write(host)
            f.write('\n')

    with open(filePath+'/'+'normal','w') as f:
        for host in normal:
            f.write(host)
            f.write('\n')

def saveRequest(d,ip,cdn,normal,filePath='result'):
    if not os.path.exists(filePath):
        os.mkdir(filePath)

    file=filePath+'/'+'ipRequest'
    with open(file,'wb') as f:
        for host in ip:
            for r in d[host]:
                f.write((r+'\n').encode('utf-8'))
     
    
    
    file=filePath+'/'+'cdnRequest'
    with open(file,'wb') as f:
        for host in cdn:
            for r in d[host]:
                f.write((r+'\n').encode('utf-8'))

    for host in normal:
        '''
        temp=host
        hs=host.split('.')
        if len(hs)>3:
            temp=hs[-3]+'.'+hs[-2]+'.'+hs[-1]
            '''
        file=filePath+'/'+'request'
        if not os.path.exists(file):
            os.mkdir(file)

        file=file+'/'+host
        with open(file,'wb') as f:
            for r in d[host]:
                f.write((r+'\n').encode('utf-8'))

def classByHost(hosts):
    '''
        对host进行分类
        1.ip类 
        2.cdn类
        3.正常类
    '''
    
    ip=[]
    cdn=[]
    normal=[]
    pattern=r'((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))'

    cdnlist=[]

    with open('doc/cdnlist.txt','r') as f:
        lines=f.readlines()

        for line in lines:
            line=line.strip()
            cdnlist.append(line)

    for host in hosts:
        
        '''
        t=hb[0].split('.')
        if len(t)>1:
            d=t[-2]+'.'+t[-1]
        else:
            d='##################'
        '''
        
        if re.match(pattern,host):
            ip.append(host)
        elif isCdn(host,cdnlist):
            cdn.append(host)
        else:
            normal.append(host)
    
    return ip,cdn,normal


def main():
    
    readFilePath=sys.argv[1]
    writeFilePath=sys.argv[2]


    sampleList=getSampleList(readFilePath)
    
    request=getHostAndRequest(sampleList)

    reducedRequest={}
    i=0
    for k in request.keys():
        reducedRequest[k]=[]
        for r in request[k]:
            if len(r.split(' '))>3:
                i+=1
                if i%10000==0:
                    print(r)
                    print(reduceRequest(r))
                    print(len(reduceRequest(r).split(' ')))
                
            reducedRequest[k].append(reduceRequest(r))
    print(i)
    
    ip,cdn,normal=classByHost(request.keys())

    saveRequest(reducedRequest,ip,cdn,normal,writeFilePath)
    saveHost(ip,cdn,normal,writeFilePath)
    

if __name__ == '__main__':
    main()

    
