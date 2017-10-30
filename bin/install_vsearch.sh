#!/bin/bash

# Install vsearch to $prefix/bin

set -e

source $(dirname $0)/argparse.bash || exit 1
argparse "$@" <<EOF || exit 1
parser.add_argument('--version', default='1.11.1', help='vsearch version [%(default)s]')
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

vsearch_is_installed(){
    $prefix/bin/vsearch --version 2> /dev/null | grep -q "$VERSION"
}

if vsearch_is_installed; then
    echo -n "vsearch is already installed: "
    $prefix/bin/vsearch --version
    exit 0
fi

mkdir -p $srcdir
cd $srcdir

gh_dl=https://github.com/torognes/vsearch/releases/download
wget -nc $gh_dl/v${version}/vsearch-${version}-linux-x86_64.tar.gz
tar -xf vsearch-${version}-linux-x86_64.tar.gz
cp vsearch-${version}-linux-x86_64/bin/vsearch $prefix/bin

vsearch_is_installed || (echo "error installing vsearch $VERSION"; exit 1)
