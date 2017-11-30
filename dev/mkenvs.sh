#!/bin/bash

if [[ ! -z $VIRTUAL_ENV ]]; then
    echo "deactivate the venv first!"
    exit 1
fi

scons='scons==3.0.1'

rm -rf py2-env
virtualenv py2-env
py2-env/bin/pip install -U pip wheel
py2-env/bin/pip install -U "$scons"
py2-env/bin/pip install -U -e .

rm -rf py3-env
python3 -m venv py3-env
py3-env/bin/pip install -U pip wheel
py3-env/bin/pip install -U "$scons"
py3-env/bin/pip install -U -e .
