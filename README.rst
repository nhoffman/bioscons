==========
 bioscons
==========

This package extends the scons build tool for the construction of
reproducible workflows in bioinformatics.

This project is in fairly early stages of development, although it is
being used fairly heavily by the developers to support both research
and clinical computational pipelines.

Documentation is available on github: http://nhoffman.github.io/bioscons/

Background
==========

Why does SCons make sense for reproducible bioinformatics pipelines?

* SCons has a sophisticated mechanism for determining dependencies,
  meaning that re-running SCons will only re-execute steps needing
  updating
* Most of the work of pipelines is done by external programs, and
  SCons is explicitly designed to make it easy to run external
  programs
* On the other hand, SCons also allows the execution of arbitrary
  python code in creating your script, and thus one can leverage the
  power of the python standard library, Biopython, NumPy, etc in your
  script.
* Rather than dealing with a mess of filenames, subsequent steps in an
  SCons build are expressed in terms of *file objects*
* Steps in the pipeline are implemented as *Commands* which implement
  a shell command or a python function in a in a way that consistently
  channels inputs into outputs
* Provides multiple mechanisms for cleanly executing isolated steps of
  the workflow (for example, by previewing commands to be executed
  using ``scons -n``, and pasting a single command directly into the
  shell)
* SCons validates files and can fail incrementally

Installation
============

dependencies
------------

* Python 2.7, 3.5+
* scons 2.4+

installation scenarios
----------------------

Various installation scenarios are possible involving different
combinations of system package installers, pip, and virtualenv vs
system installs. We will describe only the recommended configuration
here, although others are possible. Note that although ``bioscons``
*should* work with scons 2.4+, ``scons`` itself is only compatible
with python 3 in versions > 3.0.0

Install both scons and bioscons to a virtualenv
-----------------------------------------------

We strongly recommend installing both this package and ``scons`` to a
virtualenv rather than to your system due to idiosyncrasies in the
``scons`` installation script, and the fact that an older version of
``scons`` is likely to be installed by package managers. This option
is available using either python 2.7 or 3.5+

Start by creating a virtualenv. For python2.7::

  virtualenv bioscons-env

and for python 3.5+::

  python3 -m venv bioscons-env

Due to some quirks in the ``scons`` installation process, you must
ensure that ``pip`` is the most recent version, and ``wheel`` is
installed::

  source bioscons-env/bin/activate
  pip install -U pip wheel
  pip install bioscons

Take care that pip corresponds to the intended version of the python
interpreter; a safer option may be to use ``pip2`` or ``pip3``.

installation from source (for development)
------------------------------------------

::

  https://github.com/nhoffman/bioscons.git
  cd bioscons
  python3 -m venv bioscons-env
  # or, for python2: virtualenv bioscons-env
  source bioscons-env/bin/activate
  pip install -U pip wheel
  pip install -e .
  pip install -r requirements.txt  # to run tests, build docs

Defining the execution environment for reproducible pipelines
=============================================================

When intending to run the version of ``scons`` installed to the
virtualenv, it is a good idea to include the following directive in
your ``SConstruct``::

  venv = os.environ.get('VIRTUAL_ENV')
  if not venv:
      sys.exit('--> an active virtualenv is required')

It is best to define the ``$PATH`` used to locate executables that are
used within your pipeline.


