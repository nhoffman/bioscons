"""
install package:        python setup.py install
create unix package:    python setup.py sdist
"""
# Use setuptools, falling back on provided
try:
    from setuptools import setup, find_packages
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup, find_packages

import glob

from bioscons.__init__ import __version__

# all files with .py extension in top level are assumed to be scripts
scripts = list(set(glob.glob('*.py')) - set(['setup.py']))

params = {'author': 'Noah Hoffman',
          'author_email': 'noah.hoffman@gmail.com',
          'description': 'Functions extending the scons build tool for reproducible research in bioinformatics.',
          'name': 'bioscons',
          'packages': find_packages(),
          'scripts': scripts,
          'url': 'http://github.com/nhoffman/bioscons',
          'download_url': 'http://pypi.python.org/pypi/bioscons',
          'version': __version__,
          'requires':['python (>= 2.7)','scons (>= 2.0)']}

setup(**params)
