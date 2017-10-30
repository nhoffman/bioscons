#!/bin/bash

# Install infernal (cmalign) and selected easel binaries to $prefix/bin

set -e

source $(dirname $0)/argparse.bash || exit 1
argparse "$@" <<EOF || exit 1
parser.add_argument('--version', default='1.1', help='version [%(default)s]')
parser.add_argument('--prefix', default='/usr/local',
                    help='base dir for install [%(default)s]')
parser.add_argument('--srcdir',
                    help='directory to download and compile source [PREFIX/src]')
EOF

version="$VERSION"
prefix=$(readlink -f "$PREFIX")

if [[ -z $SRCDIR ]]; then
    srcdir="$prefix/src"
else
    srcdir="$SRCDIR"
fi

cmalign_is_installed(){
    "$prefix/bin/cmalign" -h 2> /dev/null | grep -q "INFERNAL $VERSION"
}

if cmalign_is_installed; then
    echo "cmalign $VERSION is already installed"
    exit 0
fi

mkdir -p "$srcdir"
cd "$srcdir"

INFERNAL=infernal-${VERSION}-linux-intel-gcc
wget -nc http://eddylab.org/software/infernal/${INFERNAL}.tar.gz
for binary in cmalign cmconvert esl-alimerge esl-sfetch esl-reformat; do
    tar xvf "${INFERNAL}.tar.gz" --no-anchored "binaries/$binary"
done
cp ${INFERNAL}/binaries/* "$prefix/bin"
rm -r "${INFERNAL}"

if ! cmalign_is_installed; then
    echo "error installing cmalign $VERSION" to "$prefix"
    exit 1
fi
