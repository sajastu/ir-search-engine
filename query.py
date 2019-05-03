import argparse
import os
import sys
import time

from inverted_index import Index
from query_processor import QueryProcessor



parser = argparse.ArgumentParser()

parser.add_argument('--expansion', action='store_true', help='query expansion')
parser.add_argument('--threshold', action='store_true', help='query thresholding.')
parser.add_argument('--position_threshold', action='store_true', help='query thresholding.')
parser.add_argument('--goodness_threshold', action='store_true', help='query thresholding.')
parser.add_argument('--index_dir', default='', help='Name of training file.')
parser.add_argument('--query_dir', default='', help='Name of training file.')
parser.add_argument('--result_dir', default='', help='Name of training file.')
parser.add_argument('--retrieval_model', default='', help='Name of training file.')
parser.add_argument('--index_type', default='', help='Name of training file.')
parser.add_argument('--threshold_value', type=int, default=0, help='')
parser.add_argument('--exp_term_threshold', required='--expansion' in sys.argv, type=int, default=0, help='')


args = parser.parse_args()

if args.threshold:
    args.expansion = False
elif args.expansion:
    args.threshold = False

opt = vars(args)

if not opt['position_threshold'] and not opt['goodness_threshold']:
    opt['position_threshold'] = True

if opt['index_dir'].startswith('/'):
    opt['index_dir'] = opt['index_dir'][1:]
if opt['result_dir'].startswith('/'):
    opt['result_dir'] = opt['result_dir'][1:]
if opt['query_dir'].startswith('/'):
    opt['query_dir'] = opt['queryfile_dir'][1:]


def manage_directories():
    if not os.path.exists(opt['index_dir']):
        create_directory(opt['index_dir'])
    if not os.path.exists(opt['result_dir']):
        create_directory(opt['result_dir'])


def create_directory(dir):
    try:
        os.makedirs(os.path.dirname(dir), exist_ok=True)
        with open(dir, "w") as f:
            f.write("initializing...")
    except OSError:
        print("Creation of the directory %s failed" % dir)
    else:
        print("Successfully created the directory %s " % dir)


def ensure_settings():
    manage_directories()


if __name__ == '__main__':
    ensure_settings()
    start_time = time.time()

    QueryProcessor(opt).static_processor()
    elapsed_time = time.time() - start_time

    print('Whole time: {:.2f}'.format(elapsed_time))
