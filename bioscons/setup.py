import os

try:
    import SCons
    from SCons.Script import (Help, GetOption, Environment, Variables)
except ImportError:
    # we expect this to fail unless imported from within SConstruct
    pass


def envsetup(vars=None, environ=None, PATH=None, bash=True, **kwargs):
    vars = vars or Variables()
    environ = os.environ.copy() if environ is None else environ

    if PATH:
        environ['PATH'] = PATH

    env = Environment(ENV=environ, variables=vars, **kwargs)

    if bash:
        use_bash(env)

    return env


def use_bash(env, shellopts='errexit:pipefail'):
    # SHELLOPTS sets shell options to fail (including piped
    # commands) with nonzero exit status; this requires bash.
    env['SHELL'] = 'bash'
    env['ENV']['SHELLOPTS'] = shellopts


def helpsetup(vars, env):
    """Makes `scons -h` print help text.

    """

    Help(vars.GenerateHelpText(env))
    if GetOption('help') and SCons.Node.Alias.default_ans.keys():
        print 'Build Aliases:'
        for alias in sorted(SCons.Node.Alias.default_ans.keys()):
            print ' ', alias
