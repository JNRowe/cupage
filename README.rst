CUPage - Check for Updated Pages
================================

.. image:: https://secure.travis-ci.org/JNRowe/cupage.png?branch=master
   :target: https://travis-ci.org/JNRowe/cupage

``cupage`` is a tool to check for updates on web pages.

``cupage`` is released under the `GPL v3`_ license.

Requirements
------------

``cupage``’s dependencies outside of the standard library are:

* click_ ≥ 7.0
* configobj_ ≥ 5.0.0
* cssselect_ ≥ 0.7.0
* httplib2_ ≥ 0.7
* lxml_ ≥ 3.0.0

It should work with any version of Python_ 3.6 or newer.  If ``cupage`` doesn’t
work with the version of Python you have installed, file an issue_ and I’ll
endeavour to fix it.

The module has been tested on many UNIX-like systems, including Linux and OS X,
but it should work fine on other systems too.

To run the tests you’ll need pytest_.  Once you have pytest_ installed you can
run the tests with the following commands::

    $ pytest tests

Example
-------

The simplest way to show how ``cupage`` works is by example.  The
following is an example configuration file::

    # dev-python
    [pep8]
    site = pypi
    match_type = tar
    [pydelicious]
    site = google code
    match_type = zip
    [pyisbn]
    url = http://www.jnrowe.ukfsn.org/_downloads/
    select = pre > a
    match_type = tar
    frequency = 6m
    [upoints]
    url = http://www.jnrowe.ukfsn.org/_downloads/
    select = pre > a
    match_type = tar
    [fruity]
    site = vim-script
    script = 1871
    [cupage]
    site = github
    user = JNRowe
    frequency = 1m

Contributors
------------

I’d like to thank the following people who have contributed to ``cupage``.

Patches
'''''''

* <Your name here?>

Bug reports
'''''''''''

* Matt Leighy

Ideas
'''''

* <Your name here?>

If I’ve forgotten to include your name I wholeheartedly apologise.  Just drop
me a mail_ or open an issue_, and I’ll update the list!

Bugs
----

If you find any problems, bugs or just have a question about this package either
file an issue_ or drop me a mail_.

If you’ve found a bug please attempt to include a minimal testcase so I can
reproduce the problem, or even better a patch!

.. _GPL v3: https://www.gnu.org/licenses/
.. _click: https://pypi.python.org/pypi/click/
.. _configobj: https://pypi.python.org/pypi/configobj/
.. _cssselect: https://pypi.python.org/pypi/cssselect/
.. _httplib2: http://code.google.com/p/httplib2/
.. _lxml: http://lxml.de/
.. _Python: https://www.python.org/
.. _issue: https://github.com/JNRowe/cupage/issues/
.. _pytest: https://pypi.python.org/pypi/pytest/
.. _mail: jnrowe@gmail.com
