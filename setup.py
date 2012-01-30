"""
install package:        python setup.py install
create unix package:    python setup.py sdist
"""

from distutils.core import setup
import glob

from bioscons.__init__ import __version__

# all files with .py extension in top level are assumed to be scripts
scripts = list(set(glob.glob('*.py')) - set(['setup.py']))

params = {'author': 'Noah Hoffman',
          'author_email': 'noah.hoffman@gmail.com',
          'description': 'Functions extending the scons build tool for reproducible research in bioinformatics.',
          'name': 'bioscons',
          'package_dir': {'bioscons': 'bioscons'},
          'packages': ['bioscons'],
          'scripts': scripts,
          'url': 'http://github.com/nhoffman/bioscons',
          'version': __version__,
          'requires':['python (>= 2.7)','scons (>= 2.0)']}

setup(**params)
