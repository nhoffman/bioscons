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

    def SRun(self, target, source, action, ncores, **kw):
        """
        Run ``action`` with srun.

        This method should be used for multithreaded jobs only. By default,
        calls to SlurmEnvironment.Command use srun.  If multiple cores
        are required, supply an ncores argument.

        This method should be used for MPI jobs only. Combining an salloc call
        with ``mpirun`` (with no arguments) will use all nodes allocated
        automatically.

        Optional arguments:
        ``slurm_args``: Additional arguments to pass to salloc
        """
        if ncores > 1:
            clone = self.Clone()
            clone['ENV']['SLURM_CPUS_PER_TASK'] = str(ncores)
            return clone._SlurmCommand(target, source, action, **kw)
        else:
            return self._SlurmCommand(target, source, action, **kw)

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
