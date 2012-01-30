"""
Functions for dispatching to SLURM (https://computing.llnl.gov/linux/slurm/)
from scons.
"""

from SCons.Script.SConscript import SConsEnvironment

class SlurmEnvironment(SConsEnvironment):
    """
    Subclass of environment, where all calls to Command are by default run
    using srun on the cluster using a single core.

    The SRun and SAlloc methods can be used to use multiple cores for
    multithreaded and MPI jobs, respectively.
    """
    def __init__(self, use_cluster=True, slurm_queue='pubnorm', **kwargs):
        super(SlurmEnvironment, self).__init__(**kwargs)
        self.use_cluster = use_cluster
        self.slurm_queue = slurm_queue

    def _SlurmCommand(self, target, source, action, slurm_command='srun', core_flag='-c', **kw):
        ncores = kw.pop('ncores', 1)
        queue = kw.pop('slurm_queue', self.slurm_queue)
        slurm_args = kw.pop('slurm_args', '')
        if self.use_cluster:
            action = '{cmd} -p {queue} {flag} {ncores} {slurm_args}'.format(
                    cmd=slurm_command,
                    queue=queue or self.slurm_queue, flag=core_flag,
                    ncores=ncores, slurm_args=slurm_args) + action
        return super(SlurmEnvironment, self).Command(target, source, action,
                **kw)

    def SAlloc(self, target, source, action, ncores, **kw):
        """
        Run ``action`` with salloc.

        This method should be used for MPI jobs only. Combining an salloc call
        with ``mpirun`` (with no arguments) will use all nodes allocated
        automatically.

        Optional arguments:
        ``slurm_queue``: To override the default
        ``slurm_args``: Additional arguments to pass to salloc
        """
        return self._SlurmCommand(target, source, action, 'salloc', '-n',
                ncores=ncores, **kw)

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
        ``slurm_queue``: To override the default
        ``slurm_args``: Additional arguments to pass to salloc
        """
        return self._SlurmCommand(target, source, action, ncores=ncores, **kw)

    def Command(self, target, source, action, use_cluster=True, **kw):
        if not use_cluster:
            return super(SlurmEnvironment, self).Command(target, source, action, **kw)
        assert 'srun' not in action
        assert 'salloc' not in action
        assert 'ncores' not in kw, "The 'ncores' argument has no effect in `SlurmEnvironment.Command()`."
        return self._SlurmCommand(target, source, action)
