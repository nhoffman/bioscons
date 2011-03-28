import subprocess
import shutil
from os.path import join,split,splitext

from SCons.Script import *

# copyfile
def copyfile_emitter(target, source, env):
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
    emitter=copyfile_emitter,
    action='cp $SOURCE $TARGET'
    )

# bunzip2
def bunzip2_emitter(target, source, env):
    """
    Decompress source file, keeping original.

    target - name of source with .bz2 suffix removed
    source - file compressed using bzip2
    """

    (sname,) = map(str, source)
    return sname.replace('.bzip2',''), source

bunzip2 = Builder(
    action = 'bunzip2 --keep $SOURCE'
    )

