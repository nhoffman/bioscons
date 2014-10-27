import subprocess
import os

# Use setuptools, falling back on provided
try:
    from setuptools import setup, find_packages
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup, find_packages

subprocess.call(
    ('git describe --tags --dirty > bioscons/data/ver.tmp'
     '&& mv bioscons/data/ver.tmp bioscons/data/ver '
     '|| rm -f bioscons/data/ver.tmp'),
    shell=True, stderr=open(os.devnull, "w"))

from bioscons import __version__, __doc__

params = {'author': 'Noah Hoffman',
          'author_email': 'noah.hoffman@gmail.com',
          'description': __doc__.strip(),
          'name': 'bioscons',
          'packages': find_packages(exclude=['tests']),
          'package_data': {'bioscons': ['data/ver']},
          'url': 'http://github.com/nhoffman/bioscons',
          'download_url': 'http://pypi.python.org/pypi/bioscons',
          'version': __version__,
          'requires': ['python (>= 2.7)',
                       'scons (>= 2.0)']}

setup(**params)
