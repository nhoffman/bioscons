"""
install package:        python setup.py install
create unix package:    python setup.py sdist
"""

from distutils.core import setup
import glob
from __init__ import __version__, _check_python_version, _min_python_version
_check_python_version()

scripts = glob.glob('scripts/*.py')

params = {'author': 'Noah Hoffman',
          'author_email': 'noah.hoffman@gmail.com',
          'description': 'Functions extending the scons build tool to support "reproducible research" in bioinformatics.',
          'name': 'sconstools',
          'package_dir': {'sconstools': '.'},
          'packages': ['sconstools'],
          'scripts': scripts,
          'url': 'https://code.google.com/p/sconstools/',
          'version': __version__,
          'requires':['python (>= %s)' % _min_python_version,'scons (>= 1.3)', 'Seq']}

setup(**params)
