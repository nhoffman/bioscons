"""Extends the scons build tool for reproducible research in bioinformatics.

"""

import glob
import sys
import imp
import subprocess
from os import path
from distutils.version import LooseVersion

MIN_SCONS_VERSION = '2.1.0'
_data = path.join(path.dirname(__file__), 'data')


def add_scons_lib(scons='scons', min_scons_version=MIN_SCONS_VERSION):
    """If `SCons` is not importable, update sys.path (side effect
    warning!), and then return False. Return True without modifying
    sys.path if importing `SCons` succeeds.

    The scons library is identified using the location and version of
    the `scons` executable,

    Raises `ImportError` if `scons` cannot be found or executed, if
    the library is not in the expected location relative to the scons
    executable, or if the version of the SCons package is at least
    `min_scons_version`.

    """

    try:
        import SCons
    except ImportError:
        try:
            scons_path = subprocess.check_output(['which', scons]).strip()
        except subprocess.CalledProcessError:
            raise ImportError('"{}" could not be found or executed'.format(scons))

        scons_mod = imp.load_source('scons', scons_path)
        root = path.split(path.split(scons_path)[0])[0]
        libpath = path.join(root, 'lib', scons_mod.scons_version)
        if not path.exists(libpath):
            raise ImportError('The path "{}" cound not be found'.format(libpath))

        sys.path.insert(0, libpath)
        retval = False
    else:
        retval = True

    import SCons

    if not LooseVersion(SCons.__version__) >= LooseVersion(min_scons_version):
        raise ImportError('The version of scons is not at least {}'.format(min_scons_version))

    return retval


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
except Exception as e:
    sys.stderr.write('Error: cannot read {}/ver\n'.format(_data))
    ver = 'v0.0.0.unknown'

__version__ = ver.lstrip('v')
