import os

class Classifier(object):
    
    def __init__(self,signaturePath):
        self.path=signaturePath
        self.signatures=os.listdir(self.path)

    def getSig(self,host):
        sig=[]
        if host in self.signatures:
            file=self.path + '/' + host
            with open(file,'r') as f:
                lines=f.readlines()
                for line in lines:
                    line = line.strip()
                    sig.append(line)
        
        return sig

            
