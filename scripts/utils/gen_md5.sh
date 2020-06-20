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
    echo "    Usage: $CMD [--help] tgt-dir out-file"
    echo ""
    echo "    Description: Generate MD5 checksum values for all WAV files under the specified directory."
    echo ""
    echo "    Args: "
    echo "        tgt-dir : The MD5 hash values are generated for all WAV files under this directory."
    echo "        out-file: Output file to save the hash values."
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


tgtdir=`realpath $1`
outfile=`realpath $2`

if [ -f $outfile ]; then
    read -p "$outfile already exists. OK to rewrite? " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    else
        /bin/rm -f $outfile
    fi
fi

function write_checksum ()
{       while read line1; do
                md5sum $line1 >> $outfile
        done
}

pushd $tgtdir
ls -1 . | write_checksum
popd
