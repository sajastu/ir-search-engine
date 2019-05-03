import operator
import os
import random
import time
from collections import deque

from utils import index_utils as utils
from entities.posting_item import PostingItem
from utils.index_utils import write_doc_to_file
from utils.parse_utils import parse_document


class Index:
    def __init__(self, opt):
        self.opt = opt
        self.memory_cons = self.opt['memory']
        self.term_doc_list = set([])
        self.doc_id = 0
        self.out_dir = self.opt['index_dir']
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)
        self.block_queue = deque([])
        self.incompleted = True
        self.cur_processed_file =''
        self.counter_on_cur_file=0
        self.portion_number=1
        self.file_prev_position = 0
        self.token_prev_position = 0
        self.prev_tokens = []
        self.files = []
        self.i = 0
        self.word_id = 0
        # j=1
        for filename in os.listdir(self.opt['data_dir']):
            # os.rename('raw_data/' + filename, 'raw_data/' + str(j))
            self.files.append(filename)
            # j+=1
        self.files = sorted(self.files)

    def EOF(self, f):
            current_pos = f.tell()
            file_size = os.fstat(f.fileno()).st_size
            return current_pos >= file_size

    def read_file_portion(self):
        data = []
        flag = False
        j = 0
        if len(self.files) > 0:
            print('Now reading: ' + self.files[0])
            # if self.files[0] == 'fr941206.1':
            #     s = 9
            self.cur_processed_file = self.files[0]

            with open(self.opt['data_dir'] + '/' + self.files[0], 'r') as f:

                line = f.readline()
                f.seek(self.file_prev_position)
                while line:
                    if line.startswith('<DOC>'):
                        flag = True
                    if flag:
                        data.append(line)
                    if line.strip().endswith('</DOC>'):
                        flag = False
                        doc_num, tokens, token_positions = parse_document(' '.join(data).replace('\n', ''), self.opt['type'])
                        data.clear()
                        self.i += 1
                        for i, token in enumerate(tokens):
                            if len(token_positions) == 0:
                                self.term_doc_list.add((token, PostingItem(doc_num, tokens.count(token))))
                            if len(token_positions) > 0:
                                self.term_doc_list.add((token, PostingItem(doc_num, tokens.count(token), [token_positions[i] for i, x in enumerate(tokens) if x == token])))

                        if len(self.term_doc_list) > self.memory_cons:
                            self.portion_number +=1
                            self.file_prev_position = f.tell()
                            break
                    line = f.readline()
                    if line == '':
                        self.portion_number = 1
                        self.file_prev_position = 0
                        if len(self.files) > 1:
                            self.counter_on_cur_file +=1
                            self.files.pop(0)
                        elif len(self.files) == 1:
                            self.incompleted = False

    def rw_first_blocks(self):
        while self.incompleted:
            self.read_file_portion()
            print('Sorting Tuples for file: {}, Portion Number: {} '.format(self.cur_processed_file, self.portion_number))
            blk_filename = self.cur_processed_file + '-' + str(self.portion_number)
            # blk_filename = self.cur_processed_file
            blk_postings_dir = self.out_dir
            block_posting_filename = open(blk_postings_dir + blk_filename + '.pl', 'w')
            block_dict = open(blk_postings_dir + blk_filename + '.dt', 'w')

            self.block_queue.append(blk_filename)

            self.term_doc_list = list(self.term_doc_list)

            self.term_doc_list = sorted(self.term_doc_list, key=operator.itemgetter(0))
            intermediate_postings_list = {}
            for term, pi in self.term_doc_list:
                if term not in intermediate_postings_list.keys():
                    if pi.positions is not None and len(pi.positions) > 0:
                        intermediate_postings_list[term] = [PostingItem(pi.doc_num, pi.freq, pi.positions)]
                    else:
                        intermediate_postings_list[term] = [pi]
                else:
                    if pi.positions is not None and len(pi.positions) > 0:
                        intermediate_postings_list[term].append(PostingItem(pi.doc_num, pi.freq, pi.positions))
                    else:
                        intermediate_postings_list[term].append(pi)

            print('Writing the posting list --> ' + self.cur_processed_file + '-' + str(self.portion_number))

            terms = {t: intermediate_postings_list[t] for t in sorted(intermediate_postings_list.keys())}
            for term in terms:
                intermediate_postings_list[term].sort(key=lambda x: x.doc_num, reverse=False)
                utils.write_intermediate_index(block_dict, block_posting_filename, term, intermediate_postings_list[term])
            block_posting_filename.close()
            block_dict.close()
            self.term_doc_list.clear()
            self.term_doc_list = set([])
        print('Num of docs : ' + str(self.i))

    def index_constuction(self):
        # self.block_queue = mockup_blocks_queue(self.opt)

        print('\nMerging written blocks...')
        while True:
            # if there is (are) NOT any blocks that remained unmerged, just break
            if len(self.block_queue) <= 1:
                break
            # else merge blocks 2-by-2 (bkl 1, and blk2)
            blk_1 = self.block_queue.popleft()
            blk_2 = self.block_queue.popleft()
            merged_tmp_lexicon = str(random.sample(range(99999999), 1)[0])
            print('Merging {} + {} --> {}'.format(blk_1, blk_2, merged_tmp_lexicon))
            blk1_pl = open(self.out_dir + blk_1 + '.pl', 'r')
            try:
                blk2_pl = open(self.out_dir + blk_2 + '.pl', 'r')
            except:
                ss=0
            blk1_dt_file = open(self.out_dir + blk_1 + '.dt', 'r')
            blk2_dt_file = open(self.out_dir + blk_2 + '.dt', 'r')
            merged_pl_tmp_lexicon = open(self.out_dir + merged_tmp_lexicon + '.pl', 'w')
            merged_dt_tmp_lexicon = open(self.out_dir + merged_tmp_lexicon + '.dt', 'w')

            # write the new merged posting lists block to file 'merged_tmp_pl'

            term_first_blk = utils.get_next_line(blk1_dt_file, blk1_pl)
            term_second_blk = utils.get_next_line(blk2_dt_file, blk2_pl)

            while True:
                if term_first_blk is None or term_second_blk is None:
                    break
                term_a, term_b = term_first_blk[0], term_second_blk[0]

                if term_a == term_b:
                    utils.merge_rewrite_pl(merged_dt_tmp_lexicon, merged_pl_tmp_lexicon, term_a, term_first_blk[1], term_second_blk[1])
                    term_first_blk = utils.get_next_line(blk1_dt_file, blk1_pl)
                    term_second_blk = utils.get_next_line(blk2_dt_file, blk2_pl)
                elif term_a < term_b:
                    utils.write_intermediate_index(merged_dt_tmp_lexicon, merged_pl_tmp_lexicon, term_a, term_first_blk[1])
                    term_first_blk = utils.get_next_line(blk1_dt_file, blk1_pl)
                else:
                    utils.write_intermediate_index(merged_dt_tmp_lexicon, merged_pl_tmp_lexicon, term_b, term_second_blk[1])
                    term_second_blk = utils.get_next_line(blk2_dt_file, blk2_pl)
            while term_first_blk is not None:
                term_a = term_first_blk[0]
                utils.write_intermediate_index(merged_dt_tmp_lexicon, merged_pl_tmp_lexicon, term_a, term_first_blk[1])
                term_first_blk = utils.get_next_line(blk1_dt_file, blk1_pl)
            while term_second_blk is not None:
                term_b = term_second_blk[0]
                utils.write_intermediate_index(merged_dt_tmp_lexicon, merged_pl_tmp_lexicon, term_b, term_second_blk[1])
                term_second_blk = utils.get_next_line(blk2_dt_file, blk2_pl)

            blk1_pl.close()
            blk2_pl.close()
            merged_pl_tmp_lexicon.close()
            blk1_dt_file.close()
            blk2_dt_file.close()
            merged_dt_tmp_lexicon.close()
            os.remove(self.out_dir + blk_1 + '.pl')
            os.remove(self.out_dir + blk_2 + '.pl')
            os.remove(self.out_dir + blk_1 + '.dt')
            os.remove(self.out_dir + blk_2 + '.dt')
            self.block_queue.append(merged_tmp_lexicon)

        print('\nPosting Lists Merging DONE!')

        # rename the final merged block to corpus.initial_blocks
        final_name = self.block_queue.popleft()
        os.rename(self.out_dir + '/' + final_name + '.pl', self.out_dir + '/postings.pl')
        os.rename(self.out_dir + '/' + final_name + '.dt', self.out_dir + '/lexicon.dt')

    def run_indexer(self):
        start_time = time.time()
        self.rw_first_blocks()
        elapsed_time = time.time() - start_time
        start_time_2 = time.time()
        self.index_constuction()
        elapsed_time_2 = time.time() - start_time_2
        print('Temporary files : {:.2f}'.format(elapsed_time))
        print('Merging files : {:.2f}'.format(elapsed_time_2))

    def run_indexer_unlimited(self):
        start_time = time.time()
        self.read_unlimited()
        elapsed_time = time.time() - start_time
        start_time_2 = time.time()
        elapsed_time_2 = time.time() - start_time_2
        print('Temporary files : {:.2f}'.format(elapsed_time))
        print('Merging files : {:.2f}'.format(elapsed_time_2))

    def read_unlimited(self):
        data = []
        docs_with_tokens = {}
        flag = False
        j = 0
        for file in self.files:
            print('Now reading: ' + file)
            with open(self.opt['data_dir'] + '/' + file, 'r') as f:
                line = f.readline()
                while line:
                    if line.startswith('<DOC>'):
                        flag = True
                    if flag:
                        data.append(line)
                    if line.strip().endswith('</DOC>'):
                        flag = False
                        doc_num, tokens, token_positions, doc_len = parse_document(' '.join(data).replace('\n', ''),
                                                                          self.opt['type'])
                        docs_with_tokens[doc_num] = tokens
                        data.clear()
                        for i, token in enumerate(tokens):
                            if len(token_positions) == 0:
                                self.term_doc_list.add((token, PostingItem(doc_num, tokens.count(token), doc_length=doc_len)))
                            if len(token_positions) > 0:
                                self.term_doc_list.add((token, PostingItem(doc_num, tokens.count(token),
                                                                           [token_positions[i] for i, x in
                                                                            enumerate(tokens) if x == token], doc_length=doc_len)))

                    line = f.readline()
        dir = self.out_dir[:-1] + '-' + self.opt['type'] + '/'
        if not os.path.exists(dir):
            os.mkdir(dir)

        block_posting_filename = open(self.out_dir[:-1] + '-' + self.opt['type'] + '/postings.pl', 'w')
        block_dict = open(self.out_dir[:-1] + '-' + self.opt['type'] + '/lexicon.dt', 'w')

        self.term_doc_list = list(self.term_doc_list)

        self.term_doc_list = sorted(self.term_doc_list, key=operator.itemgetter(0))
        postinglist = {}
        for term, pi in self.term_doc_list:
            if term not in postinglist.keys():
                if pi.positions is not None and len(pi.positions) > 0:
                    postinglist[term] = [PostingItem(pi.doc_num, pi.freq, pi.positions)]
                else:
                    postinglist[term] = [pi]
            else:
                if pi.positions is not None and len(pi.positions) > 0:
                    postinglist[term].append(PostingItem(pi.doc_num, pi.freq, pi.positions))
                elif pi.doc_num not in [pi2.doc_num for pi2 in postinglist[term]]:
                    postinglist[term].append(pi)

        print('Writing the posting list')
        write_doc_to_file(docs_with_tokens, 'dict')
        terms = {t: postinglist[t] for t in sorted(postinglist.keys())}
        for term in terms:
            postinglist[term].sort(key=lambda x: x.doc_num, reverse=False)
            utils.write_intermediate_index(block_dict, block_posting_filename, term,
                                           postinglist[term])
        block_posting_filename.close()
        block_dict.close()