======================
 Changes for bioscons
======================

1.1.0
=====

* Slurm binaries are ignored as part of the Scons pipeline decision tree database

1.0.0
=========

* Binaries and scripts that come first in the command are explicitly
  added as an SCons dependency before anything else is prepended to command string
* Multi-step Commands are now handled properly [GH: 25]
* Migrated setup.py to pyproject.toml with dynamic Git versioning
* Python 3.10+ only support (scons 3+ only)
* Time and slurm functions ignored in Command state
* /usr/bin/time and slurm prepending is not shown be defualt in decision
  tree but can be shown with env.SlurmCommand(verbose=True)

0.9.0
=====

* Python 3.5+ compatibility (scons 3+ only)
* version numbers are set using git tag (#2)
* Top-level SConstruct can run tests, perform other development tasks (#19)
* Set up automated tests using Travis-CI (#20)
* min scons version is 2.4.0

0.8.1
=====

* fix a bug when specifying a shell in the Environment

0.8
===

* removed deprecated modules providing builders for various programs
* remove fileutils.list_targets
* updated Sphinx docs
* setting the env shell var works for running commands locally
* enforcing boolean types for use_cluster, all_precious, and time vars

0.7.1
=====

* can define slurm_queue locally
* updated README.rst about PyPi submissions

0.7
===

* added option to identify targets as Precious in SlurmEnvironment
* added a SlurmEnvironment time option to output linux system time stats per Command
* added option to output linux system time information per Command with .time appended to the Target name
* moved to setuptools and added a distribute_setup.py bootstrap script
* can override default slurm_queue in each Command

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
