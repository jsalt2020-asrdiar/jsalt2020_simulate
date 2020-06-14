#!/bin/bash

if [ $# -ne 1 ]
then
    CMD=`basename $0`
    echo "Usage: $CMD <your-data-dir>"
    echo "e.g.: $CMD /data/tayoshio/jsalt2020_simulate"
    exit 1
fi



# Check if necessary tools are installed.
if ! which realpath >/dev/null; then
    echo "realpath is not installed."
    exit 1
fi
if ! which git >/dev/null; then
    echo "git is not installed."
    exit 1
fi


# Check if the directory exists. 
if [ -d $1 ]; then
    read -p "$1 already exists. OK to overwrite it? " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]
    then
        exit 1
    fi
else
    /bin/mkdir -p $1
fi


ROOTDIR=`dirname $0`
ROOTDIR=`realpath $ROOTDIR`
RIRGENPATH=$ROOTDIR/external_tools/rir-generator
EXPROOT=`realpath $1`



##
## Installing rir-generator
##
if [ ! -d $RIRGENPATH ]
then
    read -p "Installing rir-generator in $RIRGENPATH. Hit Enter or type an alternative install path name: " ret
    if [ ! -z "$ret" ]
    then
        RIRGENPATH=$ret
    fi

    if [ ! -d $RIRGENPATH ]
    then
        CWD=`pwd`
        git clone https://github.com/Marvin182/rir-generator.git $RIRGENPATH
        cd $RIRGENPATH/python
        make
        python setup.py install
        cd $CWD
    else
        echo "$RIRGENPATH exists. Skip rir-generator installation."    
    fi
fi



##
## Generate path.sh
##
echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:$RIRGENPATH/python" > $ROOTDIR/path.sh
echo "export PYTHONPATH=\$PYTHONPATH:$RIRGENPATH/python" >> $ROOTDIR/path.sh
echo "export EXPROOT=$EXPROOT" >> $ROOTDIR/path.sh
