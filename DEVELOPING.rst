=====================
 Developing bioscons
=====================

Here's the quick version of the release process, but see details
below.

- run tests!
- update CHANGELOG.rst
- make final commits to feature branch
- merge feature branch into master
- run tests again!
- update the git tag
- `git push origin master`
- `git push --tags`
- update PyPi (see below)
- update the docs: `(cd docs && make html)`
- publish the updated docs: `ghp-import -p html`


development workflow
====================

* Use a feature branch workflow as much as possible
  * open an issue describing the feature
  * create a new branch named using the issue number and some keywords
    (eg "004-add-runcible-spoon")
  * create a pull request
  * merge after code review, testing, etc
  * delete the feature branch and resolve the issue
* The head of the master branch should always be deployable to production.
* Version numbers are in the format
  ``v<major>.<minor>.<incremental>``, for example ``v0.1.0``
* Merging to master constitutes a release, so test comprehensively
  before merging.
* Add an annotated git tag and update CHANGES.rst when you perform a
  release.

So performing a release of version v0.2.0 of a branch named
`my-feature` looks more or less like::

  git checkout master
  git pull origin master
  git merge my-feature
  git tag -a -m 'v0.2.0' v0.2.0
  git push origin master
  git push --tags

You might also want to delete the local and remote versions of the
feature branch once the merge is complete::

  git branch -d my-feature    # detele local branch
  git push origin :my-feature # delete remote branch

Note that setup.py uses ``git describe --tags --dirty`` to generate the
version number. You will need to run setup.py after adding a tag to
update the version. This happens in the course of installing the
package or creating a source code distribution, but ``setup.py -h`` will
do it as well. Also be sure to perform a "git fetch" to get any new
tags from the remote.

PyPi
====

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
sure that this is up to date. Then enter the `docs` directory and
build the docs. (Yes, I know this is a project about scons and there's
a Makefile in there. Thanks for pointing that out.) Note that the html
directory needs to contain a file named `.nojekyll` to prevent GitHub
from ignoring pages with leading underscores (like `_static`), so the
Makefile adds one::

  (cd docs && make html)

Thankfully, publishing to the GitHub page for the bioscons repository
is easy using `ghp-import`::

  ghp-import -p html

