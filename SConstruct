import os
import sys

vars = Variables()
vars.Add(('RSTFLAGS','flags for rst2html.py','--generator --date --toc-top-backlinks'))

env = Environment(ENV=os.environ, variables=vars)

env['BUILDERS']['rst2html'] = Builder(
    action = 'rst2html.py $RSTFLAGS $SOURCE $TARGET'
    )

env.rst2html('README.html','README.txt')
