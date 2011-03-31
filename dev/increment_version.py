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

    if sys.argv[1:] and '-h' in sys.argv[1]:
        print __doc__
        sys.exit()
    
    current_ver = shell(["git", "describe"])
    ver_info = [int(x) for x in current_ver.split('.')]
    ver_info[-1] += 1
    new_version = '.'.join(str(x) for x in ver_info[:2])
    new_release = '.'.join(str(x) for x in ver_info)

    print 'incrementing version:',current_ver,'--->', new_release

    print 'updating version in bioscons/__init__.py'
    for line in fileinput.input('bioscons/__init__.py', inplace=True):
        if line.startswith('__version__'):
            line = '__version__ = "%s"\n' % new_release
        sys.stdout.write(line)
    fileinput.close()

    print 'updating version and release in docs/conf.py'
    for line in fileinput.input('bioscons/__init__.py', inplace=True):
        if line.startswith('version ='):
            line = "version ='%s'\n" % new_version
        elif line.startswith('release ='):
            line = "release ='%s'\n" % new_release
        sys.stdout.write(line)
    fileinput.close()
    
    # increment git tag
    # shell(['git','tag','-a','-m','"version increment using increment_version.py"','"%s"'%new_ver])
    

if __name__ == '__main__':
    main()

    
