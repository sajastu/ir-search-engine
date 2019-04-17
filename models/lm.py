import math
import operator

from models.retrieval_model import RetrievalModel


# LM with Dirichlet smoothing
class LanguageModel(RetrievalModel):
    def __init__(self, queries, opt, mu=0.5, static=True, expansion=True, sim='jaccard'):
        super().__init__(queries, opt, static, expansion, sim)
        self.mu = mu

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
        if doc['doc_num'] in [doc['doc_num'] for doc in self.hits[q_title][q_term]['postings']]:
            return doc['term_freq']
        else:
            return 0.0

    def get_expanded_list(self):
        ranked_list = {}
        for query in self.queries:
            ranked_list[query.number] = self.get_lm_expanded_ranked_list(query)
        return ranked_list

    def get_lm_expanded_ranked_list(self, query, word_th=100):
        document_scores = {}
        expanded_terms = self.identify_expanded_terms(query, word_th)

        final_score = 0
        for q_term in query.terms:
            final_score += self.compute_lm_score(doc, q_term, query.title)
        document_scores[doc['doc_num']] = final_score

        return sorted(document_scores.items(), key=operator.itemgetter(1), reverse=True)

    # sort words based on jaccard similarity
    def identify_expanded_terms(self, query, word_th):
        term_scores = {}
        for t in query.terms:
            for doc in self.all_retrieved_docs[query.title]:
                for doc_term in self.doc_tokens[doc]:
                    if doc_term not in term_scores.keys():
                        term_scores[doc_term] = self.get_similarity_score(t, doc_term)



        return sorted(term_scores.items(), key=operator.itemgetter(1), reverse=True)[:word_th]

    def get_similarity_score(self, t1, t2):
        if self.sim == 'jaccard':
            return self.jaccard_similarity(t1, t2)


    def jaccard_similarity(self, t1, t2):
        intersection = self.inverted_index
        union = len(set.union(*[set(x), set(y)]))
        return intersection / float(union)