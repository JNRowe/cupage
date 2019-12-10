Configuration
-------------

:program:`cupage` stores its configuration in :file:`~/.cupage.conf` by default,
although you can specify a different location with the :option:`cupage list -f`
command line option.

The configuration file is a ``INI`` format file, with a section for each site
definition.  The section header is the site’s name which will be displayed in
the update output, or used to select individual sites to check on the command
line.  Each section consists a collection of ``name=value`` option pairs.

An example configuration file is below:

.. code-block:: ini

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

Site definitions can either be specified entirely manually, or possibly with the
built-in site matchers(see :ref:`site-label` for available options).

``frequency`` option
''''''''''''''''''''

The ``frequency`` option allows you to set a minimum time between checks for
specific sites within the configuration file.

The format is ``<value> <units>`` where value can be an integer or float, and
units must be one of the entries from the table below:

====  ========================================
Unit  Purpose
====  ========================================
h     Hours
d     Days
w     Week
m     Month, which is defined as 28 days
y     Year, which is defined as 13 ``m`` units
====  ========================================

``match`` option
''''''''''''''''

If ``match_type`` is ``re`` then ``match`` must be a valid regular expression
that will be used to match within the selected elements.  For most common uses
a prebuilt ``match_type`` already exists(see :ref:`match_type-label`), and
``re`` should really only be used as a last resort.

The Python re_ module is used, and any functionality allowed by the module is
available in the ``match`` option(with the notable exception of the ``verbose``
syntax).

.. note::

    If you find yourself using the ``re`` type, please consider opening an
    issue_ with your requirements.  Doing so will allow other users to benefit
    from your knowledge, and means I’ll maintain compatibility for you ;)

.. _match_type-label:

``match_type`` option
'''''''''''''''''''''

The ``match_type`` value, if used, must be one of the following:

==========  ===========================================================
Match type  Purpose
==========  ===========================================================
``re``      to define custom regular expressions
``tar``     to match gzip_/bzip2_/xz_ compressed tar_ archives(default)
``zip``     to match zip_ archives
==========  ===========================================================

The ``match_type`` values simply select a predefined regular expression to use.
The base match is :regexp:`<name>-[\\d\\.]+([_-](pre|rc)[\\d]+)?\\.<type>`,
where ``<name>`` is the section name and ``<type>`` is the value of
``match_type`` for this section.

``select`` option
'''''''''''''''''

The ``select`` option, if used, must be a valid |CSS| or XPath selector
depending on the value of ``selector`` (see :ref:`selector-label`) .  Unless
specified |CSS| is the default selector type.

.. _selector-label:

``selector`` option
'''''''''''''''''''

The ``selector`` option, if used, must be one of the following:

========  ===================================================================
Selector  Purpose
========  ===================================================================
css       To select elements within the page using `CSS selectors`_ (default)
xpath     To select elements within the page using XPath_ selectors
========  ===================================================================

.. _site-label:

``site`` option
'''''''''''''''

The ``site`` option, if used, must be one of the following, hopefully
self-explanatory values:

===============  ======  ==============================================
Site             Added   Required options
===============  ======  ==============================================
``cpan``         v0.4.0
``debian``       v0.3.0
``failpad``      v0.5.0
``github``       v0.3.1  ``user`` (GitHub_ user name for project owner)
``google code``  v0.1.0
``hackage``      v0.1.0
``pypi``         v0.1.0
``vim-script``   v0.3.0  ``script`` (script id on the `vim website`_)
===============  ======  ==============================================

``site`` options are simply shortcuts that are provided to reduce duplication in
the configuration file.  They define the values necessary to check for updates
on the given site.

``url`` option
''''''''''''''

The ``url`` value is the location of the page to be checked for updates.  If
used, it must be a valid :abbr:`FTP (File Transfer Protocol)`/:abbr:`HTTP
(HyperText Transfer Protocol)`/:abbr:`HTTPS (HyperText Transfer Protocol)`
address.

.. _GitHub: https://github.com
.. _vim website: https://www.vim.org/
.. _issue: https://github.com/JNRowe/cupage/issues/
.. _gzip: https://www.gnu.org/software/gzip/
.. _bzip2: http://www.bzip.org/
.. _xz: http://tukaani.org/xz/
.. _tar: https://www.gnu.org/software/tar/
.. _zip: http://www.info-zip.org/
.. _CSS selectors: https://www.w3.org/TR/2001/CR-css3-selectors-20011113/
.. _XPath: https://www.w3.org/TR/xpath
.. _re: https://docs.python.org/3/library/re.html
