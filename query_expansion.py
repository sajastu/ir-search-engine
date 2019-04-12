from query_processor import QueryProcessor


class QueryExpansion:

    def __init__(self, opt):
        QueryProcessor(opt).query_expander()
