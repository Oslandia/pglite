# How to release

* Increment the version number in setup.py
* Publish a tag
* Add a release on github
* Publish a new Windows package with https://gitlab.com/Oslandia/osgeo4w/tree/master/packages/python3-pglite
* (Publish a new Windows package for Python2 with https://gitlab.com/Oslandia/osgeo4w/tree/master/packages/python2-pglite)

Note: the publishing of a new package to pypi is done automatically by Travis, when the tag is pushed to GitHub.
