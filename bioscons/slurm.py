"""
Functions for dispatching to SLURM (https://computing.llnl.gov/linux/slurm/)
from scons.
"""
import re
import shlex

from SCons.Script.SConscript import SConsEnvironment

# From py3.3 argparse
_find_unsafe = re.compile(r'[^\w@%+=:,./-]').search

def _quote(s):
    """Return a shell-escaped version of the string *s*."""
    if not s:
        return "''"
    if _find_unsafe(s) is None:
        return s

    # use single quotes, and put single quotes into double quotes
    # the string $'b is then quoted as '$'"'"'b'
    return "'" + s.replace("'", "'\"'\"'") + "'"

def _action_name(action):
    return shlex.split(action)[0]

class SlurmEnvironment(SConsEnvironment):
    """
    Mostly drop-in replacement for an SCons Environment, where all calls to
    Command are by executed via srun using a single core.

    The SRun and SAlloc methods can be used to use multiple cores for
    multithreaded and MPI jobs, respectively.
    """
    def __init__(self, use_cluster=True, slurm_queue=None, shell='sh', **kwargs):
        super(SlurmEnvironment, self).__init__(**kwargs)
        self.use_cluster = use_cluster
        if slurm_queue:
            self.SetPartition(slurm_queue)
        self.shell = shell

    def _quote_action(self, action):
        return '{shell} -c {action}'.format(shell=self.shell,
                action=_quote(action))

    def _SlurmCommand(self, target, source, action, slurm_command='srun', **kw):
        slurm_args = kw.pop('slurm_args', '')
        if self.use_cluster:
            action = '{cmd} {slurm_args} -J "{name}" {action}'.format(
                    cmd=slurm_command,
                    slurm_args=slurm_args,
                    name=_action_name(action),
                    action=self._quote_action(action))
        return super(SlurmEnvironment, self).Command(target, source, action,
                **kw)

    def SAlloc(self, target, source, action, ncores, timelimit=None, **kw):
        """
        Run ``action`` with salloc.

        This method should be used for MPI jobs only. Combining an salloc call
        with ``mpirun`` (with no arguments) will use all nodes allocated
        automatically.

        Optional arguments:
        ``slurm_args``: Additional arguments to pass to salloc
        ``timelimit``: value to use for environment variable SALLOC_TIMELIMIT
        """
        args = ' '.join(('-n {0}'.format(ncores), kw.pop('slurm_args', '')))
        e = self

        if timelimit is not None:
            clone = self.Clone()
            clone.SetTimeLimit(timelimit)
            e = clone

        return e._SlurmCommand(target, source, action, 'salloc',
                slurm_args=args, **kw)

    def SRun(self, target, source, action, ncores=1, timelimit=None, **kw):
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
        if not isinstance(action, basestring) or not use_cluster or not self.use_cluster:
            return super(SlurmEnvironment, self).Command(target, source, action, **kw)
        return self.SRun(target, source, action, **kw)

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
        self['ENV']['SALLOC_TIMELIMIT'] = timelimit
