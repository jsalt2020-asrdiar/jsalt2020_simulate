#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, os, json, random, copy
from collections import defaultdict
import numpy as np
from scipy.stats import bernoulli



def gen_session(corpus_spkrwise, tgtdir, config):
    ret = []

    # Initialize the dynamic corpus. 
    # Utterances will be removed once it is used. 
    dyn_corpus = {}
    for spkr in corpus_spkrwise:
        utterances = copy.deepcopy(corpus_spkrwise[spkr])
        random.shuffle(utterances)
        dyn_corpus[spkr] = utterances

    # Get the list of the configs. 
    cfgnames = sorted(list(config['probabilities'].keys()))
    cfg_probs = np.array([config['probabilities'][c] for c in cfgnames])
    cfg_probs /= np.sum(cfg_probs)

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


        start_spkr = 0
        while start_spkr < len(speakers):
            # Choose the configuration to be used for the current session. 
            cfgname = random.choices(cfgnames, weights=cfg_probs, k=1)[0]
            cur_cfg = config['configurations'][cfgname]

            # Pick the speakers for this session. 
            cur_nspkrs = random.choice(cur_cfg['speakers_per_session'])
            cur_spkrs = speakers[start_spkr : start_spkr + cur_nspkrs]
            start_spkr += cur_nspkrs

            utterances_in_session = defaultdict(list)

            for spkr in cur_spkrs:
                # Determine the number of utteraces for the current speaker. 
                cur_nutts = random.choice(cur_cfg['utterances_per_speaker'])

                # Pick the utterances.
                pop = dyn_corpus[spkr][:cur_nutts]
                rem = dyn_corpus[spkr][cur_nutts:]

                if len(rem) == 0:
                    dyn_corpus.pop(spkr)
                else:
                    dyn_corpus[spkr] = rem

                for i, utt in enumerate(pop):
                    utterances_in_session[i].append(utt)

            # Convert defaultdict to a list of lists.
            utterances_in_session = [utterances_in_session[k] for k in range(len(utterances_in_session))]

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

            # Pick the timing configurations. 
            overlap_time_ratio = random.uniform(cur_cfg['overlap_time_ratio'][0], cur_cfg['overlap_time_ratio'][1])
            sess, attr = give_timing(utterances_in_session_reorg, 
                                     overlap_time_ratio=overlap_time_ratio, 
                                     sil_prob=cur_cfg['silence_probability'], 
                                     sil_dur=cur_cfg['silence_duration'], 
                                     allow_3fold_overlap=cur_cfg['allow_3fold_overlap'])

            ret.append({'utterances': sess, 'attr': attr})

    return ret



def give_timing(sess, overlap_time_ratio=0.3, sil_prob=0.2, sil_dur=[0.3, 2.0], allow_3fold_overlap=False):
    time_marked_sess = copy.deepcopy(sess)

    # Calculate the total length and derive the overlap time budget. 
    total_len = np.sum(np.array([utt['length_in_seconds'] for utt in time_marked_sess]))
    total_overlap_time = total_len * overlap_time_ratio / (1 + overlap_time_ratio)

    # Determine where to do overlap. 
    nutts = len(time_marked_sess)
    to_overlap = bernoulli.rvs(1 - sil_prob, size=nutts - 1).astype(bool).tolist()
    noverlaps = sum(to_overlap)

    # Distribute the budget to each utterance boundary with the "stick breaking" approach. 
    probs = []
    rem = 1
    for i in range(noverlaps - 1):
        p = random.betavariate(1, 5)
        probs.append(rem * p)
        rem *= (1 - p)
    probs.append(rem)
    random.shuffle(probs)

    idx = -1
    overlap_times = [0.0]
    for b in to_overlap:
        if b:
            idx += 1
            overlap_times.append(probs[idx] * total_overlap_time)
        else:
            overlap_times.append(-np.random.uniform(low=sil_dur[0], high=sil_dur[1]))

    # Get all speakers. 
    speakers = set(utt['speaker_id'] for utt in time_marked_sess)        

    # Determine the offset values while ensuring that there is no overlap between multiple utterances spoken by the same person. 
    offset = 0
    last_utt_end = {spkr: 0.0 for spkr in speakers}
    last_utt_end_times = sorted(list(last_utt_end.values()), reverse=True)  # all zero (of course!)
    actual_overlap_time = 0
    for utt, ot in zip(time_marked_sess, overlap_times):
        spkr = utt['speaker_id']

        if len(last_utt_end_times) > 1 and (not allow_3fold_overlap): 
            # second term for ensuring same speaker's utterances do not overlap. 
            # third term for ensuring the maximum number of overlaps is two. 
            ot = min(ot, offset - last_utt_end[spkr], offset - last_utt_end_times[1])
        else:
            ot = min(ot, offset - last_utt_end[spkr])

        offset -= ot
        actual_overlap_time += max(ot, 0)
        utt['offset'] = offset
        offset += utt['length_in_seconds']

        last_utt_end[spkr] = offset

        last_utt_end_times = sorted(list(last_utt_end.values()), reverse=True)
        offset = last_utt_end_times[0]

    actual_overlap_time_ratio = actual_overlap_time / (total_len - actual_overlap_time)

    attr = {'target_overlap_time_ratio': overlap_time_ratio, 
            'actual_overlap_time_ratio': actual_overlap_time_ratio}

    return time_marked_sess, attr



def main(args):
    # Make the results predictable.
    if args.random_seed is not None:
        random.seed(args.random_seed)
        np.random.seed(args.random_seed)

    # Get the input files.
    with open(args.inputfile) as f:
        corpus = json.load(f)

    # Load the dynamics file. 
    with open(args.config) as f:
        config = json.load(f)

    # Reorganize the data by speakers. 
    corpus_spkrwise = defaultdict(list)
    for utt in corpus:
        corpus_spkrwise[utt['speaker_id']].append(utt)

    # Group uterances to form sessions. 
    sess_list = gen_session(corpus_spkrwise, args.targetdir, config)

    # Give an output file name to each session. 
    output = []
    ndigits = len(str(len(sess_list)))
    ptrn = f'[:0{ndigits}d].wav'.replace('[', '{').replace(']', '}')
    for i, sess in enumerate(sess_list):
        speakers = sorted(list(set([utt['speaker_id'] for utt in sess['utterances']])))
        sess_out = os.path.join(args.targetdir, ptrn.format(i))
        dic = {'inputs': sess['utterances'], 
               'output': sess_out, 
               'speakers': speakers, 
               'target_overlap_time_ratio': sess['attr']['target_overlap_time_ratio'], 
               'actual_overlap_time_ratio': sess['attr']['actual_overlap_time_ratio']}
        output.append(dic)

    # Generate the output JSON file. 
    print('')
    print(f'Dumping the session info to {args.outputfile}.')
    os.makedirs(os.path.dirname(os.path.abspath(args.outputfile)), exist_ok=True)
    with open(args.outputfile, 'w') as f:
        json.dump(output, f, indent=2)



def make_argparse():
    # Set up an argument parser.
    parser = argparse.ArgumentParser(description='Create a JSON file for meeting-ish audio simulation.', 
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--inputfile', metavar='<file>', required=True,
                        help='Input corpus file in JSON.')
    parser.add_argument('--outputfile', metavar='<file>', required=True,
                        help='Output mixing file in JSON.')
    parser.add_argument('--targetdir', metavar='<dir>', required=True,
                        help='Target directory name.')
    parser.add_argument('--config', metavar='<file>', required=True,
                        help='Speaker dynamics configuration file.')
    parser.add_argument('--random_seed', metavar='N', type=int,
                        help='Seed for random number generators. The current system time is used when this option is not used.')

    return parser


if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
