import argparse
import os
import sys
import time

from inverted_index import Index

parser = argparse.ArgumentParser()
# parser.add_argument('--type', choices=['single-term', 'positional', 'stem','stopwords', 'phrase'], default='single-term', help='Type of index you would like to be costructed')
# parser.add_argument('--memory', type=int,default=10000, help="Memory constraints for Indexer, the default value means unlimited")
# parser.add_argument('--data_dir', type=str, default='raw_data', help='Directory for jsonl data')
# parser.add_argument('--index_dir', type=str, default='indexes', help='Directory for jsonl data')

args = sys.argv #argument array

opt={}
opt['data_dir'] = args[1]
opt['type'] = args[2]
opt['index_dir'] = args[3]
if len(args) == 5 and args[4] is not None:
    opt['memory'] = int(args[4])
else:
    opt['memory'] = 10000000

if opt['index_dir'].startswith('/'):
    opt['index_dir'] = opt['index_dir'][1:]
if opt['data_dir'].startswith('/'):
    opt['data_dir'] = opt['data_dir'][1:]

def manage_directories():
    # if not os.path.exists(opt['data_dir']):
    #     create_directory(opt['data_dir'])
    if not os.path.exists(opt['index_dir']):
        create_directory(opt['index_dir'])

def create_directory(dir):
    try:
        os.mkdir(dir)
    except OSError:
        print("Creation of the directory %s failed" % dir)
    else:
        print("Successfully created the directory %s " % dir)

def ensure_settings():
    manage_directories()
if __name__ == '__main__':
    ensure_settings()
    start_time = time.time()
    if opt['memory'] <= 100000:
        Index(opt).run_indexer()
    else:
        Index(opt).run_indexer_unlimited()
    elapsed_time = time.time() - start_time

    print('Whole time: {:.2f}'.format(elapsed_time))