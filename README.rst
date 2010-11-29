============
 sconstools
============

This package extends the scons build tool to support reproducible
research in bioinformatics.


Background
==========

Why does SCons make sense for reproducible bioinformatics pipelines?

* SCons has a sophisticated mechanism for determining dependencies, meaning that re-running SCons will only re-execute steps needing updating
* Most of the work of pipelines is done by external programs, and SCons is explicitly designed to make it easy to run external programs
* On the other hand, SCons also allows the execution of arbitrary python code in creating your script, and thus one can leverage the power of the python standard library, Biopython, NumPy, etc in your script.
* Rather than dealing with a mess of filenames, subsequent steps in an SCons build are expressed in terms of *file objects* 
* Steps in the pipeline are implemented using objects called "builders," which implement a system call or a python command in a in a way that consistently channels inputs into outputs
* Provides multiple mechanisms for cleanly executing isolated steps of the workflow 
* SCons validates files and can fail incrementally


Alternative tools
-----------------

make
  Make is a classic and everywhere, but getting make to do complex things requires specialized (and often opaque) syntax

ruffus
  ruffus_ is a lightweight way to automate bioinformatics pipelines.
  It also supports incremental recalculation.
  It does not, however, provide assistance for making system calls or managing files, and these must be done with explict sytem calls on "hand-built" strings.



Installation
============

dependencies
------------

scons
~~~~~

Development of this project begin using the 1.x version of scons, and
seems to work so far using version 2.x. Future development will focus
on version 2.x.

Seq
~~~

TODO: make Seq package available.

source
------

Obtain the source code from github. For read-only access::

 git clone git://github.com/nhoffman/sconstools.git

For committers::

 git clone git@github.com:nhoffman/sconstools.git

Then install::

 cd sconstools
 python setup.py install



.. Targets ..
.. _ruffus : http://wwwfgu.anat.ox.ac.uk/~lg/oss/ruffus/index.html
