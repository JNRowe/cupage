.. currentmodule:: cupage.utils

Utilities
=========

.. note::

  The documentation in this section is aimed at people wishing to contribute to
  `cupage`, and can be skipped if you are simply using the tool from the command
  line.

.. autoclass:: CupageEncoder

.. autofunction:: json_to_datetime

.. autofunction:: parse_timedelta

.. autofunction:: sort_packages

.. autofunction:: robots_test

The following three functions are defined for purely cosmetic reasons, as they
make the calling points easier to read.

.. autofunction:: success
.. autofunction:: fail
.. autofunction:: warn

Examples
--------

.. testsetup::

    from cupage import (fail, success)

Output formatting
'''''''''''''''''

    >>> success('well done!')
    '\x1b[38;5;10mwell done!\x1b[m\x1b(B'
    >>> fail('unlucky!')
    '\x1b[38;5;9munlucky!\x1b[m\x1b(B'
