#!/bin/bash

ROOTDIR=`dirname $0`

source $ROOTDIR/path.sh
DATADIR=$EXPROOT/data-orig



CWD=`pwd`
mkdir -p $DATADIR

cd $DATADIR

# wget
[ ! -f ./train-clean-100.tar.gz ] && wget --no-check-certificate http://www.openslr.org/resources/12/train-clean-100.tar.gz
[ ! -f ./train-clean-360.tar.gz ] && wget --no-check-certificate http://www.openslr.org/resources/12/train-clean-360.tar.gz
[ ! -f ./dev-clean.tar.gz ] && wget --no-check-certificate http://www.openslr.org/resources/12/dev-clean.tar.gz
[ ! -f ./test-clean.tar.gz ] && wget --no-check-certificate http://www.openslr.org/resources/12/test-clean.tar.gz

# unpack    
[ ! -d ./LibriSpeech/train-clean-100 ] && tar -zxvf train-clean-100.tar.gz
[ ! -d ./LibriSpeech/train-clean-360 ] && tar -zxvf train-clean-360.tar.gz
[ ! -d ./LibriSpeech/dev-clean ] && tar -zxvf dev-clean.tar.gz
[ ! -d ./LibriSpeech/test-clean ] && tar -zxvf test-clean.tar.gz

cd $CWD


