Usage
-----

The :program:`cupage` is run from the command prompt, and displays updates on
``stdout``.

Options
'''''''

.. program:: cupage

.. cmdoption:: --version
   show program's version number and exit

.. cmdoption:: -h, --help
   show this help message and exit

.. cmdoption:: -f <file>, --config <file>
   configuration file to read

.. cmdoption:: -d <file>, --database <file>
   database to store page data to.  Default based on :option:`--config <-f>`
   value, for example ``--config my_conf`` will result in a default setting of
   ``--database my_conf.db``.

   See :ref:`database-label` for details of the database format.

.. cmdoption:: -c <dir>, --cache <dir>
   Directory to store page cache

   This can, and in fact *should* be, shared between all cupage uses.

.. cmdoption:: --no-write
   don't update cache or database

.. cmdoption:: --force
   ignore frequency checks

.. cmdoption:: -t <n>, --timeout=<n>
   timeout for network operations

.. cmdoption:: --list-sites
   display site matchers and their required values

   See :ref:`site-label`.

.. cmdoption:: -v, --verbose
   produce verbose output

.. cmdoption:: -q, --quiet
   output only results and errors

