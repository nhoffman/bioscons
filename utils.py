import itertools
import subprocess
import ConfigParser
import tempfile
import shutil
import random
from os.path import join,split,splitext
import os.path

try:
    from SCons.Script import *
except ImportError:
    # we expect this to fail unless imported from within SConstruct
    pass

class verbose(object):
    """
    Decorator class to provide more verbose progress messages.
    """
    def __init__(self, f):
        self.f = f

    def __call__(self, *args, **kwargs):
        print "entering", self.f.__name__, 'called with arguments', args, kwargs
        self.f(*args, **kwargs)
        print "exiting", self.f.__name__


def getvars(config, secnames, indir=None, outdir=None,
            fmt_in='%(sec)s-infiles', fmt_out='%(sec)s-outfiles',
            fmt_params='%(sec)s-params'):
    """
    Return a tuple of configuration variables that may be passed to
    vars.AddVariables().

    * config - an instance of ConfigParser.SafeConfigParser()
    * secnames - a list of section names from which to import variables
    * indir - path to a directory to prepend to filenames if not found in cwd
    * outdir - path to a directory to prepend to output files.
    * fmt_* - formatting string defining sections corresponding to infiles,
      outfiles, and params for each section

    Example:
    vars = Variables()
    varlist = utils.getvars(config, ['ncbi','placefiles'], indir=output, outdir=output)
    vars.AddVariables(*varlist)
    """

    vars = []

    # values from defaults section
    defaults = [k for k,v in config.items('DEFAULT')]
    for varname, val in config.items('DEFAULT'):
        if os.path.isdir(val):
            vars.append(PathVariable(varname, '%s (DEFAULT)'%varname, val, PathVariable.PathIsDir))
        if os.path.isfile(val):
            vars.append(PathVariable(varname, '%s (DEFAULT)'%varname, val, PathVariable.PathIsFile))
        else:
            vars.append((varname, val, val))

    for sec in secnames:
    # input files and directories
        for varname,pth in config.items(fmt_in % locals()):
            if varname in defaults:
                continue
            elif indir and not os.access(pth, os.F_OK):
                pth = join(indir, pth)
            vars.append(PathVariable(varname, '', pth))

        # output files and directories
        for varname,pth in config.items(fmt_out % locals()):
            if varname in defaults:
                continue
            elif outdir and not pth.startswith(outdir):
                pth = join(outdir, pth)
            vars.append(PathVariable(varname, '', pth, PathVariable.PathAccept))

        # ordinary variables; no path checking or directory creation
        params = fmt_params % locals()
        for varname, val in config.items(params):
            if varname in defaults:
                continue
            vars.append(
                (varname, '%(varname)s: defined in [%(params)s]' % locals(), val))

    return tuple(vars)

