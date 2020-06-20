#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, os, json, fnmatch, random, copy
from collections import OrderedDict
import numpy as np



def greedy_pairing(orig_corpus, output, targetdir, appendix=''):
    corpus = copy.deepcopy(orig_corpus)
    random.shuffle(corpus)

    failed = []
    success = 0
    head = 0

    while head < len(corpus)-1:
        if corpus[head]['speaker_id'] != corpus[head+1]['speaker_id']:
            ifnames = (corpus[head]['path'], corpus[head+1]['path'])
            if appendix == '':
                ofname = os.path.join( targetdir, '{}__{}.wav'.format(corpus[head]['utterance_id'], corpus[head+1]['utterance_id']) )
            else:
                ofname = os.path.join( targetdir, '{}__{}{}.wav'.format(corpus[head]['utterance_id'], corpus[head+1]['utterance_id'], appendix) )
            output.append( OrderedDict([('inputs', ifnames), ('output', ofname)]) )

            head += 2
            success += 1
        else:
            failed.append(corpus[head])
            head += 1
            
    print('{} pairs created out of {} files. {} left.'.format(success, len(corpus), len(failed)), flush=True)
    return failed


def greedy_pairing_target_interf(target_corpus, interf_corpus, output, targetdir, appendix=''):
    tcorpus = copy.deepcopy(target_corpus)
    icorpus = copy.deepcopy(interf_corpus)
    random.shuffle(icorpus)

    tfailed = []
    ifailed = []
    success = 0
    head = 0

    while head < len(tcorpus):
        if tcorpus[head]['speaker_id'] != icorpus[head]['speaker_id']:
            ifnames = ( tcorpus[head]['path'], icorpus[head]['path'] )
            if appendix == '':
                ofname = os.path.join( targetdir, '{}__{}.wav'.format(tcorpus[head]['utterance_id'], icorpus[head]['utterance_id']) )
            else:
                ofname = os.path.join( targetdir, '{}__{}{}.wav'.format(tcorpus[head]['utterance_id'], icorpus[head]['utterance_id'], appendix) )
            output.append( OrderedDict([('inputs', ifnames), ('output', ofname)]) )
            success += 1
        else:
            tfailed.append(tcorpus[head])
            ifailed.append(icorpus[head])
        head += 1

    print('{} pairs created out of {} files. {} left.'.format(success, len(tcorpus), len(tfailed)), flush=True)
    return tfailed, ifailed



def gen_pairs(orig_corpus, targetdir, single_speaker_percentage, appendix=''):
    corpus = copy.deepcopy(orig_corpus)
    random.shuffle(corpus)

    output = []

    # Leave the no-mix files out. 
    nsingles = int(single_speaker_percentage * len(corpus))
    for i in range(nsingles):
        ifnames = (corpus[i]['path'],)
        ofname = os.path.join(targetdir, corpus[i]['utterance_id'] + appendix + '.wav')
        output.append( OrderedDict([('inputs', ifnames), ('output', ofname)]) )
   
    corpus = corpus[nsingles:]

    # Create a list of pairs for mixing. 
    retried = 0
    while len(corpus) > 0 and retried < 10:
        print('Iteration {}'.format(retried+1), flush=True)
        corpus = greedy_pairing(corpus, output, targetdir, appendix)
        retried += 1


    if len(corpus) > 0:
        print('The following files failed to be paired.', flush=True)
        for f in corpus:
            print(f['utterance_id'], flush=True)
    else:
        print('All files were successfully paired.', flush=True)
    
    return output



def main(args):
    # Make the results predictable.
    if args.random_seed is not None:
        random.seed(args.random_seed)
        np.random.seed(args.random_seed)

    # Get the input files.
    with open(args.inputfile) as f:
        corpus = json.load(f)
    
    output = []
    single_speaker_percentage = args.single_speaker_percentage / (2 - args.single_speaker_percentage) * args.ncopies
    
    for i in range(args.ncopies):
        if i == 0:
            if args.ncopies == 1:
                output += gen_pairs(corpus, args.targetdir, single_speaker_percentage, appendix='')
            else:
                output += gen_pairs(corpus, args.targetdir, single_speaker_percentage, appendix='__V0')
        else:
            output += gen_pairs(corpus, args.targetdir, 0, appendix='__V{}'.format(i))

    # Generate the output JSON file. 
    os.makedirs(os.path.dirname(os.path.abspath(args.outputfile)), exist_ok=True)
    with open(args.outputfile, 'w') as f:
        json.dump(output, f, indent=2)



def make_argparse():
    # Set up an argument parser.
    parser = argparse.ArgumentParser(description='Create a JSON file specifying the mixing configuration for each pair.')
    parser.add_argument('--inputfile', metavar='FILE', required=True,
                        help='Input corpus file in JSON.')
    parser.add_argument('--outputfile', metavar='FILE', required=True,
                        help='Output mixing file in JSON.')
    parser.add_argument('--targetdir', metavar='DIR', required=True,
                        help='Target directory name.')
    parser.add_argument('--ncopies', metavar='N', type=int, default=1, 
                        help='Number of copies.')
    parser.add_argument('--single_speaker_percentage', metavar='X', required=True, type=float, 
                        help='This percentage of the input files are not mixed.')
    parser.add_argument('--random_seed', metavar='N', type=int,
                        help='Seed for random number generators. The current system time is used when this option is not used.')
    

    return parser


if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
