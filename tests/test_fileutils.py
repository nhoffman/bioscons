#!/usr/bin/env python

import os
from os import path
import unittest
import logging

from bioscons.fileutils import rename, split_path

log = logging

class TestRename(unittest.TestCase):

    def test01(self):
        fname = 'someplace/test.txt'
        self.assertTrue(rename(fname) == fname)

    def test02(self):
        fname = 'someplace/test.txt'
        self.assertTrue(rename(fname, ext='.buh') == 'someplace/test.buh')

    def test03(self):
        fname = 'someplace/test.txt'
        self.assertTrue(rename(fname, pth='elsewhere') == 'elsewhere/test.txt')

    def test04(self):
        fname = 'someplace/test.txt'
        self.assertTrue(rename(fname, ext='.buh', pth='elsewhere') == 'elsewhere/test.buh')

class TestSplitPath(unittest.TestCase):
    
    def test01(self):
        fname = 'someplace/test.txt'
        dirname, basename = split_path(fname)
        self.assertTrue(dirname == 'someplace')
        self.assertTrue(basename == 'test.txt')

    def test02(self):
        fname = 'someplace/test.txt'
        dirname, basename, ext = split_path(fname, split_ext = True)
        self.assertTrue(dirname == 'someplace')
        self.assertTrue(basename == 'test')
        self.assertTrue(ext == '.txt')        

    def test03(self):
        """
        fname can be a list or tuple, and only the first element is used
        """
        
        fname = 'someplace/test.txt'
        self.assertTrue(split_path(fname) == split_path([fname]))
        self.assertTrue(split_path(fname) == split_path((fname,)))
        self.assertTrue(split_path(fname) == split_path((fname, None)))        
