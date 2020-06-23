#!/bin/bash

# Set bash to 'debug' mode, it will exit on :
# -e 'error', -u 'undefined variable', -o ... 'error in pipeline', -x 'print commands',
set -e
set -u
set -o pipefail


function print_usage_and_exit {
    CMD=`basename $0`    
    echo ""
    echo "    ''"
    echo "    < $CMD >"
    echo ""
    echo "    Usage: $CMD [--split N] [--help]"
    echo ""
    echo "    Description: Preprocess the original LibriSpeech data."
    echo ""
    echo "    Options: "
    echo "        --split N: Split the data set into N subsets for parallel processing. N defaults to 16."
    echo "        --help: Show this message."
    echo "    ''"
    echo ""
    exit 1
}


nj=16  # default parallel jobs

while [ $# -ge 1 ]
do
    if [ "${1:0:2}" != -- ]; then
        echo ""
        echo "ERROR: Invalid command line arguments."
        echo ""
        print_usage_and_exit
    elif [ "$1" == --help ] ; then
        print_usage_and_exit
    elif [ "$1" == --split ]; then
        shift
        nj=$1
        shift
    else
        echo ""
        echo "ERROR: Invalid option $1."
        echo ""
        print_usage_and_exit
    fi
done

if ! which realpath >/dev/null; then
    echo "realpath is not installed."
    exit 1
fi



# Import $EXPROOT. 
ROOTDIR=`dirname $0`/..
ROOTDIR=`realpath $ROOTDIR`
source $ROOTDIR/path.sh

# Subset of Kaldi utils
KALDI_UTILS=$ROOTDIR/tools/kaldi_utils

# Environment
export PATH=${KALDI_UTILS}:${PATH}
. $ROOTDIR/configs/cmd.sh

# Scripts
deflac=$ROOTDIR/tools/deflac.py
gen_filelist=$ROOTDIR/tools/gen_filelist.py
segment=$ROOTDIR/tools/tight_segment.py


srcdir=$EXPROOT/data-orig/LibriSpeech  # Has to contain train-clean100 and train-clean-360 from which FLAC files are retrieved. 

for set in train dev test 
do 
    dstdir=$EXPROOT/data/$set

    # Check if the output directory already exists. 
    if [ -d $dstdir ]; then
        echo 
        read -p "$dstdir already exists. OK to overwrite?" -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            continue
        else
            /bin/rm -f -r $dstdir
        fi        
    fi

    splitdir=$dstdir/filelist/split${nj}
    mkdir -p ${splitdir}/log

    # Convert FLAC files to WAV.
    if [ "$set" == train ]; then
        python $deflac --srcdir $srcdir/train-clean-100 $srcdir/train-clean-360 $srcdir/train-other-500 --dstdir $dstdir/wav
    else
        python $deflac --srcdir $srcdir/${set}-clean --dstdir $dstdir/wav
    fi

    # List the original wav files.
    if [ "$set" == train ]; then
        python $gen_filelist --srcdir $dstdir/wav/train-clean-100 $dstdir/wav/train-clean-360 $dstdir/wav/train-other-500 --outlist $dstdir/filelist/${set}.list
    else
        python $gen_filelist --srcdir $dstdir/wav/${set}-clean --outlist $dstdir/filelist/${set}.list
    fi        

    # Split trainlist for parallel processing
    split_scp.pl ${dstdir}/filelist/${set}.list $(for j in $(seq ${nj}); do echo ${splitdir}/${set}.${j}.list; done)

    # Remove silence regions. This allows us to accurately control the overlap ratio distribution duing training.
    ${gen_cmd} JOB=1:${nj} ${splitdir}/log/tight_segment.JOB.log \
        python $segment --inputlist ${splitdir}/${set}.JOB.list --outputdir ${dstdir}/wav_newseg
done

