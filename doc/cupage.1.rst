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

|modref| checks web pages and displays changes from the last run that match
a given criteria.  Its original purpose was to check web pages for new software
releases, but it is easily configurable and can be used for other purposes.

OPTIONS
-------

--version
    Show the version and exit.

-v, --verbose
    Produce verbose output.

-q, --quiet
    Output only matches and errors.

--help
    Show this message and exit.

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
**https://www.vim.org**.

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

Full documentation: https://cupage.readthedocs.io/

Issue tracker: https://github.com/JNRowe/cupage/issues/

COPYING
-------

Copyright © 2009-2014  James Rowe.

cupage is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

cupage is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
cupage.  If not, see <http://www.gnu.org/licenses/>.
