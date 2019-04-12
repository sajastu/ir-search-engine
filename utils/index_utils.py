import json
import math

from entities.posting_item import PostingItem


def write_intermediate_index(dictFile, postings_file, term, postings, type = None):
    postings_dict = {}
    postings_dict['documents'] = []
    tf_in_collection = 0
    for item in postings:
        try:
            d_entity = {}
            d_entity['doc_num'] = item.doc_num
            d_entity['term_freq'] = item.freq
            tf_in_collection += item.freq
            d_entity['doc_len'] = item.doc_length

            if item.positions is not None and len(item.positions) > 0:
                d_entity['pos'] = item.positions
            postings_dict['documents'].append(d_entity)
        except:
            print('Couldnt write posting file')

    dict_entity = {}
    dict_entity['term'] = term
    dict_entity['posting_pointer'] = postings_file.tell()
    dict_entity['idf'] = 1 + math.log(1768 / len(postings))
    dict_entity['tf_collection'] = tf_in_collection

    if tf_in_collection > 2:
        json.dump(postings_dict['documents'], postings_file)
        postings_file.write('\n')
        json.dump(dict_entity, dictFile)
        dictFile.write('\n')


# returns a tuple[ term, posting_file_pointer, [initial_blocks list] ], where initial_blocks list is decoded and in integer format
def get_next_line(dictFile, postingsFile):
    line = dictFile.readline()
    if line == '':
        return None
    lex_entity = json.loads(line)
    if len(lex_entity) == 0:
        return None
    postingsFile.seek(lex_entity['posting_pointer'])
    try:
        pls_arr = json.loads(postingsFile.readline())
    except:
        return None
    ram_pl = []
    for pl in pls_arr:
        if 'pos' in pl and len(pl['pos']) > 0:
            ram_pl.append(PostingItem(pl['doc_num'], pl['freq'], pl['pos']))
        else:
            ram_pl.append(PostingItem(pl['doc_num'], pl['freq']))

    return [lex_entity['term'], ram_pl]


def merge_rewrite_pl(dictFile, postingsFile, term, pl_a, pl_2):
    mergedPos = merge_posting_lists(pl_a, pl_2)
    numPostings = len(mergedPos)
    write_intermediate_index(dictFile, postingsFile, term, mergedPos)


def merge_posting_lists(pl_1, pl_2):
    merged_pl = []
    i = 0
    j = 0
    while i < len(pl_1) and j < len(pl_2):
        if pl_1[i].doc_num < pl_2[j].doc_num:
            merged_pl.append(pl_1[i])
            i = i + 1
        elif pl_2[j].doc_num < pl_1[i].doc_num:
            merged_pl.append(pl_2[j])
            j = j + 1
        else:
            print('Shouldnt happen, since initial_blocks are from different blocks')
            import pdb;
            pdb.set_trace()
            merged_pl.append(pl_2[j])
            j = j + 1
            i = i + 1
    while i < len(pl_1):
        merged_pl.append(pl_1[i])
        i += 1
    while j < len(pl_2):
        merged_pl.append(pl_2[j])
        j += 1
    return merged_pl
