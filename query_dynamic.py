import argparse
import os
import sys
import time

from inverted_index import Index
from query_processor import QueryProcessor

parser = argparse.ArgumentParser()

args = sys.argv  # argument array

opt = {}
opt['index_dir'] = args[1]
opt['queryfile_dir'] = args[2]
opt['result_dir'] = args[3]


if opt['index_dir'].startswith('/'):
    opt['index_dir'] = opt['index_dir'][1:]
if opt['result_dir'].startswith('/'):
    opt['result_dir'] = opt['result_dir'][1:]
if opt['queryfile_dir'].startswith('/'):
    opt['queryfile_dir'] = opt['queryfile_dir'][1:]


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

    QueryProcessor(opt, static=False).dynamic_processor()

    elapsed_time = time.time() - start_time

    print('Whole time: {:.2f}'.format(elapsed_time))
