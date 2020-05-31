#!/bin/bash

# Set the number of splits for parallel processing. 
nj=16
if [ $# -ge 3 ] || [ $# -eq 1 ]; then
    CMD=`basename $0`
    echo "Usage: $CMD [--split] <#nsubsets>"
    echo "  e.g.: $CMD --split 16"
    echo "  By default, the split value is set to 16."
    exit 1
fi
if [ $# -eq 2 ]; then
    if [ "$1" == --split ]; then
        nj=$2
    else
        CMD=`basename $0`
        echo "Usage: $CMD [--split] <#nsubsets>"
        echo "e.g.: $CMD --split 16"
        echo "By default, the split value is set to 16."
        exit 1
    fi
fi

if ! which realpath >/dev/null; then
    echo "realpath is not installed."
    exit 1
fi

# Import $EXPROOT. 
ROOTDIR=`dirname $0`/..
ROOTDIR=`realpath $ROOTDIR`
source $ROOTDIR/path.sh

# Set bash to 'debug' mode, it will exit on :
# -e 'error', -u 'undefined variable', -o ... 'error in pipeline', -x 'print commands',
set -e
set -u
set -o pipefail

PYTHON=python

# a subset of Kaldi utils
KALDI_UTILS=$ROOTDIR/tools/kaldi_utils

# Environment
export PATH=${KALDI_UTILS}:${PATH}
. $ROOTDIR/configs/cmd.sh

# Scripts
deflac=$ROOTDIR/tools/deflac.py
gen_filelist=$ROOTDIR/tools/gen_filelist.py
segment=$ROOTDIR/tools/tight_segment.py

# Directories
srcdir=$EXPROOT/data-orig/LibriSpeech  # Has to contain train-clean100 and train-clean-360 from which FLAC files are retrieved. 
dstdir=$EXPROOT/data/train
splitdir=$dstdir/filelist/split${nj}
mkdir -p ${splitdir}/log

# Convert FLAC files to WAV.
$PYTHON $deflac --srcdir $srcdir/train-clean-100 $srcdir/train-clean-360 --dstdir $dstdir/wav

# List the original wav files.
$PYTHON $gen_filelist --srcdir $dstdir/wav/train-clean-100 $dstdir/wav/train-clean-360 --outlist $dstdir/filelist/train.list

# Split trainlist for parallel processing
split_scp.pl ${dstdir}/filelist/train.list $(for j in $(seq ${nj}); do echo ${splitdir}/train.${j}.list; done)

# Remove silence regions from the training utterances. This allows us to accurately control the overlap ratio distribution duing training.
${gen_cmd} JOB=1:${nj} ${splitdir}/log/tight_segment.JOB.log \
    $PYTHON $segment --inputlist ${splitdir}/train.JOB.list --outputdir ${dstdir}/wav_newseg
