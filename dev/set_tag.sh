#!/bin/bash

set -e

version=$(python -c "import bioscons; print bioscons.__version__")

git tag -a -m "version $version" v$version
echo -n "updated tag, now on tag "
git describe
