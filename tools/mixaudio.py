#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, sys, os, json, random
from collections import OrderedDict
import numpy as np

# Add path to libaueffect and load the module.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import libaueffect



def main(args):
    # Make the results predictable.
    if args.random_seed is not None:
        random.seed(args.random_seed)
        np.random.seed(args.random_seed)

    # Read in the IO list. 
    with open(args.iolist) as f:
        iolist = json.load(f)

    # Instatiate the mixers.    
    mixers, priors = mixer_array = libaueffect.create_AudioMixerArray(args.mixers_configfile) 
    nmixers = len(mixers)

    # Create the output directories.
    os.makedirs(os.path.dirname(os.path.abspath(args.outlist)), exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(args.log)), exist_ok=True)

    if args.save_image:
        to_save = ('image', 'noise')
    else:
        to_save = ('source', 'rir', 'noise')

    with open(args.log, 'w') as log_stream:
        print('[', file=log_stream)

        with open(args.outlist, 'w') as outfile_stream:
            # Process each audio file.
            for i, iofiles in enumerate(iolist):
                print('[{}/{} ({:.3f}%)]'.format(i+1, len(iolist), i / len(iolist)))

                infiles = [os.path.abspath(f) for f in iofiles['inputs']]
                outfile = os.path.abspath(iofiles['output'])

                # Load each input signal.
                x = []
                for f in infiles:
                    try:
                        _x, sr = libaueffect.read_wav(f, sample_rate=args.sample_rate, channel=0)
                    except RuntimeError:
                        print('Wav file is broken, skipped: {}'.format(f))
                        continue

                    if args.cancel_dcoffset:
                        _x -= np.mean(_x)
                    x.append(_x)
                sr = args.sample_rate

                # Choose the mixer to use. 
                mixer = mixers[np.random.choice(nmixers, p=priors)]

                y, p = mixer(x, 
                             sr, 
                             output_filename=outfile, 
                             input_filenames=infiles, 
                             to_save=to_save, 
                             save_as_one_file=(not args.save_each_channel_in_onefile))

                print(os.path.abspath(outfile), file=outfile_stream)
                libaueffect.write_wav(y, 
                                      outfile, 
                                      sample_rate=sr, 
                                      avoid_clipping=False, 
                                      save_as_one_file=(not args.save_each_channel_in_onefile))

                params = OrderedDict([('output', outfile), ('inputs', infiles)] + list(p.items()))
                json.dump(params, log_stream, indent=4)

                # Print the list element separator. 
                if iofiles == iolist[-1]:
                    print('', file=log_stream)
                else:
                    print(',', file=log_stream)

            # end of the list. 
            print(']', file=log_stream)



def make_argparse():
    defaults = {'outlist' : 'tmp/audio_mixer_out.scp',
                'log' : 'tmp/audio_mixer_run.json',
                'ncopies' : 1,
                'filename_style' : None}

    # Set up an argument parser.
    parser = argparse.ArgumentParser(description='Mix audio files.')
    parser.add_argument('--debug', action='store_true',
                        help='Print debug-level messages from libaueffect.')

    parser.add_argument('--iolist', metavar='FILE', required=True, 
                        help='JSON file listing pair of source and output file names.')

    dest_args = parser.add_argument_group('Output options')
    dest_args.add_argument('--outlist', metavar='FILE', default=defaults['outlist'],
                           help='List of generated audio files. (default={})'.format(defaults['outlist']))
    dest_args.add_argument('--log', metavar='FILE', default=defaults['log'],
                           help='Log file. (default={})'.format(defaults['log']))

    proc_args = parser.add_argument_group('General processing options')
    proc_args.add_argument('--sample_rate', metavar='N', type=int,
                           help='Sampling frequency of output audio. Resample is performed if necessary.')
    proc_args.add_argument('--random_seed', metavar='N', type=int,
                           help='Seed for random number generators. The current system time is used when this option is not used.')
    proc_args.add_argument('--cancel_dcoffset', action='store_true',
                           help='Unbias the DC offset.')
    proc_args.add_argument('--save_each_channel_in_onefile', action='store_true', 
                           help='Save each channel in a separate file.')

    mix_args = parser.add_argument_group('Mixer options')
    mix_args.add_argument('--mixers_configfile', metavar='FILE', 
                          help='Config file for building an array of mixers.')
    mix_args.add_argument('--save_image', action='store_true', 
                          help='Save source images instead of anechoic signals and RIRs.')

    return parser



if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
