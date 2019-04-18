import math
import operator
import re
import time

from entities.query_item import Query
from models.retrieval_model import RetrievalModel


# LM with Dirichlet smoothing
def merge_lists(init_docs, et_doc_scores):
    result = {}
    for L in init_docs, et_doc_scores:
        for key, value in L:
            result[key] = result.get(key, 0) + value

    return list(result.items())


class LanguageModel(RetrievalModel):
    def __init__(self, queries, opt, mu=0.5, static=True, expansion=True, qthreshold=False):
        super().__init__(queries, opt, static, expansion, qthreshold)
        self.mu = mu
        self.expansion = expansion

    def get_lm_list(self):
        ranked_list = {}
        for query in self.queries:
            ranked_list[query.number] = self.get_lm_ranked_list(query)
        return ranked_list

    def get_lm_ranked_list(self, query):
        document_scores = {}

        for doc in self.all_retrieved_docs[query.title]:
            final_score = 0
            for q_term in query.terms:
                final_score += self.compute_lm_score(doc, q_term, query .title)
            document_scores[doc['doc_num']] = final_score
        return sorted(document_scores.items(), key=operator.itemgetter(1), reverse=True)

    def compute_lm_score(self, doc, q_term, q_title):
        global numerator, denominator
        numerator = self.get_tf_document(doc, q_title, q_term) + (
                self.mu * self.inverted_index[q_term]['tf_collection'] / self.collection_length)
        denominator = doc['doc_len'] + self.mu
        return math.log(numerator / denominator)

    def get_tf_document(self, doc, q_title, q_term):
        try:
            if doc['doc_num'] in [doc['doc_num'] for doc in self.hits[q_title][q_term]['postings']]:
                return doc['term_freq']
            else:
                return 0.0
        except KeyError:
            print('Key Error!!')

    # def get_lm_expanded_list(self):
    #     ranked_list = {}
    #     for query in self.queries:
    #         ranked_list[query.number] = self.get_lm_expanded_ranked_list(query)
    #     return ranked_list
    #
    # def get_lm_expanded_ranked_list(self, query, word_th=1):
    #     start_time = time.time()
    #     expanded_terms = self.identify_expanded_terms(query, word_th)
    #     end = time.time()
    #     print('query: ', query.number)
    #     print('time for expansion:', end-start_time)
    #     init_docs = self.get_lm_ranked_list(query)
    #     for et in expanded_terms:
    #         et_doc_scores = LanguageModel([Query(et[0], 00, [et[0]])], self.opt, static=True, expansion=False)\
    #             .get_lm_ranked_list(Query(et[0], 00, [et[0]]))
    #         init_docs = merge_lists(init_docs, et_doc_scores)
    #     init_docs.sort(key=operator.itemgetter(1), reverse=True)
    #     return init_docs
    #


    # def get_similarity_score(self, t1, t2):
    #     if self.sim == 'jaccard':
    #         return self.jaccard_similarity(t1, t2)
    #
    #
    # def jaccard_similarity(self, t1, t2):
    #     try:
    #         t1_docs = [doc['doc_num'] for doc in self.inverted_index[t1]['postings']]
    #     except KeyError:
    #         t1_docs = {}
    #     try:
    #         t2_docs = [doc['doc_num'] for doc in self.inverted_index[t2]['postings']]
    #     except KeyError:
    #         t2_docs={}
    #
    #     intersection = len(list(set(t1_docs) & set(t2_docs)))
    #     union = len(set.union(*[set(t1_docs), set(t1_docs)]))
    #     return intersection / float(union)


def number_match(string):
    pattern = re.compile("^[^0-9]+$")
    return pattern.match(string)