import re


def remove_comments(text):
    return re.sub("(<!--.*?-->)", "", text)


def remove_amper(text):
    """
    :param text: unprocessed string containing body of the document
    :return: processed document with elimination of special characters from
    """
    return re.sub('&(.*?)(.;)+', '', text)


def remove_inside_tags(text):
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', text)


def remove_symbols(text):
    text = text.replace('(', '')
    text= text.replace(')', '')
    text = text.replace('"', '')
    text = text.replace("'", "")
    text = text.replace('``', '')
    text = text.replace(';', '')
    return text


def pre_process(text):
    text = remove_comments(text)
    text = remove_amper(text)
    text = remove_inside_tags(text)
    text = ' '.join(text.split())
    text = remove_symbols(text)
    return text.lower()

def write_results(results, dir):
    result_file = open(dir, 'w')
    for query_num, docs in results.items():
        i=1
        for doc in docs:
            result_file.write(query_num + ' ' + str(doc[0]) + ' ' + str(i) + ' ' + str(doc[1]) + '\n')
            i+=1

    result_file.close()
