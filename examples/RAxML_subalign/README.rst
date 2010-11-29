Perform leave-one-out analysis of classification of sequences in a
reference tree.


Dependencies
============

All are installed in /home/bvdiversity/local

 1. python 2.6+
 1. scons 2.0+
 1. sconstools - http://github.com/nhoffman/sconstools
 1. Seq package - will move to github


Input
=====

 1. input/test_aln.fasta (reference alignment in fasta format)

Execution
=========

Do this::
 
 source /home/bvdiversity/local/bin/activate_bv
 scons

Note that parallel jobs can be run natively, eg::

 scons -j 4

Clean up bulid targets::

 scons --clean
