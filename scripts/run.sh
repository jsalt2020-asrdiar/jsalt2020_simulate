#!/bin/bash

# Programs
# Takuya's set-up
PYTHON=/usr/bin/python3.8

# Scripts
deflac=./tools/deflac.py
gen_filelist=./tools/gen_filelist.py
segment=./tools/tight_segment.py

# Directories
# Takuya's set-up
srcdir=/mnt/f/DB/LibriSpeech/train  # Has to contain train-clean100 and train-clean-360 from which FLAC files are retrieved. 
dstdir=/mnt/f/Work/JelinekWorkshop2020/data/train

# Convert FLAC files to WAV.
$PYTHON $deflac --srcdir $srcdir/train-clean-100 $srcdir/train-clean-360 --dstdir $dstdir/wav

# List the original wav files. 
$PYTHON $gen_filelist --srcdir $dstdir/wav/train-clean-100 $dstdir/wav/train-clean-360 --outlist $dstdir/filelist/train.list


