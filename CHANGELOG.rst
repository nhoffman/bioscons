======================
 Changes for bioscons
======================

0.8-dev
=======
 * updated README.rst about PyPi submissions

0.7
=======

 * added option to identify targets as Precious in SlurmEnvironment
 * added a SlurmEnvironment time option to output linux system time stats per Command
 * added option to output linux system time information per Command with .time appended to the Target name
 * moved to setuptools and added a distribute_setup.py bootstrap script

0.6
===

 * added fileutils.write_digest and fileutils.check_digest
 * avoid ImportError when importing fileutils outside of an SConstruct

0.5
===

 * commands submitted to SLURM are wrapped in sh -c "..."
 * be more careful about running Commands locally unless use_culster is True

0.4
===

 * added ``bioscons.slurm``

0.3
===

 * added ``infernal.align_and_merge``

0.2
===

 * added ``pplacer.pplacer`` and ``pplacer.align_and_place``
 * added ``infernal.cmalign_method`` and ``infernal.cmmerge_method`` (these will replace other builders in this module)
 * renamed ``refpkg.get_vars`` to ``refpkg.get_varlist``
 * environment variables defined by ``refpkg.get_varlist`` are prepended by 'refpkg_'
