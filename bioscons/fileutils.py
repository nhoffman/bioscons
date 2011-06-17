import subprocess
import shutil
from os import path

from SCons.Script import *

def rename(fname, ext=None, pth=None):
    """
    Replace the directory or file extension in `fname` with `pth`
    and `ext`, respectively. `fname` may be a string, an object
    coercible to a string using str(), or a single-element list of
    either.
    """
    
    dirname, base, suffix = split_path(fname, split_ext = True)
    pth = pth or dirname
    ext = ext or suffix
    
    newname = os.path.join(pth, base) + ext    
    return newname
    
def split_path(fname, split_ext=False):
    """
    Returns file name elements given an absolute or relative path
    `fname`, which may be a string, an object coercible to a string
    using str(), or a single-element list of either. If `split_ext` is
    True, the name of the file is further split into a base component
    and the file suffix, ie, (dir, base, suffix), and (dir, filename)
    otherwise.
    """
    
    if isinstance(fname, list) or isinstance(fname, tuple) or hasattr(fname, 'pop'):
        fname = fname[0]
                
    fname = str(fname)
    # fname = path.abspath(str(fname))
        
    directory, filename = path.split(fname)

    if split_ext:
        base, suffix = path.splitext(filename)
        return (directory, base, suffix)
    else:
        return (directory, filename)

# def sub_ext(pth, ext=''):
#     """
#     Replace the file extension in `pth` with `sub`. `pth` may be a
#     string, an object coercible to a string using str(), or a
#     single-element list of either.
#     """

#     if isinstance(pth, list) or isinstance(pth, tuple) or hasattr(pth, 'pop'):
#         pth = pth[0]
                        
#     base, suffix = path.splitext(str(pth))
#     return base + ext
    
# copyfile
def _copyfile_emitter(target, source, env):
    """
    target - name of file or directory
    source - filename
    """

    (sname,) = map(str, source)
    (tname,) = map(str, target)

    if os.path.isdir(tname):
        target = path.join(tname, path.split(sname)[1])

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

