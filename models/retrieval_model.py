import json
import operator
import pickle
import time
from collections import defaultdict

from entities.query_item import Query


class RetrievalModel:

    def __init__(self, queries, opt):
        """

        :param queries: an array of Query objects
        :param opt: options received by the system
        """
        self.q_smooth = 0.01
        self.queries = queries
        self.opt = opt

        self.N = 1768
        self.collection_length = 793262  # collection length -- calculated by running the index-side
        self.inverted_index = self.load_inverted_index()

        self.renew_queries()

        self.mu = 0.5

        if opt['threshold']:
            self.reduce_queries(opt['threshold_value'])
            self.calculate_avg_length()

        self.hits, self.all_retrieved_docs = self.get_hits_staticly()
        if opt['expansion'] and opt['exp_term_threshold'] > 0:
            self.doc_tokens = self.load_doc_tokens()
            self.expand_queries(opt['exp_term_threshold'])
            self.hits, self.all_retrieved_docs = self.get_hits_staticly()

    # returns hits for a given query (static)
    def get_hits_staticly(self):
        hits = defaultdict(dict)
        all_docs = {}
        for q_obj in self.queries:
            visited = []
            docs_for_q = []
            for qterm in q_obj.terms:
                try:
                    pl_qterm = self.inverted_index[qterm]
                except:
                    continue
                hits[q_obj.title][qterm] = pl_qterm
                for doc in pl_qterm['postings']:
                    if doc['doc_num'] not in visited:
                        docs_for_q.append(doc)
                        visited.append(doc['doc_num'])
            all_docs[q_obj.title] = docs_for_q
        return hits, all_docs

    # load inverted index into the memory
    def load_inverted_index(self):
        inverted_index = {}
        with open(self.opt['index_dir'] + '-' + self.opt['index_type'] + '/lexicon.dt') as lex, open(
                self.opt['index_dir'] + '-' + self.opt['index_type'] + '/postings.pl') as pl:
            for x, y in zip(lex, pl):
                x = x.strip()
                y = y.strip()
                lex = json.loads(x)
                pls = json.loads(y)

                dict_sample = {}
                dict_sample['term'] = lex['term']
                dict_sample['idf'] = lex['idf']
                dict_sample['tf_collection'] = lex['tf_collection']
                dict_sample['postings'] = pls

                inverted_index[lex['term']] = dict_sample

                # inverted_index.append(lex)
        return inverted_index

    def renew_queries(self):
        for i, q in enumerate(self.queries):
            after_terms = []
            for t in q.terms:
                if t in self.inverted_index.keys():
                    after_terms.append(t)
            self.queries[i] = Query(q.title, q.number, after_terms)

    def load_phrase_idx(self):
        phrase_idx = {}
        if self.opt['index_dir'][-1] == '/':
            idx_dir = self.opt['index_dir'][:-1]
        with open(idx_dir + '-phrase/lexicon.dt') as lex, open(idx_dir + '-phrase/postings.pl') as pl:
            for x, y in zip(lex, pl):
                x = x.strip()
                y = y.strip()
                lex = json.loads(x)
                pls = json.loads(y)

                dict_sample = {}
                dict_sample['term'] = lex['term']
                dict_sample['idf'] = lex['idf']
                dict_sample['tf_collection'] = lex['tf_collection']
                dict_sample['postings'] = pls

                phrase_idx[lex['term']] = dict_sample

        return phrase_idx

    def load_positional_idx(self):
        phrase_idx = {}
        if self.opt['index_dir'][-1] == '/':
            idx_dir = self.opt['index_dir'][:-1]
        with open(idx_dir + '-positional/lexicon.dt') as lex, open(idx_dir + '-positional/postings.pl') as pl:
            for x, y in zip(lex, pl):
                x = x.strip()
                y = y.strip()
                lex = json.loads(x)
                pls = json.loads(y)

                dict_sample = {}
                dict_sample['term'] = lex['term']
                dict_sample['idf'] = lex['idf']
                dict_sample['tf_collection'] = lex['tf_collection']
                dict_sample['postings'] = pls

                phrase_idx[lex['term']] = dict_sample

                # phrase_idx.append(lex)
        return phrase_idx

    def load_proximity_idx(self):
        pass

    def load_doc_tokens(self):
        return pickle.load(open('tmp/dict', "rb"))

    def expand_queries(self, word_th):
        term_scores = {}
        for i, query in enumerate(self.queries):
            for doc in self.all_retrieved_docs[query.title]:
                for doc_term in self.doc_tokens[doc['doc_num']]:

                    start = time.time()
                    dterm_prob = self.doc_tokens[doc['doc_num']].count(doc_term) / doc['doc_len']
                    end1 = time.time()
                    e1 = end1 - start
                    # print()

                    query_factor = 1

                    start = time.time()
                    for query_term in query.terms:
                        query_factor *= (self.doc_tokens[doc['doc_num']].count(query_term) + self.q_smooth) / doc[
                            'doc_len']

                    if doc_term not in term_scores.keys():
                        term_scores[doc_term] = dterm_prob * query_factor
                    else:
                        term_scores[doc_term] += dterm_prob * query_factor

                    for query_term in query.terms:
                        if query_term in term_scores.keys(): del term_scores[query_term]

                    if len(term_scores) > 5000:
                        break
            expanded_terms_query = sorted(term_scores.items(), key=operator.itemgetter(1), reverse=True)[:word_th]
            expanded_terms = [e[0] for e in expanded_terms_query]
            self.queries[i] = Query(query.title + ' ' + ' '.join(expanded_terms),
                                    query.number, query.terms + expanded_terms)

    def reduce_queries(self, bound):
        if self.opt['position_threshold']:
            for i, query in enumerate(self.queries):
                should_remain = int(round(len(query.terms) * (1.0 - (bound / 100.0))))
                title = ' '.join(query.terms[:should_remain])
                self.queries[i] = Query(title, query.number, query.terms[:should_remain])
        elif self.opt['goodness_threshold']:
            for i, query in enumerate(self.queries):
                idf_list = []
                for term in query.terms:
                    idf_list.append(self.inverted_index[term]['idf'])
                terms_idf = dict(zip(query.terms, idf_list))
                should_removed = int(round(len(query.terms) * ((bound / 100.0))))
                if should_removed > 0 and should_removed < len(query.terms):
                    remained_terms = remaining(query.terms, idf_list, should_removed)
                else:
                    remained_terms = terms_idf.keys()

                title = ' '.join(remained_terms)
                self.queries[i] = Query(title, query.number, remained_terms)

    def calculate_avg_length(self):
        avg_len = 0
        for q in self.queries:
            avg_len += len(q.terms)
        print('Length after reduction: {0:.2f}'.format(avg_len / float(len(self.queries))))


def remaining(term_list, idf_list, smallest_n=0):
    for _ in range(smallest_n):
        m = min(idf_list)
        idx = idf_list.index(m)
        del term_list[idx]
        del idf_list[idx]
    return term_list
