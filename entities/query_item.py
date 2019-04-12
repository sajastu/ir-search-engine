class Query():
    def __init__(self, title, number, terms):
        self.title = title
        self.number = number
        self.terms = terms

    def split_slash(self):
        new_terms = []
        for t in self.terms:
            if '/' in t:
                slashed_terms = t.split('/')
                new_terms.extend(slashed_terms)
            else:
                new_terms.append(t)
        self.terms = new_terms

    def remove_paranthese(self):
        new_terms = []
        for t in self.terms:
            if '(' in t:
                t = t.replace('(', '').replace(')', '')
                new_terms.append(t)
            else:
                new_terms.append(t)
        self.terms = new_terms