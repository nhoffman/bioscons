"""
Builders
--------

cmalign
+++++++

Aligns sequences in the source fasta-file given
alignment-profile. Returns the Stockholm-format alignment and a file
containing the alignment statistics for each sequence.

:source: [alignment-profile, fasta-file]

:target: [file in stockholm format, file containing align scores]

:environment variables: env['cmalign'] provides an alternative path to the cmalign executable (default 'cmalign').

cmalign_mpi
+++++++++++

Aligns sequences in the source fasta-file given
alignment-profile. Returns the Stockholm-format alignment and a file
containing the alignment statistics for each sequence. cmalign is run
using ``mpirun -np N cmalign --mpi``; note that 'cmalign --mpi' is
only available if cmalign is compiled with the '--enable-mpi' flag.

:source: [alignment-profile, fasta-file]

:target: [file in stockholm format, file containing align scores]

:environment variables:
 * env['cmalign'] provides an alternative path to the cmalign executable (default 'cmalign').
 * env['cmalign_nproc'] defines the number of processors (default 2).

cmmerge
+++++++

Merges two sequence alignments in Stockholm format given
alignment-profile using ``cmalign --merge``. Returns the Stockholm-format alignment.


:source: [alignment-profile, stockholm-file1, stockholm-file2]

:target: [alignment in stockholm format]

:environment variables: env['cmalign'] provides an alternative path to the cmalign executable (default 'cmalign').

Public functions
----------------
"""

from os.path import join,split,splitext
import os
import subprocess
import logging

log = logging

# we expect this to fail unless imported from within SConstruct
try:
    from SCons.Script import *
except ImportError:
    pass

def check_cmalign(env):
    """
    Determines whether the cmalign executable can be used to generate
    a version string. Uses either the path to the cmalign executable
    defined in env['cmalign'] or 'cmalign' by default. If successful,
    returns (path-to-executable, version-string). Raises SystemError
    on failure.
    """
    
    try:
        cmalign = env['cmalign']
    except KeyError:
        cmalign = 'cmalign'
        
    p = subprocess.Popen('%s -h' % cmalign,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    
    if err:
        raise SystemError('"%s" could not be executed. Is it installed?' % cmalign)

    version = out.splitlines()[1].rstrip('# ')

    log.info('using %s, %s' % (cmalign, version))

    return cmalign, version

def check_mpirun(env):
    """
    Determines whether the mpirun executable can be used to generate
    a version string. Uses either the path to the mpirun executable
    defined in env['mpirun'] or 'mpirun' by default. If successful,
    returns (path-to-executable, version-string). Raises SystemError
    on failure.
    """
    
    try:
        mpirun = env['mpirun']
    except KeyError:
        mpirun = 'mpirun'

    # version info is in stderr. Yeah.
    p = subprocess.Popen('%s -V' % mpirun,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    
    if p.returncode > 0:
        raise SystemError('"%s" could not be executed. Is it installed?' % mpirun)

    version = err.splitlines()[0]

    log.info('using %s, %s' % (mpirun, version))

    return mpirun, version


# cmalign
def _cmalign_action(target, source, env):
    """
    target - [file in stockholm format, file containing align scores]
    source - [alignment profile, fasta file]
    """

    cmalign, version = check_cmalign(env)
    
    cmfile, fasta = map(str, source)
    sto, scores = map(str, target)
        
    cmd = [cmalign,'--hbanded','--sub','--dna','-1',
           '-o', sto, cmfile, fasta]

    log.info(' '.join(cmd))
    
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = p.communicate()
        
    with open(scores, 'w') as scorefile:
        scorefile.write(out)

cmalign = Builder(
    action=_cmalign_action)

def _cmalign_mpi_action(target, source, env):
    """
    Run cmalign using mpi (mpirun)

    Number of processors (default 2) is set using
    'cmalign_nproc'. Note that 'cmalign --mpi' is only available if
    cmalign is configured using the '--enable-mpi' on compilation.

    target - [file in stockholm format, file containing align scores]
    source - [alignment profile, fasta file]
    """
    
    mpirun, mpi_version = check_mpirun(env)
    cmalign, cmalign_version = check_cmalign(env)
    
    cmfile, fasta = map(str, source)
    sto, scores = map(str, target)

    try:
        nproc = int(env['cmalign_nproc'])
    except (KeyError, ValueError):
        nproc = 2

    cmd = [mpirun,
           '-np %s' % nproc,
           cmalign,
           '--mpi','--hbanded','--sub','--dna','-1',
           '-o', sto, cmfile, fasta,
           '|', 'tee', scores]

    cmd = ' '.join(cmd)
    log.info(cmd)
    os.system(cmd)

    # TODO: there is some problem with the execution environment that
    # results in an error in mpirun when executed usimg subprocess

    # cmd = ['mpirun',
    #        '-np %s' % nproc,
    #        '/home/bvdiversity/local/bin/cmalign',
    #        '--mpi','--hbanded','--sub','--dna',
    #        '-o', sto, cmfile, fasta]


    # p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    # scorestr = p.communicate()[0]

    # with open(scores, 'w') as scorefile:
    #     scorefile.write(scorestr)

cmalign_mpi = Builder(
    action=_cmalign_mpi_action)

# cmalign = Builder(
#     action='cmalign --hbanded --sub --dna -o ${TARGETS[0]} $cmfile $SOURCES | tee ${TARGETS[1]}'
#     )

def _cmmerge_action(target, source, env):
    """
    target - file in stockholm format
    source - [cmfile, cmalign1.sto, cmalign2.sto]
    """

    cmfile, sto1, sto2 = map(str, source)
    sto_out = str(target[0])

    cmd = ['cmalign','--hbanded','--sub','--merge','--dna','-1','-o',
           sto_out, cmfile, sto1, sto2]

    print ' '.join(cmd)

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    # print p.communicate()[0]

cmmerge = Builder(action=_cmmerge_action)

# def cmmerge_all_action(target, source, env):
#     """
#     Successively merges a list of Stockholm-format aligments

#     target - file in stockholm format
#     source - two or more files in stockholm format to be merged successively
#     """

#     tempdir = tempfile.mkdtemp(dir='.')
#     mktempname = lambda prefix, fileno: join(tempdir, 'round%i_file%02i.sto' \
#                                          % (prefix,fileno))

#     merged = map(str, source)
#     for i in itertools.count():
#         pairs = list(Seq.sequtil.grouper(2, merged))
#         print 'round %s, %s pairs' % (i, len(pairs))

#         merged = []
#         for fileno,pair in enumerate(pairs):
#             first, second = pair

#             if not second:
#                 print '%(first)s + None --> %(first)s' % locals()
#                 merged.insert(0,first)
#                 continue

#             fout = mktempname(i, fileno)
#             print '%(first)s + %(second)s --> %(fout)s' % locals()

#             merged.append(fout)
#             cmd = ['cmalign','--hbanded','--sub','--merge','--dna','-o',
#                    fout, env['cmfile'], str(first), str(second)]

#             print ' '.join(cmd)
#             # p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
#             # print p.communicate()[0]
#             # p = subprocess.Popen(cmd).communicate()

#         if len(merged) == 1:
#             break

#     shutil.copyfile(merged[0], str(target[0]))
#     #shutil.rmtree(tempdir)

# cmmerge_all = Builder(action=cmmerge_all_action)
