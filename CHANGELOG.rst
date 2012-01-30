======================
 Changes for bioscons
======================

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
