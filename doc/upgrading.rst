Upgrading notes
===============

Beyond the high-level notes you can find in NEWS.rst_, you’ll find some more
specific upgrading advice in this document.

.. contents::
   :local:

Switch to |JSON| (0.3.0)
------------------------

Versions prior to 0.3 used a :mod:`pickle`-backed database, however it was
deemed more useful to make the data available to users who weren’t working with
Python.

Conversion is manual, but can be performed with a simple :func:`pickle.load`
followed by :func:`json.dump`.

.. _NEWS.rst: https://github.com/JNRowe/jnrbase/blob/master/NEWS.rst
