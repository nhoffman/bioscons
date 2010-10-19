import sys
import traceback

_base_version = '0.1'
try:
    __version__ = '%s.%s' % (_base_version, '$Rev: 14 $'.split()[1])
except IndexError:
    __version__ = _base_version

__version_info__ = tuple([ int(num) for num in __version__.split('.')])

_min_python_version = '2.6.0'

def _check_python_version():
    vsplit = lambda x: tuple([int(n) for n in x.split('.')])
    sys_version = sys.version.split()[0]
    version = vsplit(sys_version)
    if version < vsplit(_min_python_version):
        raise SystemError('this package requires Python version %s or greater (current version is %s)' % (_min_python_version, sys_version))

_check_python_version()

try:
    import utils
    import builders
except (NameError, ImportError), msg:
    # we expect this to fail unless imported from within SConstruct
    traceback.print_exc(file=sys.stdout)




