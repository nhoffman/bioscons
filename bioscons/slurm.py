"""
Functions for dispatching to SLURM (https://computing.llnl.gov/linux/slurm/)
from scons.

:environment variables
 * SLURM_PARTITION - Slurm queue to use for `srun`
 * SALLOC_PARTITION - Slurm queue to use for `salloc` calls
"""

from SCons.Script.SConscript import SConsEnvironment

class SlurmEnvironment(SConsEnvironment):
    """
    Subclass of environment, where all calls to Command are by default run
    using srun on the cluster using a single core.

    The SRun and SAlloc methods can be used to use multiple cores for
    multithreaded and MPI jobs, respectively.
    """
    def __init__(self, use_cluster=True, **kwargs):
        super(SlurmEnvironment, self).__init__(**kwargs)
        self.use_cluster = use_cluster

    def _SlurmCommand(self, target, source, action, slurm_command='srun', **kw):
        slurm_args = kw.pop('slurm_args', '')
        if self.use_cluster:
            action = '{cmd} {slurm_args} '.format(
                    cmd=slurm_command,
                    slurm_args=slurm_args) + action
        return super(SlurmEnvironment, self).Command(target, source, action,
                **kw)

    def SAlloc(self, target, source, action, ncores, **kw):
        """
        Run ``action`` with salloc.

        This method should be used for MPI jobs only. Combining an salloc call
        with ``mpirun`` (with no arguments) will use all nodes allocated
        automatically.

        Optional arguments:
        ``slurm_args``: Additional arguments to pass to salloc
        """
        args = ' '.join(('-n {0}'.format(ncores), kw.pop('slurm_args', '')))
        return self._SlurmCommand(target, source, action, 'salloc',
                slurm_args=args, **kw)

    def SRun(self, target, source, action, ncores, timelimit=None, **kw):
        """
        Run ``action`` with srun.

        This method should be used for multithreaded jobs on a single machine
        only. By default, calls to SlurmEnvironment.Command use srun. Specify a
        number of processors with ``ncores``.

        Optional arguments:
        ``slurm_args``: Additional arguments to pass to salloc
        ``timelimit``: Value to use for environment variable SLURM_TIMELIMIT
        """
        clone = self.Clone()
        if ncores > 1:
            clone.SetCpusPerTask(ncores)
        if timelimit is not None:
            clone.SetTimeLimit(timelimit)
        return clone._SlurmCommand(target, source, action, **kw)

    def Command(self, target, source, action, use_cluster=True, **kw):
        if not use_cluster or not self.use_cluster:
            return super(SlurmEnvironment, self).Command(target, source, action, **kw)
        assert 'srun' not in action
        assert 'salloc' not in action
        assert 'ncores' not in kw, "The 'ncores' argument has no effect in `SlurmEnvironment.Command()`."
        return self._SlurmCommand(target, source, action, **kw)

    def Local(self, target, source, action, **kw):
        """
        Run a command locally, without SLURM
        """
        return self.Command(target, source, action, use_cluster=False, **kw)

    def SetPartition(self, partition):
        """
        Set the partition to be used. Subsequent calls to SRun and SAlloc will use this partition.
        """
        for var in ('SLURM_PARTITION', 'SALLOC_PARTITION'):
            self['ENV'][var] = partition

    def SetCpusPerTask(self, cpus_per_task):
        """
        Set number of CPUs used by tasks launched from this environment with
        srun. Equivalent to ``srun -c``
        """
        self['ENV']['SLURM_CPUS_PER_TASK'] = str(cpus_per_task)

    def SetTimeLimit(self, timelimit):
        """
        Set a limit on the total run time for jobs launched by this environment.

        Formats:
            minutes
            minutes:seconds
            hours:minutes:seconds
            days-hours
            days-hours:minutes
            days-hours:minutes:seconds
        """
        self['ENV']['SLURM_TIMELIMIT'] = timelimit
