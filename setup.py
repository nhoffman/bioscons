import subprocess
import os
import sys

# Use setuptools, falling back on provided
try:
    from setuptools import setup, find_packages
    from setuptools.command.test import test as TestCommand
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup, find_packages
else:
    class PyTest(TestCommand):
        user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

        def initialize_options(self):
            TestCommand.initialize_options(self)
            self.pytest_args = []

        def finalize_options(self):
            TestCommand.finalize_options(self)
            self.test_args = []
            self.test_suite = True

        def run_tests(self):
            # import here, cause outside the eggs aren't loaded
            import pytest
            errno = pytest.main(self.pytest_args)
            sys.exit(errno)

subprocess.call(
    ('mkdir -p {pkg}/data && '
     'git describe --tags --dirty > {pkg}/data/ver.tmp '
     '&& mv {pkg}/data/ver.tmp {pkg}/data/ver '
     '|| rm -f {pkg}/data/ver.tmp').format(pkg='bioscons'),
    shell=True, stderr=open(os.devnull, "w"))

from bioscons import __version__, __doc__, MIN_SCONS_VERSION

params = {
    'author': 'Noah Hoffman',
    'author_email': 'noah.hoffman@gmail.com',
    'description': __doc__.strip(),
    'name': 'bioscons',
    'packages': find_packages(exclude=['tests']),
    'package_data': {'bioscons': ['data/ver']},
    'url': 'http://github.com/nhoffman/bioscons',
    'download_url': 'http://pypi.python.org/pypi/bioscons',
    'version': __version__,
    'install_requires': ['scons>={}'.format(MIN_SCONS_VERSION)],
}

# add 'test' command if setuptools is available
try:
    params.update({'tests_require': ['pytest'], 'cmdclass': {'test': PyTest}})
except NameError:
    pass

setup(**params)
