#!/bin/bash

function print_usage_and_exit {
    CMD=`basename $0`    
    echo ""
    echo "    ''"
    echo "    < $CMD >"
    echo ""
    echo "    Usage: $CMD [--help] tgt-dir type set"
    echo ""
    echo "    Description: Check if your generated data are the same as those produced by others with the default settings. This ensures reproducibility of results across sites."
    echo ""
    echo "    Args: "
    echo "        tgt-dir : Simulation data directory where WAV files are retrievied."
    echo "        type    : {mtg|utt}, simulation type."
    echo "        set     : {train|dev|eval}, subset name."
    echo ""
    echo "    Options: "
    echo "        --help      : Show this message."
    echo "    ''"
    echo ""
    exit 1
}


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
    else
        echo ""
        echo "ERROR: Invalid option $1."
        echo ""
        print_usage_and_exit
    fi
done

if [ $# -ne 3 ]; then
    echo ""
    echo "ERROR: Invalid command line arguments."
    echo ""
    print_usage_and_exit
fi

if ! which realpath >/dev/null; then
    echo "realpath is not installed."
    exit 1
fi


tgtdir=`realpath $1`
type=$2
set=$3

if [ $type != "utt" ] && [ $type != "mtg" ]; then
    echo ""
    echo "ERROR: type must be utt or mtg: $type"
    echo ""
    print_usage_and_exit
fi
if [ $set != "train" ] && [ $set != "dev" ] && [ $set != "test" ]; then
    echo ""
    echo "ERROR: set must be train, dev, or test: $set"
    echo ""
    print_usage_and_exit
fi

ROOTDIR=`dirname $0`/..
ROOTDIR=`realpath $ROOTDIR`
md5file=$ROOTDIR/materials/md5sum/v0.0.1/${type}-${set}.txt

pushd $tgtdir > /dev/null
md5sum -c $md5file | grep -v OK
if [ $? -eq 0 ]; then  # Note that this is checking if "grep -v" was successful (which means md5sum checksums did not match).
    echo ""
    echo "TEST FAILED."
    echo ""
else
    echo ""
    echo "TEST PASSED."
    echo ""
fi
popd > /dev/null

