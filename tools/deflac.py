#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, os, sys, fnmatch
import soundfile as sf



def main(args):
    # Check if the source directories exist. 
    for srcdir in args.srcdir:
        if not os.path.isdir(srcdir):
            raise IOError('Specified directory cannot be found: {}'.format(srcdir))

    for srcdir in args.srcdir:
        # Count the number of files to be processed. 
        print('Retrieving FLAC files in {}'.format(srcdir), flush=True)
        nfiles = 0
        for dirpath, _, filenames in os.walk(srcdir):
            for filename in filenames:
                if fnmatch.fnmatch(filename, '*.flac'):
                    nfiles += 1
        print('{} files found.'.format(nfiles), flush=True)

        # Convert the file format. 
        nprocessed = 0
        for dirpath, _, filenames in os.walk(srcdir):
            for filename in filenames:
                if fnmatch.fnmatch(filename, '*.flac'):
                    nprocessed += 1

                    srcfile = os.path.join(dirpath, filename)
                    dstdir = os.path.join(args.dstdir, os.path.basename(srcdir), os.path.relpath(dirpath, start=srcdir))
                    os.makedirs(dstdir, exist_ok=True)                    
                    dstfile = os.path.join(dstdir, '{}.wav'.format(os.path.splitext(filename)[0]))

                    data, samplerate = sf.read(srcfile)
                    sf.write(dstfile, data, samplerate)
                    print('[{}/{}]: {}'.format(nprocessed, nfiles, dstfile), flush=True)


    
def make_argparse():
    # Set up an argument parser. 
    parser = argparse.ArgumentParser(description='FLAC to WAV conversion.')
    parser.add_argument('--srcdir', metavar='<dir>', nargs='+', required=True, 
                        help='Source directory. All .flac files under this directory will be processed.')
    parser.add_argument('--dstdir', metavar='<dir>', required=True,
                        help='Destination directory where the generated WAV files will be stored.')
                        
    return parser
    
    
if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
    
