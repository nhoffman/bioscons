#!/bin/bash

# Install OPAM (binary) and the ocaml interpreter (compiled), and
# pplacer and dependencies (compiled). Requires various system
# dependencies described here:
# http://matsen.github.io/pplacer/compiling.html
#

# System install
# ==============

# This is the default: pplacer and opam binaries will be installed to
# /usr/local/bin, and ocaml interpreter and dependencies will be placed
# in /usr/loca/share/opam

# Local install with shared OPAM
# ==============================

# Use this option, for example, when working on a shared resource (and
# can't install to the system) and want to install a different version
# of pplacer in each of several projects. In this case you could, for
# example, create a virtualenv within a project and use::

#   bin/install_pplacer.sh --prefix /path/to/virtualenv --opamroot ~/opam --srcdir ~/src

# The contents of ~/opam and ~/src can then be reused by subsequent
# installations (and only pplacer will need to be recompiled each time).

# Everything is local
# ===================

# You're a hard-core reproducible researcher and want all of your
# dependencies for a project to be local. Good for you! It will only
# cost ~700M on disk or so...::

#   bin/install_pplacer.sh --prefix /path/to/virtualenv

function abspath(){
    # no readlink -f on Darwin, unfortunately
    python -c "import os; print os.path.abspath(\"$1\")"
}

set -e

PREFIX=/usr/local
SRCDIR=/usr/local/src

OPAM_VERSION='1.1.0'
OCAML_VERSION='3.12.1'
PPLACER_VERSION=master
PIP=$(which pip || echo "")

if [[ $1 == '-h' || $1 == '--help' ]]; then
    echo "Install OPAM, the ocaml interpreter, and pplacer"
    echo "Options:"
    echo "--prefix          - base dir for binaries (eg, \$PREFIX/bin/pplacer) [$PREFIX]"
    echo "--srcdir          - path for downloads and compiling [$SRCDIR]"
    echo "--opamroot        - sets \$OPAMROOT [\$PREFIX/share/opam]"
    echo "--pip             - path to pip for installing python scripts [$PIP]"
    echo "--pplacer-version - git branch, tag, or sha [$PPLACER_VERSION]"
    echo "--opam-version    - opam binary version [$OPAM_VERSION]"
    echo "--ocaml-version   - ocaml interpreter version [$OCAML_VERSION]"
    exit 0
fi

while true; do
    case "$1" in
	--prefix ) PREFIX="$(abspath $2)"; shift 2 ;;
	--srcdir ) SRCDIR="$(abspath $2)"; shift 2 ;;
	--opamroot ) OPAMROOT="$(abspath $2)"; shift 2 ;;
	--pip ) PIP="$(abspath $2)"; shift 2 ;;
	--pplacer-version ) PPLACER_VERSION="$2"; shift 2 ;;
	--opam-version ) OPAM_VERSION="$2"; shift 2 ;;
	--ocaml-version ) OCAML_VERSION="$2"; shift 2 ;;
	* ) break ;;
    esac
done

if [[ ! -w $PREFIX ]]; then
    echo "$PREFIX is not writable - you probably want to run using sudo"
    exit 1
fi

OPAMROOT=${OPAMROOT-$PREFIX/share/opam}

mkdir -p $SRCDIR

# Install OPAM; see http://opam.ocaml.org/doc/Quick_Install.html -
# below is a greatly simplified version of
# http://www.ocamlpro.com/pub/opam_installer.sh
OPAM=$PREFIX/bin/opam
if $OPAM --version | grep -q $OPAM_VERSION; then
    echo "opam version $OPAM_VERSION is already installed in $PREFIX/bin"
else
    OPAM_FILE="opam-${OPAM_VERSION}-$(uname -m)-$(uname -s)"
    wget -P $SRCDIR -N http://www.ocamlpro.com/pub/$OPAM_FILE
    chmod +x $SRCDIR/$OPAM_FILE
    cp $SRCDIR/$OPAM_FILE $PREFIX/bin
    ln -f $PREFIX/bin/$OPAM_FILE $OPAM
fi

$OPAM init --root $OPAMROOT --comp $OCAML_VERSION --no-setup

eval $($OPAM config --root $OPAMROOT env)

# Install remote repository for pplacer
if $OPAM repo list | grep -q pplacer-deps; then
    echo pplacer-deps is already a remote repository
else
    $OPAM repo add pplacer-deps http://matsen.github.com/pplacer-opam-repository
fi

$OPAM update pplacer-deps

PPLACER_SRC=$SRCDIR/pplacer-${PPLACER_VERSION}
# rm -rf $PPLACER_SRC
# git clone https://github.com/matsen/pplacer.git $PPLACER_SRC

if [[ -d $PPLACER_SRC ]]; then
    (cd $PPLACER_SRC && git pull)
else
    git clone https://github.com/matsen/pplacer.git $PPLACER_SRC
fi

cd $PPLACER_SRC
git checkout $PPLACER_VERSION

# Note: batteries.2.0.0 fails to build under OCaml 4.01.0
for dep in $(cat opam-requirements.txt); do
    $OPAM install -y $dep
done

make
cp $PPLACER_SRC/bin/{pplacer,guppy,rppr} $PREFIX/bin

# install python scripts
if [[ ! -z $PIP ]]; then
    $PIP install -U $PPLACER_SRC/scripts
else
    python setup.py install $PPLACER_SRC/scripts --prefix=$PREFIX
fi
