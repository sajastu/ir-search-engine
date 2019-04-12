import datetime
import re

from nltk.stem import PorterStemmer

from utils import regex_patterns as rp
from utils.single_token import Token


def get_normalized_date(res):
    out = ''
    if ', ' in res:
        dt = datetime.strptime(res, '%B %d, %Y')
        out = dt.month + '-' + dt.day + '-' + dt.year
        if len(out) == 0:
            dt = datetime.strptime(res, '%b %d, %Y')
            out = dt.month + '-' + dt.day + '-' + dt.year
    else:
        dt = datetime.strptime(res, '%m/%d/%Y')
        out = dt.month + '-' + dt.day + '-' + dt.year
        if len(out) == 0:
            dt = datetime.strptime(res, '%b-%d-%Y')
            out = dt.month + '-' + dt.day + '-' + dt.year
    if len(out) > 0:
        return out
    else:
        return res


class Tokenizer:

    def __init__(self, text, index_type):
        self.tokens =[]
        self.text = text
        self.type = index_type
        self.positions = []
        self.found_patterns = set()

    def tokenize_text(self):

        if self.type == 'single':
            self.single_term_index()
            return self.tokens, []

        elif self.type == 'stem':
            self.single_term_index()
            return self.stemmer(), []

        elif self.type == 'phrase':
            return self.ngrams(), []

        if self.is_positional():
            self.single_term_index()
            return self.tokens, self.positions

    def single_term_index(self):
        self.date_extractor()
        self.file_extensions()
        self.email_extractor()
        self.ip_extractor()
        self.url_extractor()
        self.hyphen_extractor()
        self.abbr_extractor()
        self.currency_extractor()
        self.digit_normalizer()
        modified_text = self.remove_res().replace(',','').strip()
        # if self.is_positional():
        self.set_position_and_tokens(modified_text)
        self.other_preprocessings()
        # return self.tokens
        self.remove_sw()

    def date_extractor(self):
        self.extract_patterns_general(rp.DATE_1, normalized_date=True)
        self.extract_patterns_general(rp.DATE_2, normalized_date=True)

    def file_extensions(self):
        result = re.finditer(rp.EXTENSION_1, self.text)
        for m in result:
            self.fill_found_patterns(rp.EXTENSION_1)
            parts = m.group(0).rsplit('.', 1)
            self.tokens.append(parts[1])

            if self.is_positional():
                self.positions.append('{} : {}'.format(m.start(), len(m.group(0))))


    def email_extractor(self):
        self.extract_patterns_general(rp.EMAIL)


    def ip_extractor(self):
        self.extract_patterns_general(rp.IP_ADDRESS)


    def url_extractor(self):
        self.extract_patterns_general(rp.URL)


    def hyphen_extractor(self):

        result = re.finditer(rp.HYPHEN, self.text)
        result
        for m in result:
            self.fill_found_patterns(rp.HYPHEN)
            parts = m.group(0).split('-')
            if parts[0] not in rp.COMMON_PREFIXES:
                self.tokens.extend([parts[0], parts[1], parts[0]+''+parts[1]])
                if self.is_positional():
                    self.positions += ['{} : {}'.format(m.start(), len(parts[0])),
                                       '{} : {}'.format(m.start(), len(parts[1])),
                                       '{} : {}'.format(m.start(), len(parts[0] + '' + parts[1]))]

            else:
                if parts[0] == 'ready':
                    s2=2
                self.tokens.extend([parts[1], parts[0] + '' + parts[1]])
                if self.is_positional():
                    self.positions += ['{} : {}'.format(m.start(), len(parts[1])),
                                       '{} : {}'.format(m.start(), len(parts[0] + '' + parts[1]))]


    def abbr_extractor(self):

        result = re.finditer(rp.ABBREVATION, self.text)
        for m in result:
            self.fill_found_patterns(rp.ABBREVATION)

            self.tokens.append(m.group(0).replace('.', ''))

            if self.is_positional():
                self.positions.append('{} : {}'.format(m.start(), len(m.group(0))))



    def digit_normalizer(self):
        result = re.finditer(rp.NUMBERS_COMMA_REQ, self.text)
        for m in result:
            self.fill_found_patterns(rp.NUMBERS_COMMA_REQ)
            self.tokens.append(m.group(0).replace(',',''))
            if self.is_positional():
                self.positions.append('{} : {}'.format(m.start(), len(m.group(0))))

    def currency_extractor(self):
        self.extract_patterns_general(rp.CURRENCY)

    def stemmer(self):
        stemmed = []
        ps = PorterStemmer()
        for t in self.tokens:
            stemmed.append(ps.stem(t))
        return stemmed

    def remove_sw(self):
        sws = []
        processed = []
        with open('stopwords/stops.txt', 'r') as stops:
            line = stops.readline()
            while line:
                sws.append(line.replace('\n',''))
                line = stops.readline()
        for t in self.tokens:
            if t not in sws:
                processed.append(t)
        self.tokens.clear()
        self.tokens = processed

    def ngrams(self):
        ngrams = self.extract_ngrams(2)
        ngrams.extend(self.extract_ngrams(3))
        return ngrams

    # def extract_ngrams(self, n):
    #     ans = []
    #     arr = self.text.split()
    #     length = len(arr) - 1
    #     if n == 3:
    #         length = len(arr) - 2
    #     for i in range(length):
    #         if n == 2:
    #             ans.append(str(arr[i]) + ' ' + str(arr[i + 1]).strip())
    #         elif n==3:
    #             ans.append(str(arr[i]) + ' ' + str(arr[i + 1]) + ' ' + str(arr[i + 2]).strip())
    #
    #     return ans

    def extract_ngrams(self, n, sw=False):
        if sw:
            self.remove_sw()
        s = self.text.lower()
        s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)

        tokens = [token for token in s.split(" ") if token != ""]
        ngrams = zip(*[tokens[i:] for i in range(n)])
        return [" ".join(ngram) for ngram in ngrams]

    def extract_text_ngrams(self, text, n):
        s = text.lower()
        s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)

        tokens = [token for token in s.split(" ") if token != ""]
        ngrams = zip(*[tokens[i:] for i in range(n)])
        return [" ".join(ngram) for ngram in ngrams]

    def remove_res(self):
        if len(self.found_patterns) > 0:
            self.found_patterns = list(self.found_patterns)
            modified_text=''
            for ptn in self.found_patterns:
                modified_text = re.sub(ptn, '', self.text)
            return modified_text
        return self.text

    def fill_found_patterns(self, pattern):
        self.found_patterns.add(pattern)

    def extract_patterns_general(self, ptn, normalized_date=False):
        result = re.finditer(ptn, self.text)
        for m in result:
            self.fill_found_patterns(ptn)
            if normalized_date:
                self.tokens.append(get_normalized_date(m.group(0)))
            else:
                self.tokens.append(m.group(0))

            if self.is_positional():
                self.positions.append('{} : {}'.format(m.start(), len(m.group(0))))

    def is_positional(self):
        return self.type == 'positional'

    def set_position_and_tokens(self, modified_text):
        i=0
        for m in modified_text.split():
            pos = self.text.find(m, i)
            if self.is_positional(): self.positions.append('{} : {}'.format(str(pos), len(m)))
            i = + pos + len(m)
            self.tokens.append(m)

    def other_preprocessings(self):
        for i, t in enumerate(self.tokens):
            if 'new' in t:
                s=0
            if t.endswith('.'):
                self.tokens[i] = t.replace('.', '')
            if t.startswith('_'):
                self.tokens[i] = t.replace('_', '')
            if t.endswith('_'):
                self.tokens[i] = t.replace('_', '')
            if t.endswith('-'):
                self.tokens[i] = t.replace('-', '')
            if t.startswith('-'):
                self.tokens[i] = t.replace('-', '')
            if t.startswith('('):
                self.tokens[i] = t.replace('(', '').replace(')','')
            if t.startswith('['):
                self.tokens[i] = t.replace('[', '').replace(']','')

