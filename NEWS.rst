``cupage``
==========

User-visible changes
--------------------

.. contents::

0.7.0 - 2012-02-03
------------------

* Added ``bitbucket`` and ``savannah`` site matchers
* Support for ``re.VERBOSE`` matchers
* Safer database updates
* httplib2_ 0.7 is now required
* Improved the robustness of config file reading, thanks to configobj_
* Now requires blessings_
* Fixes for people using distribute_ to install

.. _blessings: http://pypi.python.org/pypi/blessings/
.. _distribute: http://pypi.python.org/pypi/distribute

0.6.0 - 2011-07-17
------------------

* Compatible with httplib2_ 0.7
* Various updates to GitHub matcher
* All versions now reported in hackage_ checks

.. _hackage: http://hackage.haskell.org/

0.5.6 - 2011-05-25
------------------

* Updated Debian_ matcher to search for Debian_ specific tarballs

0.5.5 - 2011-04-05
------------------

* Updated Debian_ matcher to search for bzip2_ compressed files

.. _Debian: http://debian.org/
.. _bzip2: http://www.bzip.org/

0.5.4 - 2011-01-03
------------------

* Switched to documented API for GitHub_ matcher, fixes 404s

0.5.3 - 2011-01-03
------------------

* Updated GitHub_ matcher, for recent site changes

0.5.2 - 2010-12-20
------------------

* Now uses termcolor_ for coloured output
* Updated GitHub_ URLs, to remove spurious warnings

.. _termcolor: http://pypi.python.org/pypi/termcolor/
.. _GitHub: https://github.com/

0.5.1 - 2010-06-16
------------------

* Fixed ``pypi`` site matcher to work with robots.txt_ support

0.5.0 - 2010-06-08
------------------

* Added ``--list-sites`` option to display built-in supported sites
* More complete documentation using the wonderful Sphinx_
* Support for robots.txt_
* Python v2.6 or a later release from the v2 branch is required, unfortunately
  Python v3 isn't supported yet
* httplib2_ and ConfigObj_ are now required

.. _Sphinx: http://sphinx.pocoo.org/
.. _robots.txt: http://www.robotstxt.org/
.. _httplib2: http://code.google.com/p/httplib2/
.. _ConfigObj: http://pypi.python.org/pypi/configobj

0.4.0 - 2010-01-22
------------------

* Added configurable per-site check frequency
* Added ``cpan`` site matcher
* ``hackage`` site matcher fix for recent upstream changes

0.3.1 - 2010-01-11
------------------

* Added ``github`` site matcher

0.3.0 - 2009-11-17
------------------

* Coloured output with termstyle_
* New ``vim-script`` site matcher
* New ``debian`` site matcher
* Switched to JSON_ as database format
* Better handling of HTTP errors

.. _termstyle: http://github.com/gfxmonk/termstyle
.. _JSON: http://www.json.org/

0.1.0 - 2009-09-18
------------------

    * Initial release
