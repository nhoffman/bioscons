import os
import sys
import glob

vars = Variables()
env = Environment(ENV=os.environ, variables=vars)

# run all subsidiary SConstruct scripts in the tests directory
SConscript(glob.glob('tests/*/SConstruct'))

# for dirpath, dirnames, filenames in os.walk('tests'):
#     print dirpath, dirnames, filenames
    
