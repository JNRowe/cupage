.. currentmodule:: cupage.utils

Utilities
=========

.. note::

  The documentation in this section is aimed at people wishing to contribute to
  `cupage`, and can be skipped if you are simply using the tool from the command
  line.

.. autofunction:: sort_packages

HTTP utilities
~~~~~~~~~~~~~~

.. autofunction:: robots_test

.. autofunction:: charset_from_headers

Output utilities
~~~~~~~~~~~~~~~~

.. autofunction:: term_link

Development tools
~~~~~~~~~~~~~~~~~

.. autofunction:: maybe_profile

Examples
--------

Development tools
~~~~~~~~~~~~~~~~~

.. doctest::
   :options: +SKIP

    >>> with maybe_profile():
    ...     time.sleep(10)
