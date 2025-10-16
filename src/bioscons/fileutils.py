import hashlib
import os
from os import path

try:
    from SCons.Script import Flatten, Builder
except ImportError:
    pass
else:
    def _copyfile_emitter(target, source, env):
        """
        target - name of file or directory
        source - filename
        """

        (sname,) = list(map(str, source))
        (tname,) = list(map(str, target))

        if os.path.isdir(tname):
            target = path.join(tname, path.split(sname)[1])

        return target, source

    copyfile = Builder(
        emitter=_copyfile_emitter,
        action='cp $SOURCE $TARGET'
    )

    def _bunzip2_emitter(target, source, env):
        """
        Decompress source file, keeping original.

        target - name of source with .bz2 suffix removed
        source - file compressed using bzip2
        """

        (sname,) = list(map(str, source))
        return sname.replace('.bz2', ''), source

    bunzip2 = Builder(
        emitter = _bunzip2_emitter,
        action = 'bunzip2 --keep $SOURCE'
        )

    class Targets(object):
        """
        Provides an object with methods for identifying objects in the
        local namespace representing build targets and to compare this
        list to the contents of a directory to idenify extraneous files.

        Example usage::

          from bioscons.fileutils import Targets
          targets = Targets()
          # build some targets
          some_target = env.Command(
              target='infile.txt', source='outfile.txt',
              action='some_action $SOURCE $TARGET')

          targets.update(locals().values())
          targets.show_extras("outdir")
        """

        def __init__(self, objs = None):
            self.targets = self.update(objs) if objs else set()

        def update(self, objs):
            """
            Given a list of objects (eg, the output of ``locals().values()``),
            update self.targets with the set containing the relative path
            to each target (ie, those objects with a "NodeInfo"
            attribute).
            """

            self.targets.update(
                set(str(obj) for obj in Flatten(objs) if hasattr(obj, 'NodeInfo')))

        def show_extras(self, directory, one_line = True):
            """
            Given a relative path ``directory`` search for files recursively
            and print a list of those not found among
            ``self.targets``. Print one path per line if ``one_line`` is
            False.
            """

            outfiles = set(
                Flatten([[path.join(d, f) for f in ff]
                         for d, _, ff in os.walk(directory)]))

            extras = outfiles - self.targets
            if extras:
                print('\nextraneous files in %s:' % directory)
                if one_line:
                    print('  ' + ' '.join(sorted(extras)))
                else:
                    print('\n'.join(sorted(extras)))
                print()


def rename(fname, ext=None, pth=None):
    """
    Replace the directory or file extension in ``fname`` with ``pth``
    and ``ext``, respectively. ``fname`` may be a string, an object
    coercible to a string using str(), or a single-element list of
    either.

    Example::

      from bioscons import rename
      stofile = 'align.sto'
      fastafile = env.Command(
          target = rename(stofile, ext='.fasta'),
          source = stofile,
          action = 'seqmagick convert $SOURCE $TARGET'
          )

    """

    dirname, base, suffix = split_path(fname, split_ext = True)
    pth = pth or dirname
    ext = ext or suffix

    newname = path.join(pth, base) + ext
    return newname


def split_path(fname, split_ext=False):
    """
    Returns file name elements given an absolute or relative path
    ``fname``, which may be a string, an object coercible to a string
    using str(), or a single-element list of either. If ``split_ext`` is
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


def write_digest(fname, dirname=None):
    """Save the md5 checksum of fname as fname.md5 in either the same
    directory as fname or in dirname if provided.

    """

    bn, fn = path.split(fname)
    hashfile = path.join(dirname or bn, fn + '.md5')

    with open(fname, 'rb') as f, open(hashfile, 'wb') as h:
        m = hashlib.md5()
        m.update(f.read())
        digest = m.hexdigest()
        h.write(digest)

    return digest


def check_digest(fname, dirname=None):
    """Return True if the stored hash exists and is identical to the
    signature of the file ``fname``. Hash is saved to a file named
    fname.md5 in either the same directory or in dirname if provided.

    """

    bn, fn = path.split(fname)
    hashfile = path.join(dirname or bn, fn + '.md5')

    with open(fname, 'rb') as f:
        m = hashlib.md5()
        m.update(f.read())
        digest = m.hexdigest()

    if path.exists(hashfile):
        with open(hashfile, 'rb') as h:
            same = h.read() == digest
    else:
        same = False

    return same
