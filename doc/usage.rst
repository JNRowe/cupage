Usage
=====

The :program:`cupage` is run from the command prompt, and displays updates on
``stdout``.

Options
-------

.. program:: cupage

.. option:: --version

   show program's version number and exit

.. option:: --help

   show this help message and exit

.. option:: -v, --verbose

   produce verbose output

.. option:: -q, --quiet

   output only matches and errors

Commands
--------

``add`` - add definition to config file
'''''''''''''''''''''''''''''''''''''''

.. program:: cupage add

.. option:: -f <file>, --config <file>

   configuration file to read

.. option:: -s <site>, --site <site>

   site helper to use

.. option:: -u <url>, --url <url>

   site url to check

.. option:: -t <type>, --match-type <type>

   pre-defined regular expression to use

.. option:: -m <regex>, --match <regex>

   regular expression to use with --match-type=re

.. option:: -q <frequency>, --frequency <frequency>

   update check frequency

.. option:: -x <selector>, --select <selector>

   content selector

.. option:: --selector <type>

   selector method to use

``check`` - check sites for updates
'''''''''''''''''''''''''''''''''''

.. program:: cupage check

.. option:: -f <file>, --config <file>

   configuration file to read

.. option:: -d <file>, --database <file>

   database to store page data to.  Default based on :option:`--config <-f>`
   value, for example ``--config my_conf`` will result in a default setting of
   ``--database my_conf.db``.

   See :ref:`database-label` for details of the database format.

.. option:: -c <dir>, --cache <dir>

   directory to store page cache

   This can, and in fact *should* be, shared between all cupage uses.

.. option:: --no-write

   don't update cache or database

.. option:: --force

   ignore frequency checks

.. option:: -t <n>, --timeout=<n>

   timeout for network operations

``list`` - list definitions from config file
''''''''''''''''''''''''''''''''''''''''''''

.. program:: cupage list

.. option:: -f <file>, --config <file>

   configuration file to read

.. option:: -m <regex>, --match <regex>

   match sites using regular expression

``list-sites`` - list supported site values
'''''''''''''''''''''''''''''''''''''''''''

.. program:: cupage list-sites

``remove`` - remove site from config
''''''''''''''''''''''''''''''''''''

.. program:: cupage remove

.. option:: -f <file>, --config <file>

   configuration file to read
