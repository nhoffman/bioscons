import os
import sys
from os.path import join,split,splitext
import re
import pprint
import glob

try:
    from SCons.Script import *
except ImportError:
    # we expect this to fail unless imported from within SConstruct
    pass

def sweave_generator(source, target, env, for_signature):
    dirname, fname = split(str(source[0]))

    action = ''
    if dirname:
        action += 'cd "%s" && ' % dirname

    action += r'echo Sweave\(\"%s\"\) | R --slave' % fname

    # action += 'R CMD Sweave "%s"' % fname

    if len(source) > 1:
        action += ' --args ${SOURCES[1:]}'

    return action

build = Builder(
    generator=sweave_generator,
    emitter=lambda target, source, env: (splitext(str(source[0]))[0]+'.tex', source)
)

