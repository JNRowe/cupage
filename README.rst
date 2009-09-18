CUPage - Check for Updated Pages
================================

Introduction
------------

``cupage`` is a tool to check for updates on web pages.

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

..
    :vim: set ft=rst ts=4 sw=4 et:

