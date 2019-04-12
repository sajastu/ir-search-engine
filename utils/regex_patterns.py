"""
Some regex patterns

"""

DATE_1 = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)+\s\d\d,\s\d{4}'
DATE_2 = r'(\d{2}(/|-)\d{2}(/|-)\d{4})'

EXTENSION_1= r'[aA-zZ]+\.(?:(?:[dD][oO][cC][xX]?)|(?:[pP][dD][fF]))'

IP_ADDRESS = r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'

URL = r'^(http[s]?:\\/\\/(www\\.)?|ftp:\\/\\/(www\\.)?|www\\.){1}([0-9A-Za-z-\\.@:%_\+~#=]+)+((\\.[a-zA-Z]{2,3})+)(/(.)*)?(\\?(.)*)?'

EMAIL = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

HYPHEN = r'[a-zA-Z]+\-+[a-zA-Z]+'

ABBREVATION = r'[a-zA-Z]+\.+[a-zA-Z]+\.?[a-zA-Z]?\.?'

NUMBERS_COMMA_REQ = r'(?!,\S)\b(\d{1,3}(?:,\d{3})*)\b(?!,)'

CURRENCY = r'\$\d+(?:\.\d+)?'

COMMON_PREFIXES = ['pre', 'pro', 'post', 're', 'tri', 'anti', 'non', 'mono', 'micro', 'intro', 'intra', 'inter', 'in', 'hyper']