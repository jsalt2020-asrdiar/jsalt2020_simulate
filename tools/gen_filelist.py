#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, os, sys
import fnmatch
import wave



def write_one_file(ostream, src, min_samplerate=None):
    ok_to_write = True

    if min_samplerate is not None:
        with wave.open(src) as wf:
            fs = wf.getframerate()
        if fs < min_samplerate:
            ok_to_write = False

    if ok_to_write:
        print(src, file=ostream)
    


def main(args):
    # Check if the source directories exist. 
    for srcdir in args.srcdir:
        if not os.path.isdir(srcdir):
            raise IOError('Specified directory cannot be found: {}'.format(srcdir))

    # Create the output directory. 
    tgtdir = os.path.dirname(os.path.abspath(args.outlist))
    os.makedirs(tgtdir, exist_ok=True)

    with open(args.outlist, 'w') as ostream:
        for srcdir in args.srcdir:
            for dirpath, dirnames, filenames in os.walk(srcdir):
                for filename in filenames:
                    include_test = any([fnmatch.fnmatch(filename, f) for f in args.include_filter])
                    exclude_test = all([not fnmatch.fnmatch(filename, f) for f in args.exclude_filter])
                    if include_test and exclude_test:
                        write_one_file(ostream, os.path.join(dirpath, filename), args.min_samplerate)


    
def make_argparse():
    # Set up an argument parser. 
    parser = argparse.ArgumentParser(description='Create a file list.')
    parser.add_argument('--srcdir', metavar='<dir>', nargs='+', required=True, 
                        help='Source directory. All files under this directory will be listed.')
    parser.add_argument('--outlist', metavar='<dir>', required=True,
                        help='Name of the output file listing the filenames of interest.')
    parser.add_argument('--include_filter', nargs='*', metavar='<pattern str>', default=['*.wav', '*.WAV'],
                        help='File names that match one of these are included in the list. By default, only files with .wav or .WAV extensions are included.')
    parser.add_argument('--exclude_filter', nargs='*', metavar='<pattern str>', default=[], 
                        help='File names that match one of these are not included in the list. This is not used by default.')
    parser.add_argument('--min_samplerate', metavar='<int>', type=int,
                        help='Minimum sampling rate in Hz. Caution: Make sure that the target files are wav files. This program performs no format check.')
                        
    return parser
    
    
if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
    
