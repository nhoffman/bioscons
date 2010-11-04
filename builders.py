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

import Seq

# copyfile
def copyfile_emitter(target, source, env):
    """
    target - name of file or directory
    source - filename
    """

    sname = str(source[0])
    tname = str(target[0])
    if os.path.isdir(tname):
        target = join(tname, split(sname)[1])

    return target, source

copyfile = Builder(
    emitter=copyfile_emitter,
    action='cp $SOURCE $TARGET'
    )

# sweave
def sweave_generator(source, target, env, for_signature):
    dirname, fname = split(str(source[0]))

    action = ''
    if dirname:
        action += 'cd "%s" && ' % dirname

    action += r'echo Sweave\(\"%s\"\) | R --slave' % fname

    # action += 'R CMD Sweave "%s"' % fname

    if len(source) > 1:
        action += ' --args ${SOURCES[1:]}'

    return action

sweave = Builder(
    generator=sweave_generator,
    emitter=lambda target, source, env: (splitext(str(source[0]))[0]+'.tex', source)
)


# stangle
def stangle_generator(source, target, env, for_signature):
    dirname, fname = split(str(source[0]))

    action = ''
    if dirname:
        action += 'cd "%s" && ' % dirname

    action += 'R CMD Stangle "%s"' % fname

    return action

stangle = Builder(
    generator=stangle_generator,
    emitter=lambda target, source, env: (splitext(str(source[0]))[0]+'.R', source)
)

# cmalign
def cmalign_action(target, source, env):
    """
    target - [file in stockholm format, file containing align scores]
    source - [alignment profile, fasta file]
    """

    cmfile, fasta = map(str, source)
    sto, scores = map(str, target)

    cmd = ['cmalign','--hbanded','--sub','--dna',
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
           '--mpi','--hbanded','--sub','--dna',
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

    cmd = ['cmalign','--hbanded','--sub','--merge','--dna','-o',
           sto_out, cmfile, sto1, sto2]

    print ' '.join(cmd)

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    print p.communicate()[0]

cmmerge = Builder(action=cmmerge_action)

def sample_wr(population, k):
    "Chooses k random elements (with replacement) from a population"
    n = len(population)
    _random, _int = random.random, int  # speed hack
    #return [_int(_random() * n) for i in itertools.repeat(None, k)]
    return [population[_int(_random() * n)] for i in itertools.repeat(None, k)]

def cmmerge_all_action(target, source, env):
    """
    Successively merges a list of Stockholm-format aligments

    target - file in stockholm format
    source - two or more files in stockholm format to be merged successively
    """

    tempdir = tempfile.mkdtemp(dir='.')
    mktempname = lambda prefix, fileno: join(tempdir, 'round%i_file%02i.sto' \
                                         % (prefix,fileno))

    merged = map(str, source)
    for i in itertools.count():
        pairs = list(Seq.sequtil.grouper(2, merged))
        print 'round %s, %s pairs' % (i, len(pairs))

        merged = []
        for fileno,pair in enumerate(pairs):
            first, second = pair

            if not second:
                print '%(first)s + None --> %(first)s' % locals()
                merged.insert(0,first)
                continue

            fout = mktempname(i, fileno)
            print '%(first)s + %(second)s --> %(fout)s' % locals()

            merged.append(fout)
            cmd = ['cmalign','--hbanded','--sub','--merge','--dna','-o',
                   fout, env['cmfile'], str(first), str(second)]

            print ' '.join(cmd)
            # p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            # print p.communicate()[0]
            # p = subprocess.Popen(cmd).communicate()

        if len(merged) == 1:
            break

    shutil.copyfile(merged[0], str(target[0]))
    #shutil.rmtree(tempdir)

cmmerge_all = Builder(action=cmmerge_all_action)

# tofasta
def sto2fasta_action(target, source, env):
    """
    target = [aligned seqs in fasta format]
    source = [stockhom format alignment]
    """

    seqs = Seq.io_stockholm.read(open(str(source[0])).read(),
                                 case='upper',
                                 keep_struct=False,
                                 keep_ref=False)

    open(str(target[0]),'w').write(Seq.io_fasta.write(list(seqs)))

sto2fasta = Builder(action=sto2fasta_action)

def mergedToFasta_action(target, source, env):
    """
    Generate separate fasta files from a merged Stockholm alignment

    target = [refalign.fasta, qalign.fasta]
    source = [refalign.sto, merged.sto]
    """

    refalign, merged = source
    refout, qout = target

    # count sequences in refalign.sto
    keep = lambda x: x.strip() and not (x.startswith('#') or x.startswith('/'))

    with open(str(refalign)) as infile:
        refnames = set(line.split()[0] for line in infile if keep(line))
        ref_seq_count = len(refnames)

    # can limit number of sequences from the command line using
    # scons qcount=number
    try:
        qcount = int(env['qcount'])
    except (ValueError, KeyError):
        qcount = None
        qstop = None
    else:
        qstop = ref_seq_count + qcount

    with open(str(merged)) as infile:
        seqs = Seq.io_stockholm.read(infile.read(),
                                     case='upper',
                                     keep_struct=False,
                                     keep_ref=False)

    refseqs = itertools.islice(seqs, ref_seq_count)
    with open(str(refout),'w') as outfile:
        outfile.write(Seq.io_fasta.write(list(refseqs)))

    qseqs = itertools.islice(seqs, ref_seq_count, qstop)
    with open(str(qout),'w') as outfile:
        outfile.write(Seq.io_fasta.write(list(qseqs)))

mergedToFasta = Builder(action=mergedToFasta_action)


def fa_to_seqmat_action(target, source, env):
    """
    Read a fasta format alignment and save a binary sequence matrix (package ape)
    """

    infile, outfile = source[0],target[0]

    rcmd = """library(ape)
    seqmat <- read.dna("%(infile)s", format="fasta", as.matrix=TRUE)
    save(seqmat, file="%(outfile)s")
    stopifnot(file.exists("%(outfile)s"))
    q()""" % locals()

    p = subprocess.Popen(["R", "--vanilla"], stdin=subprocess.PIPE, stdout=sys.stdout)
    p.communicate(rcmd)

fa_to_seqmat = Builder(action=fa_to_seqmat_action)

def fa_to_seqlist_action(target, source, env):
    """
    Read a fasta format alignment and save a binary sequence list (package ape)
    """

    infile, outfile = source[0],target[0]

    rcmd = """library(ape)
    seqlist <- read.dna("%(infile)s", format="fasta", as.matrix=FALSE)
    save(seqlist, file="%(outfile)s")
    stopifnot(file.exists("%(outfile)s"))
    q()""" % locals()

    p = subprocess.Popen(["R", "--vanilla"], stdin=subprocess.PIPE, stdout=sys.stdout)
    p.communicate(rcmd)


def sto_to_dnamultalign_action(target, source, env):

    """
    Read a stockholm format alignment and save a DNAMultipleAlignment
    object (package Biostrings).
    """

    rcmd = """
    library(Biostrings);
    msa <- read.DNAMultipleAlignment(filepath="%s", format="stockholm");
    save(msa, file="%s")""" % (source[0], target[0])

    p1 = subprocess.Popen(['echo',rcmd], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["R", "--vanilla"], stdin=p1.stdout, stdout=sys.stdout)

sto_to_dnamultalign = Builder(action=sto_to_dnamultalign_action)

fa_to_seqlist = Builder(action=fa_to_seqlist_action)

# builder for R scripts
# the first source is the name of the script
def rscript_emitter(target, source, env):
    """
    Add $output/name_of_script.rda as first
    element of $TARGETS
    """

    _, scriptname = split(str(source[0]))
    datafile = join(env.subst('$outdir'), splitext(scriptname)[0] + '.rda')

    return [datafile]+target, source

RScript = Builder(
    action='R -q --slave -f ${SOURCES[0]} --args ${SOURCES[1:]} $TARGETS',
    emitter=rscript_emitter)


# simpler builder for R scripts
# the first source is the name of the script
RScript2 = Builder(
    action='R -q --slave -f ${SOURCES[0]} --args $TARGETS ${SOURCES[1:]}')

# an even simpler builder for an R script
runR = Builder(action='R -q --slave -f ${SOURCES[0]} --args ${SOURCES[1:]}')

# stockholm format to phylip (replace names in phylip file to make
# raxml happy)
def sto2phy_emitter(target, source, env):
    # emits target = phylip alignment, namesfile
    sourcename = str(source[0]).replace('.sto','')
    target = [sourcename+'.phy', sourcename+'_names.txt']
    return target, source

sto2phy = Builder(
    action='sto2other.py -f $SOURCE -F phylip --numbers=${TARGETS[1]} > ${TARGETS[0]}',
    emitter=sto2phy_emitter)

# raxml
def raxml_emitter(target, source, env):
    """
    source - infile.phy
    targets - RAxML_info.infile, RAxML_result.infile

    Note that RAxML produces other files not emitted as targets.
    """

    outdir, fname = split(str(source[0]))
    label = splitext(fname)[0]

    target = [join(outdir,'RAxML_%s.%s'%(x,label)) for x in ('info','result')]

    return target, source

def raxml_generator(source, target, env, for_signature):
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

    try:
        nthreads = int(env['raxml_threads'])
    except (KeyError, ValueError):
        nthreads = 1
       
    # here we pull from the environment variables to figure out which RAxML to run
    # TODO: decide if we want to provide default values

    if nthreads < 2:
        raxml_key = 'RAxML'
        threadflag = '-T %s' % nthreads        
    else:
        raxml_key = 'RAxML_threaded'
        threadflag = ''

    try:
        raxml = env[raxml_key]
    except KeyError:
        raise KeyError("KeyError: '%s' must be defined in the current environment." % raxml)
    
    outdir, fname = split(str(source[0]))
    label = splitext(fname)[0]

    removeme = join(outdir, 'RAxML_*.'+label)

    action = (
        'cd %(outdir)s && '
        'rm -f %(removeme)s && '
        '%(raxml)s %(threadflag)s -m GTRGAMMA -n %(label)s -s %(fname)s' % locals()
        )

    return action

raxml = Builder(generator=raxml_generator, emitter=raxml_emitter)

# replace original names
rename = Builder(
    action='namerepl.py -f ${SOURCES[0]} -m ${SOURCES[1]} -o $TARGET')

# pplacer and utilities
def pplacer_emitter(target, source, env):
    tree, info, refalign, qalign = source

    target = os.path.splitext(str(qalign))[0] + '.place'
    return target, source

# def pplacer_generator(source, target, env, for_signature):
#     """
#     target = [.place file (derived from query align)]
#     source = [raxml tree renamed, raxml info, ref align, query align]
#     """

#     tree, info, refalign, qalign = source
#     outdir, _ = split(str(qalign))

#     action='nice pplacer --outDir %s -t ${SOURCES[0]} -s ${SOURCES[1]} -r ${SOURCES[2]} ${SOURCES[3]}' % outdir
#     return action

def pplacer_generator(source, target, env, for_signature):
    """
    target = [.place file (derived from query align)]
    source = [raxml tree renamed, raxml info, ref align, query align]

    See http://matsen.fhcrc.org/pplacer/manual.html
    -p adds posterior probability and Bayes marginal likelihood to output
    --unfriendly reduces memory consumption
    """

    tree, info, refalign, qalign = source
    outdir, _ = split(str(qalign))

    check_count = False

    if check_count:
        with open(str(qalign)) as qfile:
            qcount = qfile.read().count('>')
        unfriendly = '' if qcount < 2600 else '--unfriendly'
    else:
        unfriendly = ''

    action='nice pplacer -p %(unfriendly)s --outDir %(outdir)s -t ${SOURCES[0]} -s ${SOURCES[1]} -r ${SOURCES[2]} ${SOURCES[3]}' % locals()

    return action

pplacer = Builder(generator=pplacer_generator, emitter=pplacer_emitter)

# placeviz
def placeviz_generator(source, target, env, for_signature):
    fname = str(source[0])
    pth, fn = split(fname)
    action='placeviz --outDir "%(pth)s" "%(fname)s"' % locals()
    return action

def placeviz_emitter(target, source, env):
    fname = str(source[0])
    target = fname.replace('.place','.ML.num.tre')
    return target, source

placeviz = Builder(
    generator=placeviz_generator,
    emitter=placeviz_emitter
    )

# placeutil --distmat
def distmat_generator(source, target, env, for_signature):
    src = str(source[0])
    spath, sfile = split(src)

    distfile = sfile.replace('.place','.distmat')

    targ = str(target[0])
    tpath, tfile = split(targ)

    action = 'cp "%(src)s" "%(tpath)s"'
    action += ' && cd %(tpath)s'
    action += ' && placeutil --distmat "%(sfile)s"'
    action += ' && mv "%(distfile)s" "%(tfile)s"'
    action += ' && rm "%(tpath)s/%(sfile)s"'

    return action % locals()

distmat = Builder(
    generator = distmat_generator
    )

# filenames.R from setup.ini

def filenames_action(target, source, env):

    """
    Writes an R list defining variables and corresponding paths
    specified in setup.ini to TARGET.

    SOURCE is an .ini file (see ConfigParser)

    A subset of sections are scanned for files and directories,
    including [DEFAULT] and any section ending with 'files'. Files
    and directories represented as absolute paths.
    """

    config = ConfigParser.SafeConfigParser()
    config.optionxform = str # preserve case of options
    config.read(str(source[0]))

    lstr = """
files <- list(
    %s
)"""

    basedir = env['basedir']
    defaultvars = set([x[0] for x in config.items('DEFAULT')])

    sections = ['DEFAULT'] + [s for s in config.sections() if s.endswith('files')]
    files = {}
    for var,pth in itertools.chain(*[config.items(s) for s in sections]):
        if var in files and var in defaultvars:
            continue
        elif var in files and not files[var].endswith(pth):
            raise ValueError('"%s" is defined differently in multipe sections' % var)

        files[var] = pth if pth.startswith(basedir) else join(basedir,pth)

    # sys.stdout.write(lstr % ',\n    '.join(
    #         '%s = "%s"' % tup for tup in sorted(files.items())
    #         ) + '\n')


    with open(str(target[0]),'w+') as fout:
        fout.write(lstr % ',\n    '.join(
                '`%s` = "%s"' % tup for tup in sorted(files.items())
                ) + '\n')


filenames = Builder(action=filenames_action)
