from os.path import join,split,splitext
import os
import subprocess

try:
    from SCons.Script import *
except ImportError:
    # we expect this to fail unless imported from within SConstruct
    pass


# cmalign
def cmalign_action(target, source, env):
    """
    target - [file in stockholm format, file containing align scores]
    source - [alignment profile, fasta file]
    """

    cmfile, fasta = map(str, source)
    sto, scores = map(str, target)

    cmd = ['cmalign','--hbanded','--sub','--dna','-1',
           '-o', sto, cmfile, fasta]

    print ' '.join(cmd)

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    scorestr = p.communicate()[0]

    with open(scores, 'w') as scorefile:
        scorefile.write(scorestr)

cmalign = Builder(
    action=cmalign_action)

def cmalign_mpi_action(target, source, env):
    """
    Run cmalign using mpi (mpirun)

    Number of processors (default 1) is set using 'cmalign_nproc'.

    target - [file in stockholm format, file containing align scores]
    source - [alignment profile, fasta file]
    """

    cmfile, fasta = map(str, source)
    sto, scores = map(str, target)

    try:
        nproc = int(env['cmalign_nproc'])
    except (KeyError, ValueError):
        nproc = 1

    try:
        cmalign = env['cmalign']
    except KeyError:
        cmalign = 'cmalign'

    cmd = ['mpirun',
           '-np %s' % nproc,
           cmalign,
           '--mpi','--hbanded','--sub','--dna','-1',
           '-o', sto, cmfile, fasta,
           '|', 'tee', scores]

    cmd = ' '.join(cmd)
    os.system(cmd)

    # TODO: there is some problem with the executaion environment that
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
    action=cmalign_mpi_action)

# cmalign = Builder(
#     action='cmalign --hbanded --sub --dna -o ${TARGETS[0]} $cmfile $SOURCES | tee ${TARGETS[1]}'
#     )

def cmmerge_action(target, source, env):
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
    print p.communicate()[0]

cmmerge = Builder(action=cmmerge_action)

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
