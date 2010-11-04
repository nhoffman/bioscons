#!/usr/bin/env python

import sys
import os
import itertools
import re

import Seq

def write_interleaved(fout, seqs):

    fout.write('%s %s\n' % (len(seqs), len(seqs[0])))

    for seq in seqs:
        fout.write('%s %s\n' % (seq.name, seq.seq.upper()))

def main():
    i = int(sys.argv[1])
    infile = sys.argv[2]
    fasta = sys.argv[3]
    phylip = sys.argv[4]

    seqs = Seq.io_fasta.read(open(infile).read())
    thisone = seqs.pop(i)

    with open(fasta,'w') as fout:
        fout.write(Seq.io_fasta.write(thisone))

    with open(phylip,'w') as fout:
        write_interleaved(fout, seqs)

if __name__ == '__main__':
    main()
