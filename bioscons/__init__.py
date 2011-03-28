__version__ = "0.1.2"
__version_info__ = tuple([ int(num) for num in __version__.split('.')])

# _min_python_version = '2.6.0'

# def _check_python_version():
#     vsplit = lambda x: tuple([int(n) for n in x.split('.')])
#     sys_version = sys.version.split()[0]
#     version = vsplit(sys_version)
#     if version < vsplit(_min_python_version):
#         raise SystemError('this package requires Python version %s or greater (current version is %s)' \
#                               % (_min_python_version, sys_version))

# _check_python_version()

