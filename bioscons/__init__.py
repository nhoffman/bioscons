"""Extends the scons build tool for reproducible research in bioinformatics.

"""

import glob
import sys
from os import path

_data = path.join(path.dirname(__file__), 'data')


def package_data(fname, pattern=None):
    """Return the absolute path to a file included in package data
    (bioscons/data), raising ValueError if no such file exists. If
    `pattern` is provided, return a list of matching files in package
    data (ignoring `fname`).

    """

    if pattern:
        return glob.glob(path.join(_data, pattern))

    pth = path.join(_data, fname)

    if not path.exists(pth):
        raise ValueError('Package data does not contain the file %s' % fname)

    return pth

try:
    with open(package_data('ver')) as v:
        ver = v.read().strip()
except Exception, e:
    sys.stderr.write('Error: cannot read {}/ver\n'.format(_data))
    ver = 'v0.0.0.unknown'

__version__ = ver.lstrip('v')
