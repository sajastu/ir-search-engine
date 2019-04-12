import math
import operator

from models.retrieval_model import RetrievalModel


class BM25(RetrievalModel):

    def __init__(self, queries, opt, static=True):
        super().__init__(queries, opt, static)
        self.queries = queries
        self.k1 = 1.2
        self.k2 = 500
        self.b = 0.75
        self.avgdl = self.get_avgdl_value()

    # returns ranked list of documents for all queries
    def get_bm25_list(self):
        ranked_list = {}
        for query in self.queries:
            ranked_list[query.number] = self.get_ranked_list(query)
        return ranked_list

    def get_ranked_list(self, query):
        document_scores = {}

        for doc in self.all_retrieved_docs[query.title]:
            final_score = 0
            for q_term in query.terms:
                n = len(self.hits[query.title][q_term])
                final_score += self.compute_bm25_score(doc, query, q_term, n)
            document_scores[doc['doc_num']] = final_score

        return sorted(document_scores.items(), key=operator.itemgetter(1), reverse=True)

    # returns k value
    def get_k_value(self, doc):
        return self.k1 * (1 - self.b + self.b * (doc['doc_len']) / self.avgdl)

    # returns average document length
    def get_avgdl_value(self):
        return self.collection_length / self.N

    def compute_bm25_score(self, doc, query, q_term, n):
        qterm_weight = math.log((self.N - n + 0.5) / (n + 0.5))
        k = self.get_k_value(doc)
        qterm_freq = query.terms.count(q_term)
        tf = self.get_tf_document(doc, query.title, q_term)
        q_term_factor = ((self.k2 + 1) * qterm_freq) / (self.k2 + qterm_freq)
        document_factor = ((self.k1 + 1) * tf) / (k + tf)

        return qterm_weight * document_factor * q_term_factor

    def get_tf_document(self, doc, q_title, q_term):
        if doc['doc_num'] in [doc['doc_num'] for doc in self.hits[q_title][q_term]['postings']]:
            return doc['term_freq']
        else:
            return 0.0