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
        avg_query=0
        with open(self.opt['query_dir'], 'r') as f:
            for line in f:
                if 'num' in line:
                    number = line.split("Number:", 1)[1].strip()
                elif 'title' in line and not self.opt['threshold']:
                    title = line.split("Topic:", 1)[1].strip()
                    if static:
                        qterms = Tokenizer(title.lower(), self.opt['index_type']).tokenize_text()
                    else:
                        qterms = Tokenizer(title.lower(), 'single').tokenize_text()
                    q = Query(title.lower(), number, [q.lower() for q in qterms[0]])
                    if '/' in title:
                        q.split_slash()
                    queries.append(q)

                elif 'narr' in line and self.opt['threshold']:
                    line = f.readline()
                    narrative = ''
                    while '</top>' not in line:
                        narrative += line.replace('\n', '')
                        line = f.readline()
                    qterms = Tokenizer(narrative.lower().strip(), 'single').tokenize_text()
                    avg_query += len(qterms[0])
                    q = Query(narrative.lower(), number, [q.lower() for q in qterms[0]])
                    queries.append(q)
        if (self.opt['threshold']):
            print('Average Query Length before reduction: {0:.2f}'.format(avg_query/ float(len(queries))))
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
