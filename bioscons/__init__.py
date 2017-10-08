"""Extends the scons build tool for reproducible research in bioinformatics.

"""

import glob
import sys
import imp
import subprocess
from os import path
from distutils.version import LooseVersion

MIN_SCONS_VERSION = '2.4.0'
_data = path.join(path.dirname(__file__), 'data')


def add_scons_lib(min_scons_version=MIN_SCONS_VERSION):
    """If `SCons` is not importable, update sys.path (side effect
    warning!).

    The scons library is identified using the location and version of
    the `scons` executable,

    """

    try:
        scons_path = subprocess.check_output(
            ['which', 'scons'], universal_newlines=True).strip()
    except subprocess.CalledProcessError:
        raise ImportError('"{}" could not be found or executed'.format('scons'))

    scons_mod = imp.load_source('scons', scons_path)

    if not LooseVersion(scons_mod.__version__) >= LooseVersion(min_scons_version):
        raise ImportError(
            'scons version >= {} is required'.format(min_scons_version))

    root = path.split(path.split(scons_path)[0])[0]
    libpath = path.join(root, 'lib',
                        'python{}.{}'.format(*sys.version_info[:2]),
                        'site-packages', scons_mod.scons_version)
    if not path.exists(libpath):
        raise ImportError('The path "{}" cound not be found'.format(libpath))

    sys.path.insert(0, libpath)
    return libpath


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
    with open(package_data('ver')) as f:
        __version__ = (
            f.read().strip().replace('-', '+', 1).replace('-', '.').lstrip('v'))
except Exception as e:
    __version__ = ''
