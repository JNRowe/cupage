.. currentmodule:: cupage

``Site``
===========

.. note::

  The documentation in this section is aimed at people wishing to contribute to
  `cupage`, and can be skipped if you are simply using the tool from the command
  line.

..
    We don't use ``autodata`` for ``SITES`` as it includes all the data, and it
    looks very messy

.. data:: SITES
   :annotation: = {}

    Site specific configuration data

.. autodata:: USER_AGENT

.. autoclass:: Site
.. autoclass:: Sites

Examples
--------

.. testsetup::

    from cupage import Sites

Reading stored configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    >>> sites = Sites()
    >>> sites.load('support/cupage.conf', 'support/cupage.db')
    >>> sites[0].frequency
    360000

Writing updates
~~~~~~~~~~~~~~~

    >>> sites.save('support/cupage.db')
