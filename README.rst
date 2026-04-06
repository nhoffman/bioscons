.. image:: logo.svg
   :alt: bioscons
   :width: 400px

``bioscons`` extends `SCons <https://scons.org>`_ for building reproducible bioinformatics pipelines, with built-in support for the Slurm job scheduler.

- Dependency tracking: only re-run steps whose inputs have changed
- Slurm integration: dispatch jobs to a cluster with a single drop-in replacement
- Parallelization: dependency graph enables concurrent execution of independent steps

Why SCons?
==========

`SCons <https://scons.org>`_ is well-suited for bioinformatics pipelines:

* **Incremental builds**: re-running SCons only re-executes steps whose inputs have changed
* **Parallelization**: the dependency graph enables concurrent execution of independent steps
* **Shell-like syntax**: external programs are easy to invoke with variable substitution
* **Python integration**: leverage the standard library, Biopython, NumPy, etc. directly in your build script
* **File objects**: pipeline steps are expressed in terms of file objects rather than filenames, keeping scripts readable
* **Incremental validation**: SCons validates files and can fail gracefully at any step

Requirements
============

* Python 3.10+
* scons 3+

Installation
============

::

  python3 -m pip install bioscons

Usage
=====

Basic SCons pipeline::

  from SCons.Script import Environment

  env = Environment(MP_NUM_THREADS=3)

  alignment = env.Command(
      target='$out/seqs.aln.fasta',
      source='$data/seqs.fasta',
      action='muscle -in $SOURCE -out $TARGET -threads 4'
  )

  tree = env.Command(
      target='$out/seqs.tre',
      source=alignment,
      action='FastTreeMP -nt -gtr $SOURCE > $TARGET'
  )

Basic Bioscons pipeline using Slurm::

  from bioscons.slurm import SlurmEnvironment

  env = SlurmEnvironment(OMP_NUM_THREADS=3, use_cluster=True)

  alignment = env.Command(
      target='$out/seqs.aln.fasta',
      source='$data/seqs.fasta',
      action='muscle -in $SOURCE -out $TARGET -threads 4',
      ncores=4
  )

  tree = env.Command(
      target='$out/seqs.tre',
      source=alignment,
      action='FastTreeMP -nt -gtr $SOURCE > $TARGET',
      ncores=3  # OMP_NUM_THREADS=3
  )

See the `full documentation <http://nhoffman.github.io/bioscons/>`_ for additional utilities.


Contributors
============

* Noah Hoffman
* Erick Matsen
* Chris Rosenthal
* Christopher Small
* Connor McCoy
* Tim Holland
