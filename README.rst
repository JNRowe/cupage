CUPage - Check for Updated Pages
================================

Introduction
------------

``cupage`` is a tool to check for updates on web pages.

Requirements
------------

``cupage``'s only dependency outside of the standard library is the
fantastic lxml_.  It should run with Python 2.5 or newer [#]_.  If
``cupage`` doesn't work with the version of Python you have installed,
drop me a mail_ and I'll endeavour to fix it.

The modules have been tested on many UNIX-like systems, including Linux,
Solaris and OS X, but it should work fine on other systems too.  The
modules and scripts contain a large collection of ``doctest`` tests that
can be checked with ``./setup test_code``, and the code examples in the
documentation can be tested with ``./setup test_doc``.

.. [#] If you still use Python v2.4 only small changes are required, for
       example to the base class definitions and the unrolling of
       conditional expressions.


Example
-------

The simplest way to show how ``cupage`` works is by example.  The
following is an example configuration file.

.. code-block:: ini

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
    [upoints]
    url = http://www.jnrowe.ukfsn.org/_downloads/
    select = pre > a
    match_type = tar

libcupage
'''''''''

All the class definitions, methods and independent functions contain
hopefully useful usage examples in the docstrings.  You can run the
examples as tests with ``./setup.py test_code``.

API Stability
-------------

API stability isn't guaranteed across versions, although frivolous
changes won't be made.

When ``cupage`` 1.0 is released the library API will be frozen, and any
changes which aren't backwards compatible will force a major version
bump.

Hacking
-------

Patches are most welcome, but I'd appreciate it if you could follow the
guidelines below to make it easier to integrate your changes.  These are
guidelines however, and as such can be broken if the need arises or you
just want to convince me that your style is better.

  * `PEP 8`_, the style guide, should be followed where possible.
  * While support for Python versions prior to v2.5 may be added in the
    future if such a need were to arise, you are encouraged to use v2.5
    features now.
  * All new classes and methods should be accompanied by new
    ``doctest`` examples, and epydoc_'s epytext formatted descriptions if
    at all possible.
  * Tests *must not* span network boundaries, see ``test.mock`` for
    workarounds.
  * ``doctest`` tests in modules are only for unit testing in general,
    and should not rely on any modules that aren't in Python's standard
    library.
  * Functional tests should be in the ``doc`` directory in
    reStructuredText_ formatted files, with actual tests in ``doctest``
    blocks.  Functional tests can depend on external modules, but they
    must be Open Source.

New examples for the ``doc`` directory are as appreciated as code
changes.

Bugs
----

If you find any problems, bugs or just have a question about this
package either drop me an email_ or file an issue_.  Locally bugs are
managed with ditz_, so if you're working with a clone of the repository
you can report, list and fix bugs using ``ditz``.

If you've found please attempt to include a minimal testcase so I can
reproduce the problem, or even better a patch!

.. _lxml: http://codespeak.net/lxml/
.. _PEP 8: http://www.python.org/dev/peps/pep-0008/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _mail: jnrowe@gmail.com
.. _issue: http://github.com/JNRowe/``module``/issues
.. _ditz: http://ditz.rubyforge.org/

..
    :vim: set ft=rst ts=4 sw=4 et:

