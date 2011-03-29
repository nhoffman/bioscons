import os
import sys
import glob

vars = Variables()
env = Environment(ENV=os.environ, variables=vars)

# run all subsidiary SConstruct scripts in the tests directory
# see http://www.scons.org/doc/production/HTML/scons-user.html#chap-hierarchical
SConscript(glob.glob('tests/*/SConstruct'))

    
