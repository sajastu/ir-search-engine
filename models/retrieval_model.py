import json
from collections import defaultdict

from entities.query_item import Query
from utils.tokenizer import Tokenizer


class RetrievalModel:

    def __init__(self, queries, opt, static):
        """

        :param queries: an array of Query objects
        :param opt: options received by the system
        """
        self.queries = queries
        self.opt = opt

        self.N = 1768
        self.collection_length = 793262  # collection length -- calculated by running the index-side
        self.inverted_index = self.load_inverted_index()

        self.renew_queries()

        self.mu = 0.5

        # returns the hits for the queries if static
        if static:
            self.hits, self.all_retrieved_docs = self.get_hits_staticly()
        else:
            self.phrase_idx = self.load_phrase_idx()
            self.positional_idx = self.load_positional_idx()
            # self.proximity_idx = self.load_proximity_idx()
            self.hits, self.all_retrieved_docs = self.get_hits_dynamically()

    def get_hits_dynamically(self):
        hits = defaultdict(dict)

        all_docs = {}
        for q_obj in self.queries:
            if 'economies' in q_obj.terms:
                s = 0
            docs_for_q = []
            ngrams = Tokenizer(q_obj.title, 'single').extract_ngrams(2, True)
            thgrams = Tokenizer(q_obj.title, 'single').extract_ngrams(3, True)
            if len(thgrams) > 0:
                ngrams.extend(Tokenizer(q_obj.title, 'single').extract_ngrams(3))
            for ngram in ngrams:
                try:
                    q_obj_idx = self.phrase_idx[ngram]
                    if q_obj_idx['tf_collection'] >= 5:
                        pl_phrase = self.phrase_idx[ngram]
                        for qterm in ngram.split():
                            docs_for_qterm = []
                            try:
                                all_relevant_docs_for_qterm = [d['doc_num'] for d in
                                                               self.inverted_index[qterm]['postings']]
                                for doc in pl_phrase['postings']:
                                    if doc['doc_num'] in all_relevant_docs_for_qterm:
                                        docs_for_qterm.append(doc)
                                qterm_entity = {}
                                qterm_entity['term'] = qterm
                                qterm_entity['idf'] = self.inverted_index[qterm]['idf']
                                qterm_entity['tf_collection'] = self.inverted_index[qterm]['tf_collection']
                                qterm_entity['postings'] = docs_for_qterm
                                hits[q_obj.title][qterm] = qterm_entity
                            except:
                                pass

                    else:  # do proximity index
                        # hits = defaultdict(dict)
                        visited = []
                        docs_for_q = []
                        for qterm in q_obj.terms:
                            try:
                                pl_qterm = self.positional_idx[qterm]
                                hits[q_obj.title][qterm] = pl_qterm
                                for doc in pl_qterm['postings']:
                                    if doc['doc_num'] not in visited:
                                        docs_for_q.append(doc)
                                        visited.append(doc['doc_num'])
                                if q_obj.title == 'sick building syndrome':
                                    s = 2
                                all_docs[q_obj.title] = docs_for_q
                            except:
                                continue

                except:
                    pass

            # if not enough document found, then simply use single-term index
            if len(docs_for_q) <= 5:
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
        with open(self.opt['index_dir'] + 'lexicon.dt') as lex, open(self.opt['index_dir'] + 'postings.pl') as pl:
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
