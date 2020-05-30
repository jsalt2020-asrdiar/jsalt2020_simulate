#!/bin/bash

ROOTDIR=`dirname $0`

source $ROOTDIR/path.sh
DATADIR=$EXPROOT/data-orig



if [ -d $DATADIR ]
then
    echo "Downloading LibriSpeech training data."    
    CWD=`pwd`
    mkdir -p $DATADIR

    cd $DATADIR

    # wget
    wget --no-check-certificate http://www.openslr.org/resources/12/train-clean-100.tar.gz
    wget --no-check-certificate http://www.openslr.org/resources/12/train-clean-360.tar.gz

    # unpack    
    tar -zxvf train-clean-100.tar.gz
    tar -zxvf train-clean-360.tar.gz

    cd $CWD
fi


