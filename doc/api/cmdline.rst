.. currentmodule:: cupage.cmdline

Command line
============

.. note::

  The documentation in this section is aimed at people wishing to contribute to
  `cupage`, and can be skipped if you are simply using the tool from the command
  line.

.. autodata:: USAGE

.. autofunction:: main

.. autofunction:: add
.. autofunction:: check
.. autofunction:: list_conf
.. autofunction:: list_sites
.. autofunction:: remove

Examples
--------

.. testsetup::

    from cupage import process_command_line

Parse command line options
''''''''''''''''''''''''''

    >>> options, args = process_command_line()
