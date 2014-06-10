==========
 bioscons
==========

This package extends the scons build tool for the construction of reproducible
workflows in bioinformatics.

This project is in fairly early stages of development, although I have
been using scons to create workflows using an earlier version of this
package for some time.


Background
==========

Why does SCons make sense for reproducible bioinformatics pipelines?

* SCons has a sophisticated mechanism for determining dependencies, meaning that re-running SCons will only re-execute steps needing updating
* Most of the work of pipelines is done by external programs, and SCons is explicitly designed to make it easy to run external programs
* On the other hand, SCons also allows the execution of arbitrary python code in creating your script, and thus one can leverage the power of the python standard library, Biopython, NumPy, etc in your script.
* Rather than dealing with a mess of filenames, subsequent steps in an SCons build are expressed in terms of *file objects* 
* Steps in the pipeline are implemented using objects called "builders," which implement a shell command or a python command in a in a way that consistently channels inputs into outputs
* Provides multiple mechanisms for cleanly executing isolated steps of the workflow 
* SCons validates files and can fail incrementally


Alternative tools
-----------------

make
  Make is a classic and everywhere, but getting make to do complex things requires specialized (and often opaque) syntax

ruffus
  ruffus_ is a lightweight way to automate bioinformatics pipelines.
  It also supports incremental recalculation.
  It does not, however, provide assistance for executing shell commands or managing files, and these must be done with explict sytem calls on "hand-built" strings.

galaxy 
  galaxy_ is a web-based tool for building remotely-executed
  workflows. This is a hugely attractive framework for exposing
  complex workflows using a graphical-interface, but occupies a very
  different niche from this project (which provides a command line
  interface to locally-executed programs).

Documentation
=============

Documentation is available on github: http://nhoffman.github.com/bioscons/

Installation
============

PyPi
============

Make sure to update the __version__ variable in the bioscons/__init__.py file.

If you have not done so create a ~/.pypirc file::

  python setup.py register

Proceed to build and upload::

  python setup.py clean
  python setup.py sdist bdist_wheel
  twine upload dist/*

dependencies
------------

scons
~~~~~

Development of this project begin using the 1.x version of scons, and
seems to work so far using version 2.x. Future development will focus
on version 2.x.

source
------

Obtain the source code from github. For read-only access::

 git clone git://github.com/nhoffman/bioscons.git

For committers::

 git clone git@github.com:nhoffman/bioscons.git

Then install::

 cd bioscons
 python setup.py install

.. Targets ..
.. _ruffus : http://wwwfgu.anat.ox.ac.uk/~lg/oss/ruffus/index.html
.. _galaxy : http://galaxy.psu.edu/
