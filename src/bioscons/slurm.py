"""
Functions for dispatching to SLURM (https://computing.llnl.gov/linux/slurm/)
from scons.
"""

import re
import SCons
import subprocess

from SCons.Script.SConscript import SConsEnvironment

# From py3.3 argparse
_find_unsafe = re.compile(r'[^\w@%+=:,./-]').search

# system path to the time function
_time = '/usr/bin/time --verbose --output ${TARGETS[0]}.time '


def check_srun():
    """
    Return the absolute path to the `srun` executable.
    """

    try:
        srun = subprocess.check_output(['which', 'srun'])
        srun = srun.strip().decode("utf-8")
    except subprocess.CalledProcessError:
        srun = None

    return srun


def _check_type(bool_vars):
    """list((var, varname, type)) checking variable types
    """

    for var, name, tp in bool_vars:
        if not isinstance(var, tp):
            raise TypeError('{} {} argument expected, got {}'.format(
                name, tp, type(var)))


class SlurmEnvironment(SConsEnvironment):

    """
    Mostly drop-in replacement for an SCons Environment, where all calls to
    Command are by executed via srun using a single core.

    The SRun and SAlloc methods can be used to use multiple cores for
    multithreaded and MPI jobs, respectively.
    """

    def __init__(self, use_cluster=True, slurm_queue=None,
                 all_precious=False, time=False, verbose=False, **kwargs):
        super(SlurmEnvironment, self).__init__(**kwargs)

        # check boolean types because so often these are accidentally strings
        _check_type([(use_cluster, 'use_cluster', bool),
                     (all_precious, 'all_precious', bool),
                     (time, 'time', bool)])

        self.use_cluster = use_cluster
        self.all_precious = all_precious
        self.time = time
        self.verbose = verbose
        if slurm_queue:
            self.SetPartition(slurm_queue)
        self.shell = kwargs.get('SHELL', 'sh')

    def _SlurmCommand(self, target, source, action, slurm_cmd, time, **kw):
        if not isinstance(action, list):
            action = [action]
        if time or slurm_cmd:
            kw['IMPLICIT_COMMAND_DEPENDENCIES'] = False
            for a in action:
                cmd = self.subst(a, SCons.Subst.SUBST_RAW, target, source)
                cmd = cmd.split(maxsplit=1)[0]
                self.Depends(target, self.WhereIs(cmd))

        actions = []
        for a in action:
            if isinstance(a, str):
                actions.append(
                    _SlurmAction(a, self.shell, slurm_cmd, time,
                                 kw.pop('slurm_args', ''), self.verbose)
                    )
            else:
                actions.append(a)

        env = super(SlurmEnvironment, self)
        result = env.Command(target, source, actions, **kw)

        if kw.pop('precious', self.all_precious):
            self.Precious(result)

        return result

    def Command(
            self, target, source, action, use_cluster=True, time=True, **kw):
        """Dispatches ``action`` (and extra arguments) to ``SRun`` if
        ``use_cluster`` is True.

        """
        time = time and self.time
        slurm_cmd = 'srun' if use_cluster and self.use_cluster else None
        return self._SlurmCommand(
            target, source, action, slurm_cmd, time=time, **kw)

    def SAlloc(self, target, source, action, ncores,
               timelimit=None, time=True, **kw):
        """
        Run ``action`` with salloc.

        This method should be used for MPI jobs only. Combining an salloc call
        with ``mpirun`` (with no arguments) will use all nodes allocated
        automatically.

        Optional arguments:
        ``slurm_args``: Additional arguments to pass to salloc
        ``timelimit``: value to use for environment variable SALLOC_TIMELIMIT
        """
        slurm_args = kw.pop('slurm_args', '')
        slurm_args = ' '.join(['-n {0}'.format(ncores), slurm_args])
        e = self

        if timelimit is not None:
            clone = self.Clone()
            clone.SetTimeLimit(timelimit)
            e = clone

        slurm_cmd = 'salloc' if self.use_cluster else None

        return e._SlurmCommand(target, source, action, slurm_cmd,
                               time, slurm_args=slurm_args, **kw)

    def SRun(self, target, source, action, ncores=1,
             timelimit=None, slurm_queue=None, time=True, **kw):
        """
        Run ``action`` with srun.

        This method should be used for multithreaded jobs on a single
        machine only. By default, calls to SlurmEnvironment.Command
        use srun. Specify a number of processors with ``ncores``,
        which provides a value for ``srun -c/--cpus-per-task``.

        Optional arguments:
        ``slurm_args``: Additional arguments to pass to salloc
        ``timelimit``: Value to use for environment variable SLURM_TIMELIMIT
        """

        clone = self.Clone()
        if ncores > 1:
            clone.SetCpusPerTask(ncores)
        if timelimit is not None:
            clone.SetTimeLimit(timelimit)
        if slurm_queue is not None:
            clone.SetPartition(slurm_queue)

        slurm_cmd = 'srun' if self.use_cluster else None

        return clone._SlurmCommand(
            target, source, action, slurm_cmd, time, **kw)

    def Local(self, target, source, action, time=True, **kw):
        """
        Run a command locally, without SLURM
        """
        return self.Command(
            target, source, action, use_cluster=False, time=time, **kw)

    def SetPartition(self, partition):
        """
        Set the partition to be used. Subsequent calls
        to SRun and SAlloc will use this partition.
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
        Set a limit on the total run time
        for jobs launched by this environment.

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


class _SlurmAction(SCons.Action.CommandAction):
    def __init__(
            self, command, shell, slurm_cmd, time, slurm_args, verbose=False):
        if slurm_cmd:
            name = self.job_name(command)
            if time:
                action = _time + self._quote_action(shell, command)
            else:
                action = self._quote_action(shell, command)
            if slurm_args:
                action = f'{slurm_cmd} {slurm_args} -J "{name}" {action}'
            else:
                action = f'{slurm_cmd} -J "{name}" {action}'
        elif time:
            action = _time + command
        else:
            action = command
        self.command = action if verbose else command
        SCons.Action.CommandAction.__init__(self, action)

    def _quote(self, s):
        """Return a shell-escaped version of the string *s*."""
        if not s:
            return "''"
        if _find_unsafe(s) is None:
            return s

        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        return "'" + s.replace("'", "'\"'\"'") + "'"

    def _quote_action(self, shell, action):
        return shell + ' -c ' + self._quote(action)

    def job_name(self, command):
        command = command.split()
        name = command.pop(0)
        while name.startswith('$'):
            name = command.pop(0)
        return name

    def print_cmd_line(self, _, target, source, env):
        c = env.subst(self.command, SCons.Subst.SUBST_RAW, target, source)
        SCons.Action.CommandAction.print_cmd_line(self, c, target, source, env)
