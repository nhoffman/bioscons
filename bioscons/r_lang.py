"""
Builders
--------

fa_to_seqlist
+++++++++++++

Save the sequence alignment as a list-like object of class DNAbin, for example::

  > library(ape)
  > seqlist <- read.dna(source, format="fasta", as.matrix=FALSE)
  > save(seqlist, file=target)

:source: [fasta-file]

:target: [R data file]

:environment variables (module globals define defaults):

fa_to_seqmat
++++++++++++

Save the sequence alignment as a matrix-like object of class DNAbin, for example::

  > library(ape)
  > seqlist <- read.dna(source, format="fasta", as.matrix=TRUE)
  > save(seqlist, file=target)

:source: [fasta-file]

:target: [R data file]

:environment variables (module globals define defaults):

RScript
+++++++

runR
++++

sweave
++++++

stangle
+++++++

Public functions and variables
------------------------------
"""


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

def _sweave_generator(source, target, env, for_signature):
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
    generator=_sweave_generator,
    emitter=lambda target, source, env: (splitext(str(source[0]))[0]+'.tex', source)
)

# stangle
def _stangle_generator(source, target, env, for_signature):
    dirname, fname = split(str(source[0]))

    action = ''
    if dirname:
        action += 'cd "%s" && ' % dirname

    action += 'R CMD Stangle "%s"' % fname

    return action

stangle = Builder(
    generator=_stangle_generator,
    emitter=lambda target, source, env: (splitext(str(source[0]))[0]+'.R', source)
)

def _fa_to_seqlist_action(target, source, env):
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

fa_to_seqlist = Builder(action=_fa_to_seqlist_action)    

def _fa_to_seqmat_action(target, source, env):
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

fa_to_seqmat = Builder(action=_fa_to_seqmat_action)

# def _sto_to_dnamultalign_action(target, source, env):

#     """
#     Read a stockholm format alignment and save a DNAMultipleAlignment
#     object (package Biostrings).
#     """

#     rcmd = """
#     library(Biostrings);
#     msa <- read.DNAMultipleAlignment(filepath="%s", format="stockholm");
#     save(msa, file="%s")""" % (source[0], target[0])

#     p1 = subprocess.Popen(['echo',rcmd], stdout=subprocess.PIPE)
#     p2 = subprocess.Popen(["R", "--vanilla"], stdin=p1.stdout, stdout=sys.stdout)

# sto_to_dnamultalign = Builder(action=_sto_to_dnamultalign_action)

# builder for R scripts
# the first source is the name of the script
RScript = Builder(
    action='R -q --slave -f ${SOURCES[0]} --args $TARGETS ${SOURCES[1:]}')

# an even simpler builder for an R script
runR = Builder(action='R -q --slave -f ${SOURCES[0]} --args ${SOURCES[1:]}')
