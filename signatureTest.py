import re
import sys
import numpy as np

from pprint import pprint


def GetLCS(str1, str2):
    '''
            Given two strings, returns the longest common substring.
    '''
    str1Len = len(str1)
    str2Len = len(str2)
    compares = 0

    # If one of the input is None, there is no common part between them.
    if str1Len == 0 or str2Len == 0:
        return -1

    # Create a matrix to record the substring
    m = np.zeros([str1Len, str2Len], dtype=np.int)

    for j in range(str2Len):
        compares += 1
        m[0][j] = 1 if str1[0] == str2[j] else 0

    for i in range(1, str1Len):
        compares += 1
        m[i][0] = 1 if str1[i] == str2[0] else 0

        for j in range(1, str2Len):
            compares += 1
            m[i][j] = m[i - 1][j - 1] + 1 if str1[i] == str2[j] else 0

    # Find the biggest number of the matrix
    lcsLen = 0
    startPos1 = -1
    # startPos2 = -1
    for i in range(str1Len):
        for j in range(str2Len):
            if lcsLen < m[i][j]:
                lcsLen = m[i][j]
                startPos1 = i - lcsLen + 1
                #startPos2 = j - lcsLen + 1

    # Longest common substring
    lcs = str1[startPos1: startPos1 + lcsLen]

    # return [lcs , lcsLen , startPos1 , startPos2 , compares]
    return lcs


def GetCommonList(str1, str2, csList):
    '''
            Given two strings, get the common substrings between them recursively.
            Storage the common substrings in the csList.
    '''
    if len(str1) < 2 or len(str2) < 2:
        return

    lcs = GetLCS(str1, str2)
    if lcs == '' or len(lcs) < 2:
        return

    # Split str1 and str2.
    splitList1 = str1.split(lcs)
    splitList2 = str2.split(lcs)

    # Recursive.
    GetCommonList(splitList1[0], splitList2[0], csList)
    csList.append(lcs)
    GetCommonList(splitList1[1], splitList2[1], csList)


def GetTokenList(sampleList):
    '''
            Given the sample list, extract the tokens pairwise.
            Storage the tokens in the tokenList.
    '''
    commonList = []
    for i in range(len(sampleList)):
        sample1 = sampleList[i]
        for j in range(i + 1, len(sampleList)):
            sample2 = sampleList[j]
            tempList = []
            GetCommonList(sample1, sample2, tempList)
            commonList.append(tempList)

    # Make sure that every token exists in every sample.
    tokenList = []
    for tokens in commonList:
        for token in tokens:
            num = 0
            for sample in sampleList:
                if token in sample:
                    num += 1
            if num == len(sampleList):
                tokenList.append(token)

    # Distinct
    tokenList = list(set(tokenList))

    # Reversely sort the tokens by the length of them.
    tokenList.sort(key=lambda x: len(x), reverse=1)

    # Prune out the fake tokens that exists in other tokens
    i = len(tokenList) - 1
    while i >= 0:
        j = i - 1
        while j >= 0:
            if tokenList[i] in tokenList[j]:
                tokenList.remove(tokenList[i])
                break
            j -= 1
        i -= 1

    # Sort the tokens by the order of appearance in the sample.
    orderedList = []
    for token in tokenList:
        index = sampleList[0].find(token)
        orderedList.append((token, index))
    orderedList.sort(key=lambda x: x[1])
    tokenList = [i[0] for i in orderedList]

    return tokenList


def GetSignature(tokenList):
    '''
            Given the token list, generate and return the signature consists of these tokens.
    '''
    signatureStr = ''
    wildcard = '(.*)?'

    for token in tokenList:
        signatureStr += wildcard
        signatureStr += '('
        signatureStr += re.escape(token)
        signatureStr += ')'
    signatureStr += wildcard

    return signatureStr



sampleList = [  
                'GET /o/ajax/log/?page=simple&fromcase=50xyz001&type=1&id=748&appid=52472048&apkid=66553501&chanabnelId=&r=0.5336161153480674 HTTP/1.1',
                'GET /o/ajax/log/?callValue=||865626ab035149497||||4600782xyz66535578|||720|1280|OPPO|OPPO HTTP/1.1',
                'GET /o/ajax/log/?page=simple&fromcase=500xyz01&type=1&id=744&appid=52472048&apkid=66553501&channabelId=&r=0.07101931124494154 HTTP/1.1'
            ]
tokenList = GetTokenList(sampleList)
pprint(tokenList)
print('---------------------------------------------------------------!')
signature = GetSignature(tokenList)
print(signature)

m = re.match(signature, 'GET /o/ajax/log/?callValue=||865626ab035149497||||4600782xyz66535578|||720|1280|OPPO|OPPO HTTP/1.1')
if m:
    print('OK')
else:
    print('NO')

