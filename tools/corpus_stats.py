#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, os, json
from collections import defaultdict
import numpy as np



def main(args):
    # Get the input files.
    with open(args.inputfile) as f:
        corpus = json.load(f)

    # Reorganize the data by speakers. 
    utterances_per_speaker = defaultdict(list)

    for utt in corpus:
        utterances_per_speaker[utt['speaker_id']].append(utt)

    # Number of speakers
    print('[Number of speakers]')
    print(f'\t{len(utterances_per_speaker)}')
    print('')

    # Number of utterances per speaker
    nutterances_per_speaker = [len(utterances) for utterances in utterances_per_speaker.values()]
    print('[Utterances per speaker]')
    print(f'\tMin : {np.amin(nutterances_per_speaker)}')
    print(f'\tMax : {np.amax(nutterances_per_speaker)}')
    print(f'\tMean: {np.mean(nutterances_per_speaker):.2f}')
    print('')

    # Utterance length
    uttlen = [utt['length_in_seconds'] for utt in corpus]
    longest = corpus[np.argmax(uttlen)]['path']
    shortest = corpus[np.argmin(uttlen)]['path']

    print('[Utterance length]')
    print(f'\tMin : {np.amin(uttlen):5.2f} s, {shortest}')
    print(f'\tMax : {np.amax(uttlen):5.2f} s, {longest}')
    print(f'\tMean: {np.mean(uttlen):5.2f} s')
    print('')

    # Histogram
    bins = np.linspace(0, 30, 12, endpoint=False)
    np.append(bin, np.inf)
    hist, bins = np.histogram(uttlen, bins=bins, density=False)    

    print('[Utterance length histogram]')
    for (st, en), val in zip(zip(bins[:-1], bins[1:]), hist):
        print(f'\t({st:4.1f}s - {en:4.1f}s) {val}')



def make_argparse():
    # Set up an argument parser.
    parser = argparse.ArgumentParser(description='Show some statistics of a corpus.')
    parser.add_argument('--inputfile', metavar='<file>', required=True,
                        help='Input corpus file in JSON.') 

    return parser


if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
