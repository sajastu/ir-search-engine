
class PostingItem():
    def __init__(self, docID, freq, positions=None, doc_length=None):
        self.doc_num = docID
        self.freq = freq
        self.positions = positions
        self.doc_length = doc_length