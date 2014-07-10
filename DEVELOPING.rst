=====================
 Developing bioscons
=====================

PyPi
====

Make sure to update the __version__ variable in the bioscons/__init__.py file.

If you have not done so create a ~/.pypirc file::

  python setup.py register

Proceed to build and upload::

  python setup.py clean
  python setup.py sdist bdist_wheel
  twine upload dist/*

Building docs with Sphinx
=========================

It's best to create and activate a virtualenv first to provide all of
the requirements for building and publishing the documentation::

  bin/mkvenv.sh
  source bioscons-env/bin/activate

The Sphinx configuration uses git tags to define the version, so make
sure both that the __version__ variable in bioscons/__init__.py is
set, and that the most recent git tag matches it. Then enter the
`docs` directory and build the docs. (Yes, I know this is a project
about scons and there's a Makefile in there. Very funny, thanks for
pointing that out.) Note that the html directory needs to contain a
file named `.nojekyll` to prevent GitHub from ignoring pages with
leading underscores (like `_static`), so the Makefile adds one::

  (cd docs && make html)

Thankfully, publishing to the GitHub page for the bioscons repository
is easy using `ghp-import`::

  ghp-import -p html

