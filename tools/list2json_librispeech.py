#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, os, sys, re, json, wave
from collections import OrderedDict



def main(args):
    # Create an empty corpus.    
    corpus = []

    # Count the number of lines.
    nlines = 0
    with open(args.input_list) as input_strm:
        for l in input_strm:
            nlines += 1

    if args.novad:
        spkr_ptrn = re.compile('(\d+)-\d+-\d+\.wav')
    else:
        spkr_ptrn = re.compile('(\d+)-\d+-\d+_\d\.wav')

    # 103-1240-0000_1

    # Read each line and get file names. 
    nlines_done = 0
    with open(args.input_list) as input_strm:
        for l in input_strm:
            # path, utterance ID
            path = l.rstrip()
            basename = os.path.basename(path)
            uttid, _ = os.path.splitext(basename)

            # speaker ID
            m = spkr_ptrn.match(basename)
            if m is None:
                raise RuntimeError('File name does not match the assumed speaker pattern: {}'.format(basename))

            spkrid = m.group(1) 

            with wave.open(path) as wf:
                nsamples = wf.getnframes()
                sr = wf.getframerate()
                dur = nsamples / sr
                
            # Generate segment info for the current file. 
            seg_info = OrderedDict([('utterance_id', uttid),
                                    ('path', path),
                                    ('speaker_id', spkrid),
                                    ('number_of_samples', nsamples),
                                    ('sampling_rate', sr),
                                    ('length_in_seconds', dur)])
            
            corpus.append(seg_info)
            
            # Print a progress report. 
            nlines_done += 1
            if nlines_done % 100 == 0:
                print('{:.2f}% [{}/{}]'.format(nlines_done/nlines * 100, nlines_done, nlines), flush=True)


    # Generate the output corpus file. 
    with open(args.output_file, 'w') as f:
        json.dump(corpus, f, indent=2)

        

def make_argparse():
    # Set up an argument parser. 
    parser = argparse.ArgumentParser(description='Create a JSON file for LibriSpeech.')
    parser.add_argument('--input_list', required=True, 
                        help='Wav file list.')
    parser.add_argument('--output_file', required=True,
                        help='Output JSON file name.')
    parser.add_argument('--novad', action='store_true', 
                        help='File name pattern for the no-VAD (i.e., the original LibriSpeech) data.')
                        
    return parser
    
    
if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
    

