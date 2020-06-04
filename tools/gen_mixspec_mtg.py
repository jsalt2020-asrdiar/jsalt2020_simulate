#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, os, json, random, copy
from collections import defaultdict
import numpy as np



def gen_session(corpus_spkrwise, tgtdir, nspkrs_per_session, nutts_per_spkr):
    ret = []

    # Initialize the dynamic corpus. 
    # Utterances will be removed once it is used. 
    dyn_corpus = {}
    for spkr in corpus_spkrwise:
        utterances = copy.deepcopy(corpus_spkrwise[spkr])
        random.shuffle(utterances)
        dyn_corpus[spkr] = utterances

    # Consume all utterances. 
    iter = 0
    while len(dyn_corpus) > 0:
        iter += 1
        speakers = list(dyn_corpus.keys())
        random.shuffle(speakers)

        print('--')
        print(f'Iteration {iter}')
        print(f'\tNumber of speakers: {len(speakers)}')

        # Histogram
        nutterances_per_speaker = [len(utterances) for utterances in dyn_corpus.values()]
        bins = np.linspace(0, 200, 10, endpoint=False)
        np.append(bin, np.inf)
        hist, bins = np.histogram(nutterances_per_speaker, bins=bins, density=False)    

        for (st, en), val in zip(zip(bins[:-1], bins[1:]), hist):
            print(f'\t({int(st):4} - {int(en):4}) {val}')


        for i in range(0, len(speakers), nspkrs_per_session):
            utterances_in_session = [[] for i in range(nutts_per_spkr)]

            # Pick the speakers to be included in the current session. 
            for spkr in speakers[i : i + nspkrs_per_session]:
                pop = dyn_corpus[spkr][:nutts_per_spkr]                    
                rem = dyn_corpus[spkr][nutts_per_spkr:]

                if len(rem) == 0:
                    dyn_corpus.pop(spkr)
                else:
                    dyn_corpus[spkr] = rem

                for i, utt in enumerate(pop):
                    utterances_in_session[i].append(utt)


            # Try to avoid adjacent utterances being spoken by the same speaker. 
            utterances_in_session_reorg = copy.deepcopy(utterances_in_session[0])
            for current_utterances in utterances_in_session[1:]:
                last_spkr = utterances_in_session_reorg[-1]['speaker_id']

                temp = copy.deepcopy(current_utterances)
                if len(temp) == 0:
                    break
                elif len(temp) == 1:
                    utterances_in_session_reorg.append(temp[0])
                else:
                    while True:
                        random.shuffle(temp)
                        if temp[0]['speaker_id'] != last_spkr:
                            utterances_in_session_reorg += temp
                            break

            ret.append(utterances_in_session_reorg)

    return ret



def give_timing(sess_list, overlap_time_ratio=0.3):
    ret = []

    for sess in sess_list:
        time_marked_sess = copy.deepcopy(sess)

        # Calculate the total length and derive the overlap time budget. 
        total_len = np.sum(np.array([utt['length_in_seconds'] for utt in time_marked_sess]))
        total_overlap_time = total_len * overlap_time_ratio / (1 + overlap_time_ratio)

        # Distribute the budget to each utterance boundary with the "stick breaking" approach. 
        nutts = len(time_marked_sess)
        probs = []
        rem = 1
        for i in range(nutts - 2):
            p = random.betavariate(1, 5)
            probs.append(rem * p)
            rem *= (1 - p)
        probs.append(rem)
        random.shuffle(probs)
        probs.insert(0, 0)
        overlap_times = total_overlap_time * np.array(probs)

        offset = 0
        for utt, ot in zip(time_marked_sess, overlap_times):
            offset -= ot
            utt['offset'] = offset            
            offset += utt['length_in_seconds']

        ret.append(time_marked_sess)

    return ret



def main(args):
    random.seed(0)

    # Get the input files.
    with open(args.inputfile) as f:
        corpus = json.load(f)

    # Reorganize the data by speakers. 
    corpus_spkrwise = defaultdict(list)
    for utt in corpus:
        corpus_spkrwise[utt['speaker_id']].append(utt)

    # Generate session specs. 
    sess_list = gen_session(corpus_spkrwise, args.targetdir, args.speakers, args.utterances_per_speaker)

    # Give start times to each utterance. 
    sess_list = give_timing(sess_list, overlap_time_ratio=args.overlap_time_ratio)

    # Give an output file name to each session. 
    output = []
    ndigits = len(str(len(sess_list)))
    ptrn = f'[:0{ndigits}d].wav'.replace('[', '{').replace(']', '}')
    for i, sess in enumerate(sess_list):
        sess_out = os.path.join(args.targetdir, ptrn.format(i))
        dic = {'input': sess, 
               'output': sess_out}
        output.append(dic)

    # Generate the output JSON file. 
    print('')
    print(f'Dumping the session info to {args.outputfile}.')
    os.makedirs(os.path.dirname(os.path.abspath(args.outputfile)), exist_ok=True)
    with open(args.outputfile, 'w') as f:
        json.dump(output, f, indent=2)



def make_argparse():
    # Set up an argument parser.
    parser = argparse.ArgumentParser(description='Create a JSON file for meeting-ish audio simulation.')
    parser.add_argument('--inputfile', metavar='<file>', required=True,
                        help='Input corpus file in JSON.')
    parser.add_argument('--outputfile', metavar='<file>', required=True,
                        help='Output mixing file in JSON.')
    parser.add_argument('--targetdir', metavar='<dir>', required=True,
                        help='Target directory name.')
    parser.add_argument('--speakers', type=int, metavar='<int>', default=3, 
                        help='Number of speakers per session.')
    parser.add_argument('--utterances_per_speaker', type=int, metavar='<int>', default=3, 
                        help='Number of utterances per session/speaker.')
    parser.add_argument('--overlap_time_ratio', type=float, metavar='<float>', default=0.2, 
                        help='Target overlap time ratio as defined as overlap-time/session-time.')

    return parser


if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
