import os
import sys
import glob
import subprocess

# Ensure that a virtualenv is active before importing non-stdlib dependencies.
venv = os.environ.get('VIRTUAL_ENV')
if not venv:
    sys.exit('--> an active virtualenv is required'.format(venv))

import SCons
from SCons.Script import (SConscript, Environment, Variables,
                          Depends, Help, Dir, Flatten, Alias, Default,
                          GetOption)

# Ensure that the bioscons version number is up to date with the git
# repository before importing.
subprocess.call(['python', 'setup.py', '-h'], stdout=open(os.devnull, 'w'))
import bioscons

# Define some PATH elements explicitly.
PATH = ':'.join([
    'bin', os.path.join(venv, 'bin'), os.environ['PATH']])

vars = Variables()

# SHELLOPTS sets shell options to fail (including piped commands) with
# nonzero exit status; this requires bash.
env = Environment(
    ENV=dict(os.environ, PATH=PATH, SHELLOPTS='errexit:pipefail'),
    variables=vars,
    SHELL='bash',
    version=bioscons.__version__
)

Help(vars.GenerateHelpText(env))

# Run all subsidiary SConstruct scripts in the tests directory; see
# http://www.scons.org/doc/production/HTML/scons-user.html#chap-hierarchical
bioscons_source = glob.glob('bioscons/*.py')

scons_tests = SConscript(glob.glob('tests/*/SConstruct*'),
                         ['env', 'PATH'])
Depends(scons_tests, bioscons_source)

py_tests = env.Command(
    target='tests.log',
    source=bioscons_source,
    action='python setup.py test | tee $TARGET || rm -f $TARGET'
)
Depends(py_tests, glob.glob('tests/*.py'))

tests = Flatten([scons_tests, py_tests])
Alias('test', tests)

# Build a tarball and wheel (note that the wheel name replaces hyphens
# with underscores)
build = env.Command(
    target=[
        'dist/bioscons-{}-py2-none-any.whl'.format(env['version'].replace('-', '_')),
        'dist/bioscons-${version}.tar.gz'],
    source=bioscons_source,
    action=['python setup.py clean',
            'python setup.py sdist bdist_wheel']
)
Alias('build', build)
Default(build)
Depends(build, tests)

# Compile Sphinx docs
docs_index = env.Command(
    target='html/index.html',
    source=Flatten([
        glob.glob('docs/*.rst'),
        glob.glob('docs/*.py'),
        bioscons_source,
    ]),
    action="cd docs && make html"
    )
Alias('docs', docs_index)
Default(docs_index)

# Non-default commands are below (eg, use 'scons name-of-alias' to execute)

# upload to pypi
pypirc = os.path.expanduser('~/.pypirc')
if os.path.exists(pypirc):
    pypi_log = env.Command(
        target='dist.log',
        source=build,
        action='twine upload $SOURCES > $TARGET'
        )
    Alias('pypi', pypi_log)
    Depends(pypi_log, pypirc)

# Publish Sphinx docs
publish_log = env.Command(
    target='docs_publish.log',
    source=docs_index,
    action='ghp-import -p html')
Alias('publish-docs', publish_log)

if GetOption('help'):
    print 'Available Build Aliases:'
    print '-----'
    for alias in sorted(SCons.Node.Alias.default_ans.keys()):
        print alias
