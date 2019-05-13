f1 = open('lisa.relevance.txt','r')
rel = f1.read().split()
relevance = {}
i = 0
while(i<len(rel)):
    relevance[int(rel[i])] = rel[(i+2):(i+2+int(rel[i+1]))]
    i = i+2+int(rel[i+1])
print(relevance)

with open('evaluation_output.txt','r') as f:
    list = []
    retrived = {}
    linelist = []
    i = 0
    for line in f:
        list = line.strip().split()
        if i % 15 == 0:
            datalist = [list[1]]
            retrived [int(list[0])] = datalist
        else:
            datalist.append(list[1])
        i+=1


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

preci = {}
rec = {}
pat = {}
rep = {}
ma = {}
for i in relevance:
    preci[i] = precision(retrived[i],relevance[i])
    rec[i] = recall(retrived[i],relevance[i])
    pat[i] = patten(retrived[i],relevance[i])
    rep[i] = rprecisionforty(retrived[i],relevance[i])
    ma[i] = map(retrived[i],relevance[i])

print(retrived)
print(preci)
print(rec)
print(pat)
print(rep)
print(ma)