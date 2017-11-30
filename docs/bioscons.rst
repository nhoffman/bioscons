``bioscons`` Documentation
==========================

This page contains the ``bioscons`` Package documentation.

Subpackages
-----------

.. toctree::

The :mod:`fast` Module
----------------------

.. automodule:: bioscons.fast
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`fileutils` Module
---------------------------

.. automodule:: bioscons.fileutils
    :members:
    :undoc-members:
    :show-inheritance:

The :mod:`slurm` Module
-----------------------

.. automodule:: bioscons.slurm
    :members:
    :undoc-members:
    :show-inheritance:

Notes on parallelization
~~~~~~~~~~~~~~~~~~~~~~~~

The combination of ``scons`` and ``slurm`` provides a powerful
mechanism for rate-limiting parallel tasks to maximize resource
utilization while preventing oversubscription. Here's an
example. Consider the following ``SConstruct``::

  import os
  from bioscons.slurm import SlurmEnvironment

  vars = Variables()
  vars.Add('ncores', 'number of cores per task', default=1)

  env = SlurmEnvironment(
      ENV=os.environ,
      variables=vars,
      use_cluster=True,
      SHELL='bash',
      out='output'
  )

  print(env.subst('--> ncores=$ncores'))

  for i in range(10):
      AlwaysBuild(env.Command(
	  target='$out/{}.txt'.format(i),
	  source=None,
	  action=('date > $TARGET; sleep 2'),
	  ncores=env['ncores'],
      ))

Running this as 10 jobs in parallel with a single core allocated to
each task results in the following::

  % scons -j10
  scons: Reading SConscript files ...
  --> ncores=1
  scons: done reading SConscript files.
  scons: Building targets ...
  srun -J "date" bash -c 'date > output/0.txt; sleep 2'
  srun -J "date" bash -c 'date > output/1.txt; sleep 2'
  srun -J "date" bash -c 'date > output/2.txt; sleep 2'
  srun -J "date" bash -c 'date > output/3.txt; sleep 2'
  srun -J "date" bash -c 'date > output/4.txt; sleep 2'
  srun -J "date" bash -c 'date > output/5.txt; sleep 2'
  srun -J "date" bash -c 'date > output/6.txt; sleep 2'
  srun -J "date" bash -c 'date > output/7.txt; sleep 2'
  srun -J "date" bash -c 'date > output/8.txt; sleep 2'
  srun -J "date" bash -c 'date > output/9.txt; sleep 2'
  scons: done building targets.
  % cat output/*.txt | sort | uniq -c
  10 Wed Nov 29 22:13:50 PST 2017

The final line demonstrates that all tasks are dispatched
simultaneously. Now let's imagine that the action is actually a
multi-threaded process requiring 20 cores, and dispatching 10
simultaneous jobs would exceed the number of cpus or amount of memory
per cpu available. By increasing the number of cores per task, we can
force slurm to rate-limit the jobs.::

  % scons ncores=20 -j10
  scons: Reading SConscript files ...
  --> ncores=20
  scons: done reading SConscript files.
  scons: Building targets ...
  srun -J "date" bash -c 'date > output/0.txt; sleep 2'
  srun -J "date" bash -c 'date > output/1.txt; sleep 2'
  srun -J "date" bash -c 'date > output/2.txt; sleep 2'
  srun -J "date" bash -c 'date > output/3.txt; sleep 2'
  srun -J "date" bash -c 'date > output/4.txt; sleep 2'
  srun -J "date" bash -c 'date > output/5.txt; sleep 2'
  srun -J "date" bash -c 'date > output/6.txt; sleep 2'
  srun: job 26896 queued and waiting for resources
  srun -J "date" bash -c 'date > output/7.txt; sleep 2'
  srun: job 26897 queued and waiting for resources
  srun: job 26898 queued and waiting for resources
  srun -J "date" bash -c 'date > output/8.txt; sleep 2'
  srun -J "date" bash -c 'date > output/9.txt; sleep 2'
  srun: job 26899 queued and waiting for resources
  srun: job 26900 queued and waiting for resources
  srun: job 26901 queued and waiting for resources
  srun: job 26896 has been allocated resources
  srun: job 26897 has been allocated resources
  srun: job 26898 has been allocated resources
  srun: job 26899 has been allocated resources
  srun: job 26900 has been allocated resources
  srun: job 26901 has been allocated resources
  scons: done building targets.
  % cat output/*.txt | sort | uniq -c
	4 Wed Nov 29 22:24:44 PST 2017
	4 Wed Nov 29 22:24:46 PST 2017
	2 Wed Nov 29 22:24:48 PST 2017

Rate-limiting job dispatch is of course the whole purpose of
``slurm``; ``scons`` brings the additional benefit of
paralellization. This pattern provides a mechanism for specifying an
arbitrarily large value for ``-j`` to maximize the number of tasks run
in parallel without exceeding system resources.

The :mod:`utils` Module
-----------------------

.. automodule:: bioscons.utils
    :members:
    :undoc-members:
    :show-inheritance:





