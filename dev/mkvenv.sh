#!/bin/bash
# Usage: bin/mkvenv.sh [Options]

# Create a virtualenv, and install requirements to it.

# override the default python interpreter using
# `PYTHON=/path/to/python bin/bootstrap.sh`

# if [[ -n $VIRTUAL_ENV ]]; then
#     echo "You can't run this script inside an active virtualenv"
#     exit 1
# fi

set -e

abspath(){
    python -c "import os; print os.path.abspath(\"$1\")"
}

GREP_OPTIONS=--color=never

# defaults for options configurable from the command line
VENV=$(abspath $(basename $(pwd))-env)

PYTHON=$(which python)
PY_VERSION=$($PYTHON -c 'import sys; print "{}.{}.{}".format(*sys.version_info[:3])')
REQFILE=requirements.txt

if [[ $1 == '-h' || $1 == '--help' ]]; then
    echo "Create a virtualenv and install all pipeline dependencies"
    echo "Options:"
    echo "--venv            - path of virtualenv [$VENV]"
    echo "--python          - path to the python interpreter [$PYTHON]"
    echo "--requirements    - a file listing python packages to install [$REQFILE]"
    echo ""
    echo "--venv and --python are ignored if a virtualenv is active"
    exit 0
fi

while true; do
    case "$1" in
	--venv ) VENV="$2"; shift 2 ;;
	--python ) PYTHON="$2"; shift 2 ;;
	--requirements ) REQFILE="$2"; shift 2 ;;
	* ) break ;;
    esac
done

VENV_VERSION=1.11.6
SCONS_VERSION=2.3.1

mkdir -p src

# Create the virtualenv using a specified version of the virtualenv
# source. This also provides setuptools and pip. Inspired by
# http://eli.thegreenplace.net/2013/04/20/bootstrapping-virtualenv/

# create virtualenv if necessary
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo "using active virtualenv $VIRTUAL_ENV"
    VENV="$VIRTUAL_ENV"
else
    if [[ -f ${VENV:?}/bin/activate ]]; then
	echo "using inactive virtualenv $VENV"
    else
	echo "creating new virtualenv $VENV"
	if which virtualenv > /dev/null; then
	    virtualenv $VENV
	else
	    # download virtualenv source if necessary
	    if [[ ! -f src/virtualenv-${VENV_VERSION}/virtualenv.py ]]; then
		VENV_URL='https://pypi.python.org/packages/source/v/virtualenv'
		(cd src && \
			wget -N ${VENV_URL}/virtualenv-${VENV_VERSION}.tar.gz && \
			tar -xf virtualenv-${VENV_VERSION}.tar.gz)
	    fi
	    $PYTHON src/virtualenv-${VENV_VERSION}/virtualenv.py $VENV
	fi
    fi
    source $VENV/bin/activate
fi

# install python packages from pipy or wheels
grep -v -E '^#|git+|^-e' $REQFILE | while read pkg; do
    pip install $pkg
done

# scons can't be installed using pip
if [ ! -f $VENV/bin/scons ]; then
    (cd src && \
	wget -N http://downloads.sourceforge.net/project/scons/scons/${SCONS_VERSION}/scons-${SCONS_VERSION}.tar.gz && \
	tar -xf scons-${SCONS_VERSION}.tar.gz && \
	cd scons-${SCONS_VERSION} && \
	python setup.py install
    )
else
    echo "scons is already installed in $(which scons)"
fi

# install bioscons
pip install -U -e .
