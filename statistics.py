import json
import os
path = 'tmp/my-indexes/'
doc_freqs=[]
with open(path + 'lexicon.dt') as f:
    line = f.readline()
    while line:
        ent = json.loads(line)
        doc_freqs.append(ent['doc_freq'])
        line = f.readline()

def median(lst):
    sortedLst = sorted(lst)
    lstLen = len(lst)
    index = (lstLen - 1) // 2

    if (lstLen % 2):
        return sortedLst[index]
    else:
        return (sortedLst[index] + sortedLst[index + 1])/2.0



print('Count: {:,}'.format(len(doc_freqs)))
print('Size: {:,} + {:,} = {:,}'.format(os.path.getsize(path + 'lexicon.dt'), os.path.getsize(path + 'postings.pl'),
                                  float(os.path.getsize(path + 'lexicon.dt')) + float(os.path.getsize(path + 'postings.pl')) ))
print('Max: {:,}'.format(max(doc_freqs)))
print('Min: {}'.format(min(doc_freqs)))
print('Mean: {:.2f}'.format(sum(doc_freqs) / float(len(doc_freqs))))
print('Median: {}'.format(median(doc_freqs)))

