import porter
import json
import string
import math
import sys
import getopt
import os

p = porter.PorterStemmer()
stopword = set()
with open('stopwords.txt','r') as f:
    for line in f:
    	stopword.add(line.strip())

f = open('lisa.all.txt','r')
division = f.read().split('********************************************')

f1 = open('lisa.queries.txt','r')
querydiv = f1.read().split('#')

def getrelevance():
    f1 = open('lisa.relevance.txt', 'r')
    rel = f1.read().split()
    relevance = {}
    i = 0
    while (i < len(rel)):
        relevance[int(rel[i])] = rel[(i + 2):(i + 2 + int(rel[i + 1]))]
        i = i + 2 + int(rel[i + 1])
    return relevance

def getretrived():
    with open('evaluation_output.txt', 'r') as f:
        list = []
        retrived = {}
        linelist = []
        i = 0
        for line in f:
            list = line.strip().split()
            if i % 15 == 0:
                datalist = [list[1]]
                retrived[int(list[0])] = datalist
            else:
                datalist.append(list[1])
            i += 1
    return retrived

stem_freq = {}
stemmed = {}

def prepare(docum):
    dict = {}
    sum = 0
    j = 0
    for i in docum:
        list = []
        for s in i:
            if s in string.punctuation:
                i = i.replace(s, "")
        division = i.split()
        no = int(division[1])
        for str in division[2:]:
            str = str.lower()
            if str not in stopword:
                if str not in stemmed:
                    stemmed[str] = p.stem(str)
                str = stemmed[str]
                list.append(str)
        sum += len(list)
        dict[no] = list
    avg = sum/len(dict)
    return dict,avg

def preparequery(docum):
    dict = {}
    for i in docum:
        q = set()
        for s in i:
            if s in string.punctuation:
                i = i.replace(s, "")
        division = i.split()
        no = int(division[0])
        for str in division[1:]:
            str = str.lower()
            if str not in stopword:
                if str not in stemmed:
                    stemmed[str] = p.stem(str)
                str = stemmed[str]
                q.add(str)
        dict[no] = q
    return dict

def BM25(dict, avg, k, b):
    length = len(dict)
    lefts = {}
    right = {}
    for id in dict:
        left = {}
        freq = {}
        for term in dict[id]:
            if term not in freq:
                if term not in stem_freq:
                    stem_freq[term] = 1
                else:
                    stem_freq[term] += 1
                freq[term] = 1
            else:
                freq[term] += 1
        for term in freq:
            left[term] = (freq[term]*(1+k))/(freq[term]+k*((1-b)+b*len(dict[id])/avg))
        lefts[id] = left
    for term in stem_freq:
        rightvalue = math.log((length - stem_freq[term] + 0.5)/(stem_freq[term] + 0.5), 2)
        right[term] = rightvalue
    return lefts,right

def preparesimplequery(query):
    qset = set()
    for i in query:
        if i not in stopword:
            if i not in stemmed:
                stemmed[i] = p.stem(i)
            i = stemmed[i]
            qset.add(i)
    return qset

def similarity(query,docudict,right):
    scoredic = {}
    for doc in docudict:
        score = 0
        for q in query:
            if q in docudict[doc]:
                score += docudict[doc][q] * right[q]
        scoredic[doc] = score
    scoredic = sorted(scoredic.items(), key=lambda d: d[1], reverse=True)
    return scoredic

def manual_print(scoredic,query):
    print('Results for query [', end='')
    for q in query:
        if q != query[-1]:
            print(q, end=' ')
        else:
            print(q, end=']\n\n')
    i = 1
    for tuple in scoredic:
        if i <= 15:
            print(str(i)+' '+str(tuple[0])+' '+str(tuple[1]))
            i+=1
        else:
            print()
            break

def precision(retrieved,relevant):
    i=0
    for ret in retrieved:
        if ret in relevant:
            i += 1
    return i/len(retrieved)

def recall(retrieved,relevant):
    i = 0
    for ret in retrieved:
        if ret in relevant:
            i += 1
    return i/len(relevant)

def patten(retrieved,relevant):
    i = 0
    for ret in retrieved[0:10]:
        if ret in relevant:
            i += 1
    return i / 10

def rprecisionforty(retrieved,relevant):
    i = 0
    j = 0
    recall = 0
    for ret in retrieved:
        if recall >= 0.4:
            break
        if ret in relevant:
            i += 1
        recall = i/len(relevant)
        j += 1
    return i / j

def map(retrieved,relevant):
    i = 0
    j = 0
    sum = 0
    for ret in retrieved:
        j += 1
        if ret in relevant:
            i += 1
            precision = i/j
            sum += precision
    return sum/len(relevant)

def manual(lefts, right):
    active = True
    while active:
        message = input("Enter query:")
        if message == "QUIT":
            active = False
        else:
            inputquery = message.split()
            inputset = preparesimplequery(inputquery)
            simpledic = similarity(inputset, lefts, right)
            manual_print(simpledic, inputquery)

def evaluation(lefts, right):
    querydic = preparequery(querydiv[:-1])
    feva = open('evaluation_output.txt', 'a')
    for id in querydic:
        simpledic = similarity(querydic[id], lefts, right)
        i = 1
        for s in simpledic[0:15]:
            feva.write(str(id) + ' ' + str(s[0]) + ' ' + str(i) + '\n')
            i += 1
    feva.close()

def fivevalue(retrived,relevance):
    # preci = {}
    # rec = {}
    # pat = {}
    # rep = {}
    # ma = {}
    # for i in relevance:
    #     preci[i] = precision(retrived[i],relevance[i])
    #     rec[i] = recall(retrived[i],relevance[i])
    #     pat[i] = patten(retrived[i],relevance[i])
    #     rep[i] = rprecisionforty(retrived[i],relevance[i])
    #     ma[i] = map(retrived[i],relevance[i])
    # print(preci)
    # print(rec)
    # print(pat)
    # print(rep)
    # print(ma)

    # for i in relevance:
    #     print('Query '+ str(i) + ':')
    #     print('Precision: '+str(precision(retrived[i],relevance[i])))
    #     print('Recall: '+str(recall(retrived[i],relevance[i])))
    #     print('P@10: '+str(patten(retrived[i],relevance[i])))
    #     print('Rprecision0.4: '+str(rprecisionforty(retrived[i],relevance[i])))
    #     print('Map: '+str(map(retrived[i],relevance[i])))
    #     print()

    preci = 0
    rec = 0
    pat = 0
    rep = 0
    ma = 0
    for i in relevance:
        preci += precision(retrived[i],relevance[i])
        rec += recall(retrived[i],relevance[i])
        pat += patten(retrived[i],relevance[i])
        rep += rprecisionforty(retrived[i],relevance[i])
        ma += map(retrived[i],relevance[i])
    print('Precision: '+str(preci/len(relevance)))
    print('Recall: '+str(rec/len(relevance)))
    print('P@10: '+str(pat/len(relevance)))
    print('Rprecision0.4: '+str(rep/len(relevance)))
    print('Map: '+str(ma/len(relevance)))

    # ffr = open('five_result.txt', 'w')
    # for i in relevance:
    #     ffr.write('Query '+ str(i) + '\n')
    #     ffr.write('Precision: '+str(precision(retrived[i],relevance[i]))+'\n')
    #     ffr.write('Recall: '+str(recall(retrived[i],relevance[i]))+'\n')
    #     ffr.write('P@10: '+str(patten(retrived[i],relevance[i]))+'\n')
    #     ffr.write('Rprecision0.4: '+str(rprecisionforty(retrived[i],relevance[i]))+'\n')
    #     ffr.write('Map: '+str(map(retrived[i],relevance[i]))+'\n\n')
    #
    # preci = 0
    # rec = 0
    # pat = 0
    # rep = 0
    # ma = 0
    # for i in relevance:
    #     preci += precision(retrived[i], relevance[i])
    #     rec += recall(retrived[i], relevance[i])
    #     pat += patten(retrived[i], relevance[i])
    #     rep += rprecisionforty(retrived[i], relevance[i])
    #     ma += map(retrived[i], relevance[i])
    # ffr.write('Average:\n')
    # ffr.write('Precision: ' + str(preci / len(relevance))+'\n')
    # ffr.write('Recall: ' + str(rec / len(relevance))+'\n')
    # ffr.write('P@10: ' + str(pat / len(relevance))+'\n')
    # ffr.write('Rprecision0.4: ' + str(rep / len(relevance))+'\n')
    # ffr.write('Map: ' + str(ma / len(relevance))+'\n')
    # ffr.close()

def main():
    if(os.path.exists('lefts.json')):
        with open('lefts.json', 'r') as f1:
            lefts = json.load(f1)
        with open('right.json', 'r') as f2:
            right = json.load(f2)
    else:
        print('Loading BM25 index from file, please wait.')
        doc, avg = prepare(division[:-1])
        lefts, right = BM25(doc, avg, 1, 0.75)
        with open('lefts.json', 'w') as f3:
            json.dump(lefts, f3)
        with open('right.json', 'w') as f4:
            json.dump(right, f4)
    try:
        opts, args = getopt.getopt(sys.argv[1:], "m:")
    except getopt.GetoptError:
        sys.exit(-1)
    for opt, arg in opts:
        if opt in ("-m"):
            if arg == 'manual':
                manual(lefts, right)
            elif arg == 'evaluation':
                if (os.path.exists('evaluation_output.txt') == False):
                    evaluation(lefts, right)
                fivevalue(getretrived(),getrelevance())

if __name__ == '__main__':
    main()