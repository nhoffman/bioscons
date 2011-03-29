import subprocess
import shutil
from os.path import join, split, splitext, abspath

from SCons.Script import *

def split_path(path, split_ext=True):
    """
    Returns file name elements given `path`, which may be a string, an
    object coercible to a string using str(), or a single-element list
    of either. If `split_ext` is True, the name of the file is further
    split into a base component and the file suffix, ie, (pth, base,
    suffix), and (pth, filename, None) otherwise.
    """

    if isinstance(path, list) or isinstance(path, tuple):
        path = path[0]
        
    pth, filename = split(str(path))

    if split_ext:
        base, suffix = splitext(filename)
        return (abspath(pth), base, suffix)
    else:
        return (abspath(pth), filename, None)

# copyfile
def _copyfile_emitter(target, source, env):
    """
    target - name of file or directory
    source - filename
    """

    (sname,) = map(str, source)
    (tname,) = map(str, target)

    if os.path.isdir(tname):
        target = join(tname, split(sname)[1])

    return target, source

copyfile = Builder(
    emitter=_copyfile_emitter,
    action='cp $SOURCE $TARGET'
    )

# bunzip2
def _bunzip2_emitter(target, source, env):
    """
    Decompress source file, keeping original.

    target - name of source with .bz2 suffix removed
    source - file compressed using bzip2
    """
        
    (sname,) = map(str, source)
    return sname.replace('.bz2',''), source

bunzip2 = Builder(
    emitter = _bunzip2_emitter,
    action = 'bunzip2 --keep $SOURCE'
    )

