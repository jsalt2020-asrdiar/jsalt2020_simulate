#!/bin/bash

# Set bash to 'debug' mode, it will exit on :
# -e 'error', -u 'undefined variable', -o ... 'error in pipeline', -x 'print commands',
set -e
set -u
set -o pipefail

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

PYTHON=python

# a subset of Kaldi utils
KALDI_UTILS=$ROOTDIR/tools/kaldi_utils

# Environment
export PATH=${KALDI_UTILS}:${PATH}
. $ROOTDIR/configs/cmd.sh

# Scripts
splitjson=$ROOTDIR/tools/splitjson.py
mergejson=$ROOTDIR/tools/mergejsons.py
gen_filelist=$ROOTDIR/tools/gen_filelist.py
list2json=$ROOTDIR/tools/list2json_librispeech.py
mixspec=$ROOTDIR/tools/gen_mixspec_mtg.py
mixer=$ROOTDIR/tools/mixaudio_mtg.py

# Directories
srcdir=$EXPROOT/data/train/wav_newseg  # Generated by preprocess.sh. Use $EXPROOT/data/train/wav if you want to use the unprocessed LibriSpeech files. In that case, add --novad to $list2json. 
tgtroot=$EXPROOT/data/LibriCSS-train-meetings

# Hyper-parameters
overlap_time_ratio=0.3
utterances_per_speaker=3
speakers_per_session=3

# List the source files. 
trainlist=$tgtroot/train.list
$PYTHON $gen_filelist --srcdir $srcdir --outlist $trainlist

# Split trainlist for parallel processing
splitdir=${tgtroot}/split${nj}
mkdir -p ${splitdir}/log
split_scp.pl ${trainlist} $(for j in $(seq ${nj}); do echo ${splitdir}/train.${j}.list; done)

# Create a JSON file for the source data set. (~10 min with nj=32)
trainjson=$tgtroot/train.json
${gen_cmd} JOB=1:${nj} ${splitdir}/log/list2json.JOB.log \
    $PYTHON $list2json --input_list ${splitdir}/train.JOB.list --output_file ${splitdir}/train.JOB.json

$PYTHON $mergejson $(for j in $(seq ${nj}); do echo ${splitdir}/train.${j}.json; done) > $trainjson

# Generate mixture specs. 
tgtdir=$tgtroot/wav
specjson=$tgtroot/mixspec.json
$PYTHON $mixspec --inputfile $trainjson --outputfile $specjson --targetdir $tgtdir --speakers $speakers_per_session --utterances_per_speaker $utterances_per_speaker --overlap_time_ratio $overlap_time_ratio

# Split $tgtroot/mixspec.json into several smaller json files: $splitdir/mixspec.JOB.json
$PYTHON $splitjson --inputfile $specjson --number_splits $nj --outputdir $splitdir

# Generate mixed audio files. 
mixlog=$tgtroot/mixlog.json
${gen_cmd} JOB=1:${nj} ${splitdir}/log/mixlog.JOB.log \
    $PYTHON $mixer --iolist ${splitdir}/mixspec.JOB.json --cancel_dcoffset --sample_rate 16000 --log ${splitdir}/mixlog.JOB.json
$PYTHON $mergejson $(for j in $(seq ${nj}); do echo ${splitdir}/mixlog.${j}.json; done) > $mixlog
