"""
Builders
--------

raxml
+++++

Calculates a maximum likelihood phylogenetic tree using RAxML. Will
attempt to execute a multithreaded version if RAXML_PTHREADS > 1. The
output will be written to the same directory as the input file, with
filenames matching the pattern [RAxML_info.foo, RAxML_result.foo]
given an alignment named `foo.phy`. Other files not returned as
targets may also be generated.

:source: [input alignment (relaxed phylip format)]

:target: [info_file, result_file]

:environment variables (module globals define defaults):
 * env['RAXML']
 * env['RAXML_FLAGS']
 * env['RAXML_NTHREADS']
 * env['RAXML_PTHREADS']

example
-------

.. code-block:: python

 from bioscons.raxml import raxml
 env['BUILDERS']['raxml'] = raxml

 info_file, result_file = env.raxml('alignment.phy')
 
 
Public functions and variables
------------------------------
"""

import os
from os import path
import subprocess
import logging

log = logging

# we expect this to fail unless imported from within SConstruct
try:
    from SCons.Script import *
except ImportError:
    pass

from fileutils import split_path

#: Name of the RAxML executable if
#: RAXML_NTHREADS == 1. ['raxmlHPC-SSE3']
RAXML = 'raxmlHPC-SSE3'

#: Name of the RAxML executable if
#: RAXML_NTHREADS > 1. ['raxmlHPC-PTHREADS-SSE3']
RAXML_PTHREADS = 'raxmlHPC-PTHREADS-SSE3'

#: String containing optional command line parameters. []
RAXML_FLAGS = '-m GTRGAMMA'

#: Number of threads used by RAxML. [1]
RAXML_NTHREADS = 1

def check_raxml(env):
    """
    Determines whether the raxml executable can be executed, and if
    so, generates a version string. Returns environment-defined or
    default values of either RAXML or RAXML_PTHREADS as
    appropriate. If successful, returns (path-to-executable,
    version-string). Raises SystemError on failure.
    """


    nthreads = int(env.get('RAXML_NTHREADS', RAXML_NTHREADS))

    # determine which RAxML to run based on number of threads
    if nthreads < 2:
        threadflag = ''
        raxml = env.get('RAXML', RAXML)
    else:
        threadflag = '-T %s' % nthreads
        raxml = env.get('RAXML_PTHREADS', RAXML_PTHREADS)
        
    p = subprocess.Popen('%s -h' % raxml,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    
    if err:
        raise SystemError('"%s" could not be executed. Is it installed?' % raxml)

    version = out.strip().splitlines()[0]

    log.info('using %s, %s' % (raxml, version))

    return raxml, version



def _raxml_emitter(target, source, env):
    """
    source - infile.phy
    targets - RAxML_info.infile, RAxML_result.infile

    Note that RAxML produces other files not emitted as targets.
    """

    outdir, label, suffix = split_path(source[0], split_ext=True)
    target = [path.join(outdir,'RAxML_%s.%s'%(x,label)) for x in ('info','result')]

    return target, source

def _raxml_generator(source, target, env, for_signature):
    """
    Implements env.raxml
    Depends on env['RAxML'] or env['RAxML_threaded']
    Number of threads (-T) may be set using env['raxml_threads'], default is 1

    raxmlHPC -m GTRGAMMA -n label -s align.phy

    -m is the model
    -n is the name of the run (will become output filenames)
    -s is the alignment in phylip format

    TODO: will want to have an additional environment variable for
    arbitrary command line flags for raxml.
    """

    raxml, version = check_raxml(env)
    log.info(version)
    
    nthreads = int(env.get('RAXML_NTHREADS', RAXML_NTHREADS))
    threadflag = '-T %s' % nthreads if nthreads > 1 else ''

    flags = env.get('RAXML_FLAGS', RAXML_FLAGS)
    
    outdir, fname = split_path(source[0], split_ext=False)
    label, _ = path.splitext(fname)

    removeme = path.join(outdir, 'RAxML_*.'+label)

    action = (
        'cd %(outdir)s && '
        'rm -f %(removeme)s && '
        '%(raxml)s %(threadflag)s %(flags)s -n %(label)s -s %(fname)s' % \
            locals()
        )

    return action

raxml = Builder(generator=_raxml_generator, emitter=_raxml_emitter)

