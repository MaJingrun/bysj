from pprint import pprint

import scipy.cluster.hierarchy as sch
import numpy as np

import Levenshtein
import os
import re
import csv


'''
	Return the jaccard distance between two lists. 
	J(A , B) = 1 - |(A & B)| / |(A | B)|
'''


def JaccardDistance(listA, listB):
    distance = 0

    intersection = set(listA) & set(listB)
    union = set(listA) | set(listB)

    if len(union) == 0:
        distance = 0
    else:
        distance = 1 - len(intersection) / float(len(union))

    return distance


'''
	Return the normalized edit distance between two string. 
'''


def EditDistance(strA, strB):
    distance = Levenshtein.distance(strA,strB)

    if distance == 0:
        normalizedDistance = 0
    else:
        normalizedDistance = distance / float(max(len(strA), len(strB)))

    return normalizedDistance


'''
	Return the distance between two request methods. 
	The distance is 1 if such two methods are equal, 0 otherwise.
'''


def MethodDistance(strA, strB):
    return 1 - int(strA == strB)


'''
	Return the overall distance between two http requests.
	The input format is: [str , str , list , str]
	overallDistance = w0 * d0 + w1 * d1 + w2 * d2 + w3 * d3
'''


def OverallDistance(sampleA, sampleB):
    distance = 0

    d0 = MethodDistance(sampleA[0], sampleB[0])
    d1 = EditDistance(sampleA[1], sampleB[1])
    d2 = JaccardDistance(sampleA[2], sampleB[2])
    d3 = EditDistance(sampleA[3], sampleB[3])
    '''
    w0 = 0.455
    w1 = 0.365
    w2 = 0.135
    w3 = 0.045
    '''
    w0 = 10
    w1 = 8
    w2 = 3
    w3 = 1
    distance = w0 * d0 + w1 * d1 + w2 * d2 + w3 * d3

    return distance


'''
	Given a list of samples, like [sampleA , sampleB , ... , sampleZ], 
	and the format of sample is [feature1 , feature2 , feature3 , feature4].
	Return a distance metrix which is only represented in the format of triangular.
'''


def GetDistanceMatrix(sampleList):
    distanceMatrix = []

    for i in range(len(sampleList)):
        for j in range(i + 1, len(sampleList)):
            distance = OverallDistance(sampleList[i], sampleList[j])
            distanceMatrix.append(distance)

    return distanceMatrix


'''
	Parse the HTTP request.
	Return a list, which consists of 4 elements represent require method, page, parameter names and parameter values, respectively.
'''


def Parse(request):
    featureList = []

    requestMethod = ''
    requestPage = ''
    parameterNames = []
    parameterValues = ''

    splitBlank = request.split(' ')
    requestMethod = splitBlank[0]							# Get the request method field
    # Aim at some POST request which path field is started with 'http:/'
    requestPath = splitBlank[1].replace('http:/', '')
    # Remove the '\n' from the protocol field, but this field seemingly not useful in the paper
    # requestProtocol = splitBlank[2].rstrip('\n')

    featureList.append(requestMethod)

    if '?' in requestPath:
        splitQuestionMark = requestPath.split('?')
        requestPage = splitQuestionMark[0]
        requestParameters = splitQuestionMark[1]

        featureList.append(requestPage)

        splitParameters = requestParameters.split('&')
        for parameter in splitParameters:
            if parameter != '':
                if '=' in parameter:
                    temp = parameter.split('=')
                    parameterNames.append(temp[0])
                    parameterValues += temp[1]
                else:
                    parameterNames.append(parameter)
    else:
        featureList.append(requestPath)

    featureList.append(parameterNames)
    featureList.append(parameterValues)

    return featureList


'''
	There are some files which have only '\n' in there request field.
	So we use the regular expression to filter these noises.

	Some files have more than one http record.
	So we should return a list, which elements are also lists.
'''


def GetHttpRequest(file):
    requestList = []
    with open(file, 'r', encoding='utf-8') as f:
        record = f.readlines()
        # OPTIONS , GET , POST , HEAD, PUT , DELETE , TRACE
        expression = r'^(OPTIONS|GET|POST|HEAD|PUT|TRACE)'
        # if not re.match(expression, record[0]):
        # 	print '---------------------------------'
        # 	print file
        # 	pprint(record)
        for temp in record:
            if re.match(expression, temp):
                # Append the string to the list if such string match the RE.
                requestList.append(temp)
    return requestList


'''
	Given the direction name, get the files in this below this direction. 
'''


def GetFile(dirPrefix):
    absDir = os.path.abspath(dirPrefix)
    fileNameList = os.listdir(absDir)
    return fileNameList


'''
	Given the a sample and its belonging cluster, distribute such sample into corresponding file.
'''


def Save(originalRequest, clusterNum):
    fileName = 'fineClusterResult/'
    fileName += str(clusterNum)

    # addInfo = [originalRequest , clusterNum]
    # addInfo = [originalRequest]
    # print(addInfo)

    # csvFile = open(fileName , 'a')

    # writer = csv.writer(csvFile)
    # writer.writerow(addInfo)

    # csvFile.close()

    with open(fileName, 'ab') as f:
        addInfo = originalRequest + '\n'
        x=addInfo.encode('utf-8')
        f.write(x)


'''
	Given the cluster, plot the dendrogram.
'''

'''
def Plot(Z):
    plt.figure(figsize=(25, 10))
    plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel('sample index')
    plt.ylabel('distance')

    sch.dendrogram(Z, leaf_rotation=90, leaf_font_size=8)
    plt.show()
'''


def main():
    dirPrefix = os.path.abspath('subSamples')
    fileNameList = GetFile(dirPrefix)

    sampleList = []
    originalRequestList = []

    # Get the requests from the files.
    for fileName in fileNameList:
        filePath = os.path.join('%s/%s' % (dirPrefix, fileName))
        requestList = GetHttpRequest(filePath)
        for request in requestList:
            sample = Parse(request)
            originalRequestList.append(request.rstrip('\n'))
            # Append the parsed request to the sample list.
            sampleList.append(sample)
            # print(len(sampleList) - 1 , request.rstrip('\n'))

    # Get the distance matrix of these requests.
    distanceMatrix = GetDistanceMatrix(sampleList)

    distanceArray = np.array(distanceMatrix)

    # Put the distance matrix to the clustering function.
    encodedCluster = sch.linkage(distanceArray, method='single')

    # Flat the cluster result.
    flatCluster = sch.fcluster(
        encodedCluster, t=1, criterion='inconsistent')
    print(len(originalRequestList), len(flatCluster))

    # Save the cluster result.
    for i in range(len(originalRequestList)):
        Save(originalRequestList[i], flatCluster[i])

    # # Plot the dendrogram.
    # Plot(encodedCluster)

    # sampleList = []
    # a = ['GET', '/service/api2.php', ['qt', 'tt'], '15061440440472992']
    # b = ['POST', '/short.weixin.qq.com/cgi-bin/micromsg-bin/getcdndns', [], '']
    # c = ['POST', '/app_logs', [], '']
    # d = ['GET', '/infonew/0/news_pics_124163258.jpg/220', [], '']
    # e = ['GET', '/rtmonitor.kugou.com/Mobile/MobileStat.aspx', ['ver', 'md5', 'state', 'imei', 'uid', 'type', 'net', 'os', 'para', 'ftype'], '7610ed9fb556109ebd7b4451a95afd58a773172353603208649888684245209702331011']
    # sampleList = [a,b,c,d,e]

    # # distanceMatrix = GetDistanceMatrix(sampleList)
    # sampleArray = np.array(sampleList , dtype = object)
    # disMat = sch.distance.pdist(sampleArray , OverallDistance)
    # print disMat
    # # print distanceMatrix
    # # print len(sampleList) , len(distanceMatrix)



