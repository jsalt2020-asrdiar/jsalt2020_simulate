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
    echo "    Usage: $CMD [--split N] [--cfg FILE] [--times N] [--subsample X] [--onespkr X] [--save_channels_separately] [--vad] [--save_image] [--help] dest-dir set"
    echo ""
    echo "    Description: Reverberate, mix, and noise-corrupt speech signals."
    echo ""
    echo "    Args: "
    echo "        dest-dir: Destination directory, relative to \$EXPROOT/data."
    echo "        set: {train|dev|eval}, subset to process."
    echo ""
    echo "    Options: "
    echo "        --split N                  : Split the data set into N subsets for parallel processing. N defaults to 32."    
    echo "        --cfg FILE                 : Simulation configuration file. FILE defaults to <repo-root>/configs/2mix_reverb_stanoise.json."
    echo "        --times N                  : Each utterance is used N times. This could be used for data augmentation. N defaults to 1."
    echo "        --subsample X              : Use X*100 % of the files."
    echo "        --onespkr X                : Probability with which a purely single speaker sample is generated."
    echo "        --vad                      : Use VAD-segmented signals."
    echo "        --save_image               : Save source images instead of anechoic signals and RIRs."
    echo "        --save_channels_separately : Save each output channel separately."
    echo "        --help                     : Show this message."
    echo "    ''"
    echo ""
    exit 1
}


nj=32  # default parallel jobs

while true
do 
    if [ $# -eq 0 ]; then
        echo ""
        echo "ERROR: Invalid command line arguments."
        echo ""
        print_usage_and_exit
    fi

    if [ "${1:0:2}" != -- ]; then
        break
    fi

    if [ "$1" == --help ] ; then
        print_usage_and_exit
    elif [ "$1" == --vad ]; then
        vad=
        shift
    elif [ "$1" == --save_channels_separately ]; then
        save_channels_separately=
        shift
    elif [ "$1" == --save_image ]; then
        save_image=
        shift
    elif [ "$1" == --split ]; then
        shift
        nj=$1
        shift
    elif [ "$1" == --cfg ]; then
        shift
        cfgfile=$1
        shift
    elif [ "$1" == --times ]; then
        shift
        ncopies=$1
        shift
    elif [ "$1" == --subsample ]; then
        shift
        subsample=$1
        shift
    elif [ "$1" == --onespkr ]; then
        shift
        single_spkr=$1
        shift
    else
        echo ""
        echo "ERROR: Invalid option $1."
        echo ""
        print_usage_and_exit
    fi
done

if [ $# -ne 2 ]; then
    echo ""
    echo "ERROR: Invalid command line arguments."
    echo ""
    print_usage_and_exit
fi

if ! which realpath >/dev/null; then
    echo "realpath is not installed."
    exit 1
fi


# Import $EXPROOT. 
ROOTDIR=`dirname $0`/..
ROOTDIR=`realpath $ROOTDIR`
source $ROOTDIR/path.sh

# a subset of Kaldi utils
KALDI_UTILS=$ROOTDIR/tools/kaldi_utils

# Environment
export PATH=${KALDI_UTILS}:${PATH}
. $ROOTDIR/configs/cmd.sh

# Scripts
splitjson=$ROOTDIR/tools/splitjson.py
mergejson=$ROOTDIR/tools/mergejsons.py
gen_filelist=$ROOTDIR/tools/gen_filelist.py
sample_filelist=$ROOTDIR/tools/sample_filelist.py
list2json=$ROOTDIR/tools/list2json_librispeech.py
mixspec=$ROOTDIR/tools/gen_mixspec_2spkr.py
mixer=$ROOTDIR/tools/mixaudio.py

# Directories
set=$2
if [ -v vad ]; then
    srcdir=$EXPROOT/data/${set}/wav_newseg  # VAD-segmented signals
else
    srcdir=$EXPROOT/data/${set}/wav  # original signals
fi
tgtroot=$EXPROOT/data/$1

# Hyper-parameters
if [ ! -v ncopies ]; then
    ncopies=1
fi
if [ ! -v single_spkr ]; then
    single_spkr=0.08
fi
if [ ! -v cfgfile ]; then
    cfgfile=$ROOTDIR/configs/common/2mix_reverb_stanoise.json
fi

# List the source files. 
datalist=$tgtroot/${set}.list
python $gen_filelist --srcdir $srcdir --outlist $datalist

# Subsample the files. 
if [ -v subsample ]; then
    python $sample_filelist --inlist $datalist --outlist $datalist --subset_size $subsample
fi

# Split datalist for parallel processing
splitdir=${tgtroot}/split${nj}
mkdir -p ${splitdir}/log
split_scp.pl ${datalist} $(for j in $(seq ${nj}); do echo ${splitdir}/${set}.${j}.list; done)

# Create a JSON file for the source data set. (~10 min with nj=32)
datajson=$tgtroot/${set}.json
if [ -v vad ]; then
    ${gen_cmd} JOB=1:${nj} ${splitdir}/log/list2json.JOB.log \
        python $list2json --input_list ${splitdir}/${set}.JOB.list --output_file ${splitdir}/${set}.JOB.json
else
    ${gen_cmd} JOB=1:${nj} ${splitdir}/log/list2json.JOB.log \
        python $list2json --input_list ${splitdir}/${set}.JOB.list --novad --output_file ${splitdir}/${set}.JOB.json
fi

python $mergejson $(for j in $(seq ${nj}); do echo ${splitdir}/${set}.${j}.json; done) > $datajson

# Generate mixture specs. 
tgtdir=$tgtroot/wav
specjson=$tgtroot/mixspec.json
python $mixspec --inputfile $datajson --outputfile $specjson --ncopies $ncopies --random_seed 0 --single_speaker_percentage $single_spkr --targetdir $tgtdir

# Split $tgtroot/mixspec.json into several smaller json files: $splitdir/mixspec.JOB.json
python $splitjson --inputfile $specjson --number_splits $nj --outputdir $splitdir

# Generate mixed audio files. 
mixlog=$tgtroot/mixlog.json
if [ -v save_channels_separately ]; then
    opts='--save_each_channel_in_onefile'
else
    opts=''
fi
if [ -v save_image ]; then
    opts="$opts --save_image"
fi
${gen_cmd} JOB=1:${nj} ${splitdir}/log/mixlog.JOB.log \
    python $mixer $opts --iolist ${splitdir}/mixspec.JOB.json --cancel_dcoffset --random_seed JOB --mixers_configfile $cfgfile --sample_rate 16000 --log ${splitdir}/mixlog.JOB.json
python $mergejson $(for j in $(seq ${nj}); do echo ${splitdir}/mixlog.${j}.json; done) > $mixlog
