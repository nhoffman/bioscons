#!/bin/bash

# Install FastTree tools to $prefix/bin

set -e

source $(dirname $0)/argparse.bash || exit 1
argparse "$@" <<EOF || exit 1
parser.add_argument('--version', default='2.1.8', help='FastTree version [%(default)s]')
parser.add_argument('--prefix', default='/usr/local', help='base dir for install [%(default)s]')
parser.add_argument('--srcdir', help='directory to download and compile source [PREFIX/src]')
EOF

version="$VERSION"
prefix=$(readlink -f "$PREFIX")

if [[ -z $SRCDIR ]]; then
    srcdir="$prefix/src"
else
    srcdir="$SRCDIR"
fi

if $prefix/bin/FastTree -help 2>&1 | grep -q $version &&
   $prefix/bin/FastTreeMP -help 2>&1 | grep -q $version ; then
    echo "FastTree version $version is already installed in $prefix/bin"
    exit 0
fi

mkdir -p $srcdir
cd $srcdir

# Download and compile single-threaded FastTree
wget -N http://microbesonline.org/fasttree/FastTree-$version.c
gcc -DUSE_DOUBLE -Wall -O3 -finline-functions -funroll-loops -o FastTree FastTree-$version.c -lm

# Download and compile multi-threaded FastTree
gcc -DUSE_DOUBLE -DOPENMP -fopenmp -O3 -finline-functions \
    -funroll-loops -Wall -o FastTreeMP FastTree-$version.c -lm
chmod a+x FastTree FastTreeMP

mv FastTree $prefix/bin/
mv FastTreeMP $prefix/bin/

# confirm success
$prefix/bin/FastTree -help 2>&1 | grep $version
$prefix/bin/FastTreeMP -help 2>&1 | grep $version
