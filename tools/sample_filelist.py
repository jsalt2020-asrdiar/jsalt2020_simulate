#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, os, sys, random
import numpy as np



def main(args):
    # Make the results predictable.
    if args.random_seed is not None:
        random.seed(args.random_seed)
        np.random.seed(args.random_seed)

    # value check
    if args.subset_size < 0 or args.subset_size > 1:
        raise ValueError(f'subset_size must be between 0 and 1, but the given value is {args.subset_size}')

    # Read the source list. 
    with open(args.inlist) as f:
        orig_list = [l.strip() for l in f.readlines()]

    # Shuffle the list. 
    random.shuffle(orig_list)

    # Pick the first subset_size elements. 
    subset_size = int(np.floor(len(orig_list) * args.subset_size))
    with open(args.outlist, 'w') as f: 
        for i in range(subset_size):   
            print(orig_list[i], file=f)

    
def make_argparse():
    # Set up an argument parser. 
    parser = argparse.ArgumentParser(description='Sample a subset from a file list.')
    parser.add_argument('--inlist', metavar='<file>', required=True, 
                        help='Input file list.')
    parser.add_argument('--outlist', metavar='<file>', required=True,
                        help='Output file list.')
    parser.add_argument('--subset_size', metavar='<float>', type=float, required=True, 
                        help='Subset size relative to the original list. The value must be between 0 and 1.')
    parser.add_argument('--random_seed', metavar='N', type=int,
                        help='Seed for random number generators. The current system time is used when this option is not used.')
                        
    return parser
    
    
if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)
    
