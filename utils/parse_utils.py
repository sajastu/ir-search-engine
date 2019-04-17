import re

from utils.text_utils import pre_process
from utils.tokenizer import Tokenizer


def parse_document(document, type='single'):
    document = document.replace('\r', '').replace('\n','')
    doc_num = str(re.search('<DOCNO>(.*?)</DOCNO>', document).groups(1)).replace('(\'', '').replace('\',)','').strip()
    doc_body = str(re.search('<TEXT>(.*?)</TEXT>', document).groups(1))
    processed_doc = pre_process(doc_body)
    tokens, positions = Tokenizer(processed_doc, type).tokenize_text()
    doc_len = len(tokens)
    return doc_num, tokens, positions, doc_len