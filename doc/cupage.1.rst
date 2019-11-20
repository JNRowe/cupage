cupage.py
=========

Check for updates on web pages
------------------------------

:Author: James Rowe <jnrowe@gmail.com>
:Date: 2010-01-23
:Copyright: GPL v3
:Manual section: 1
:Manual group: Networking

SYNOPSIS
--------

    cupage.py [option]... <command>

DESCRIPTION
-----------

:mod:`cupage` checks web pages and displays changes from the last run that match
a given criteria.  Its original purpose was to check web pages for new software
releases, but it is easily configurable and can be used for other purposes.

OPTIONS
-------

--version
    show program’s version number and exit

--help
    show this help message and exit

-v, --verbose
    produce verbose output

-q, --quiet
    output only matches and errors

COMMANDS
--------

.. click:: cupage.cmdline:add
   :prog: cupage add

.. click:: cupage.cmdline:check
   :prog: cupage check

.. click:: cupage.cmdline:list_conf
   :prog: cupage list

.. click:: cupage.cmdline:list_sites
   :prog: cupage list-sites

.. click:: cupage.cmdline:remove
   :prog: cupage remove

CONFIGURATION FILE
------------------

The configuration file, by default **~/.cupage.conf**, is a simple **INI**
format file, with sections defining sites to check.  For example:

.. code-block:: ini

    [spill]
    url = http://www.rpcurnow.force9.co.uk/spill/index.html
    select = p a
    [rails]
    site = vim-script
    script = 1567

With the above configuration file the site named **spill** will be checked at
**http://www.rpcurnow.force9.co.uk/spill/index.html**, and elements matching the
CSS selector **p a** will be scanned for tarballs.  The site named **rails**
will be checked using the **vim-script** site matcher, which requires only
a **script** value to check for updates in the scripts section of
**http://www.vim.org**.

Various site matchers are available, see the output of ``cupage.py
--list-sites``.

BUGS
----

None known.

AUTHOR
------

Written by `James Rowe <mailto:jnrowe@gmail.com>`__

RESOURCES
---------

Home page: http://github.com/JNRowe/cupage

COPYING
-------

Copyright © 2009-2014  James Rowe.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.
