#!/usr/bin/env python

"""
usage:

./increment_version.py

Retrieve the curent version stored as an annotated git tag in the
format 'major.minor.release', increment 'release', and create a new
tag to store the new version. Then update bioscons/__init__.py to
reflect the new vaule. If you want to increment 'major' or 'minor',
use 'git tag -a'.
"""

from subprocess import Popen, PIPE
import fileinput
import sys

def shell(args):
    return Popen(args, stdout=PIPE).communicate()[0].strip()
    
def main():

    if '-h' in sys.argv[1]:
        print __doc__
        sys.exit()
    
    current_ver = shell(["git", "describe"])
    ver_info = [int(x) for x in current_ver.split('.')]
    ver_info[-1] += 1
    new_ver = '.'.join(str(x) for x in ver_info)

    print 'incrementing version:',current_ver,'--->', new_ver

    # update version in bioscons/__init__.py
    for line in fileinput.input('bioscons/__init__.py', inplace=True):
        if line.startswith('__version__'):
            sys.stdout.write('__version__ = "%s"\n' % new_ver)
        else:
            sys.stdout.write(line)
    fileinput.close()
    
    # increment git tag
    shell(['git','tag','-a','-m','"version increment using increment_version.py"','"%s"'%new_ver])
    

if __name__ == '__main__':
    main()

    
