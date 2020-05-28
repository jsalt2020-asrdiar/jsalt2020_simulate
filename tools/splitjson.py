#!/usr/bin/env python3
# encoding: utf-8

# Copyright 2020 Shanghai Jiao Tong University (Wangyou Zhang)
#  Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)

import argparse
import json
import os
import sys

import numpy as np


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputfile', type=str, required=True,
                        help='Json file to be splitted')
    parser.add_argument('--number_splits', type=int, required=True,
                        help='Number of splits to be generated')
    parser.add_argument('--outputdir', type=str, default='',
                        help='Output directory to store the splitted json files')
    args = parser.parse_args()

    # check parameter
    if args.number_splits <= 1:
        print('Error: Number of splits (%d) is too small.' % args.number_splits)
        sys.exit(1)

    # check directory
    filename = os.path.splitext(os.path.basename(args.inputfile))[0]
    if args.outputdir:
        dirname = args.outputdir
    else:
        dirname = os.path.dirname(os.path.abspath(args.inputfile))
        dirname = '{}/split{}'.format(dirname, args.number_splits)
        
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    # load json
    with open(args.inputfile) as f:
        utts = json.load(f)

    print("number of utterance pairs = %d" % len(utts))
    if len(utts) < args.number_splits:
        print("#utterances (%d) < #splits (%d). Use smaller split number." % (len(utts), args.number_splits))
        sys.exit(1)
    utts_list = np.array_split(utts, args.number_splits)
    utts_list = [utt_split.tolist() for utt_split in utts_list]

    for i, utt_split in enumerate(utts_list, 1):
        with open(os.path.join(dirname, '{}.{}.json'.format(filename, i)), 'w') as f:
            json.dump(utt_split, f, indent=2)
