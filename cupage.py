#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""cupage - a tool to check for updates on web pages"""
# Copyright (C) 2009 James Rowe;
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import division

__version__ = "0.1.0"
__date__ = "2009-09-18"
__author__ = "James Rowe <jnrowe@gmail.com>"
__copyright__ = "Copyright (C) 2009 James Rowe"
__license__ = "GNU General Public License Version 3"
__credits__ = ""
__history__ = "See Git repository"

from email.utils import parseaddr
__doc__ += """

cupage checks for updates on one or more web pages specified in a simple config
file.

A simple config example is::

.. code-block:: ini

    # dev-python
    [pep8]
    site = pypi
    match_type = tar
    [pyisbn]
    url = http://www.jnrowe.ukfsn.org/_downloads/
    select = pre > a
    match_type = tar

In the first example we only need to specify the type of archive as the page
location and search patterns are set up based on the value of ``site``.  In the
second example we specify a page location and also a CSS based selector to
check.

@version: %s
@author: U{%s <mailto:%s>}
@copyright: %s
@status: WIP
@license: %s
""" % ((__version__, ) + parseaddr(__author__) + (__copyright__, __license__))

import ConfigParser
import cPickle
import logging
import optparse
import os
import sys

# Pull the first paragraph from the docstring
USAGE = __doc__[:__doc__.find('\n\n', 100)].splitlines()[2:]
# Replace script name with optparse's substitution var, and rebuild string
USAGE = "\n".join(USAGE).replace("cupage", "%prog")


class Sites(dict):
    def load(self, config_file, database):
        """Read sites from a user's config file"""
        conf = ConfigParser.ConfigParser()
        conf.read(config_file)
        if not conf.sections():
            logging.debug("Config file `%s' is empty" % config_file)
            return {}

        if os.path.exists(database):
            data = cPickle.load(open(database))
        else:
            logging.debug("Database file `%s' doesn't exist" % database)
            data = {}

        for name in conf.sections():
            options = {}
            for opt in conf.options(name):
                options[opt] = conf.get(name, opt)
            self[name] = Site.parse(name, options, data.get(name))

    def save(self, database):
        data = {}
        for k, v in self.iteritems():
            data[k] =  v.state()
        cPickle.dump(data, open(database, "w"), -1)


def process_command_line():
    """Main command line interface"""
    parser = optparse.OptionParser(usage="%prog [options...] <site>...",
                                   version="%prog v" + __version__,
                                   description=USAGE)

    parser.set_defaults(config=os.path.expanduser("~/.cupage.conf"),
                        database=os.path.expanduser("~/.cupage.db"))

    parser.add_option("-f", "--config", action="store",
                      metavar=os.path.expanduser("~/.cupage.conf"),
                      help="Config file to read page definitions from")
    parser.add_option("-d", "--database", action="store",
                      metavar=os.path.expanduser("~/.cupage.db"),
                      help="Database to store page data to")
    parser.add_option("--no-write", action="store_true",
                      help="Don't update database")

    parser.add_option("-v", "--verbose", action="store_true",
                      dest="verbose", help="produce verbose output")
    parser.add_option("-q", "--quiet", action="store_false",
                      dest="verbose",
                      help="output only matches and errors")

    options, args = parser.parse_args()

    return options, args

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        datefmt="%Y-%m-%dT%H:%M:%S%z")

    options, args = process_command_line()

    sites = Sites()
    sites.load(options.config, options.database)
    for site in sites.values():
        if options.verbose:
            print "Checking %s..." % site.name
        site.check()
    if not options.no_write:
        sites.save(options.database)

if __name__ == '__main__':
    sys.exit(main())

