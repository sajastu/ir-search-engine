import math
import operator

from models.retrieval_model import RetrievalModel


def get_dot_product(v1, v2):
    assert len(v1) == len(v2)
    dot_product_value = 0
    for i in range(len(v1)):
        dot_product_value += v1[i] * v2[i]
    return dot_product_value


class CosineSimilarity(RetrievalModel):

    def __init__(self, queries, opt, static=True, expansion=True, qthreshold=False):
        super().__init__(queries, opt)

    def form_query_vector(self, q):
        q_vector = []
        for qterm in q.terms:
            try:
                q_vector.append(self.hits[q.title][qterm]['idf'] * q.terms.count(qterm) / len(q.terms))
            except:
                q_vector.append(0.0)
        return q_vector

    def form_doc_vector(self, doc, query):
        qterms_occurred_in_doc = []

        for q_term in self.hits[query.title]:
            if doc['doc_num'] in [p['doc_num'] for p in self.hits[query.title][q_term]['postings']]:
                qterms_occurred_in_doc.append(q_term)

        d_vector = []

        for qterm in query.terms:
            if qterm in qterms_occurred_in_doc:
                d_vector.append(self.hits[query.title][qterm]['idf'] * (doc['term_freq'] / doc['doc_len']))
            else:
                d_vector.append(0.0)
        return d_vector

    def get_cosine_similarity_list(self):
        ranked_list = {}
        for query in self.queries:
            ranked_list[query.number] = self.get_cosine_ranked_list(query)
        return ranked_list

    def get_cosine_ranked_list(self, query):
        document_scores = {}
        q_vector = self.form_query_vector(query)
        for doc in self.all_retrieved_docs[query.title]:
            d_vector = self.form_doc_vector(doc, query)
            document_scores[doc['doc_num']] = self.cosine_sim_value(d_vector, q_vector)

        return sorted(document_scores.items(), key=operator.itemgetter(1), reverse=True)

    # returns magnitude of given vector
    def compute_vector_magnitude(self, vector):
        magnitude = 0
        for item in vector:
            magnitude += math.pow(item, 2)
        return math.sqrt(magnitude)

    # returns similarity value between a document and a query vector
    def cosine_sim_value(self, doc_vector, query_vector):

        query_magnitude = self.compute_vector_magnitude(query_vector)
        doc_magnitude = self.compute_vector_magnitude(doc_vector)

        cosine_value = get_dot_product(query_vector, doc_vector) \
                       / (1.0 * query_magnitude * doc_magnitude)

        return cosine_value
