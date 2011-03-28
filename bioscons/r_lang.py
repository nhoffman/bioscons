import os
import sys
from os.path import join,split,splitext
import re
import pprint
import glob

try:
    from SCons.Script import *
except ImportError:
    # we expect this to fail unless imported from within SConstruct
    pass

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
RScript = Builder(
    action='R -q --slave -f ${SOURCES[0]} --args $TARGETS ${SOURCES[1:]}')

# an even simpler builder for an R script
runR = Builder(action='R -q --slave -f ${SOURCES[0]} --args ${SOURCES[1:]}')
