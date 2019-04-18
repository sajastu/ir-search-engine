import time

from entities.query_item import Query
from models.bm25 import BM25
from models.cosine import CosineSimilarity
from models.lm import LanguageModel
from utils.text_utils import write_results
from utils.tokenizer import Tokenizer


class QueryProcessor:
    def __init__(self, opt=None, static=True):
        self.opt = opt
        self.queries = self.read_queries(static)

    def read_queries(self, static):
        queries = []
        global number, title
        with open(self.opt['query_dir'], 'r') as f:
            for line in f:
                if 'num' in line:
                    number = line.split("Number:", 1)[1].strip()
                elif 'title' in line:
                    title = line.split("Topic:", 1)[1].strip()
                    if static:
                        qterms = Tokenizer(title.lower(), self.opt['index_type']).tokenize_text()
                    else:
                        qterms = Tokenizer(title.lower(), 'single').tokenize_text()
                    q = Query(title.lower(), number, [q.lower() for q in qterms[0]])
                    if '/' in title:
                        q.split_slash()
                    queries.append(q)
        return queries

    def static_processor(self):
        results = {}

        if self.opt['retrieval_model'] == 'cosine':
            results = CosineSimilarity(self.queries, self.opt).get_cosine_similarity_list()

        elif self.opt['retrieval_model'] == 'bm25':
            results = BM25(self.queries, self.opt).get_bm25_list()

        elif self.opt['retrieval_model'] == 'lm':
            results = LanguageModel(self.queries, self.opt).get_lm_list()

        write_results(results, self.opt['result_dir'])

    # def dynamic_processor(self):
    #     results = LanguageModel(self.queries, self.opt, static=True, expansion=True).get_lm_list()
    #     write_results(results, self.opt['result_dir'])

    def query_expander(self):

        st = time.time()
        results = LanguageModel(self.queries, self.opt).get_lm_list()
        write_results(results, self.opt['result_dir'])
        en = time.time()

        print('query expansion whole: ', en - st)

    def query_threshold(self, th_val):
        results = LanguageModel(self.queries, self.opt, expansion=False, qthreshold=True).get_th_list(th_val)
        write_results(results, self.opt['result_dir'])
