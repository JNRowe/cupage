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

import logging
import optparse
import os
import sys

import libcupage

# Pull the first paragraph from the docstring
USAGE = libcupage.__doc__[:libcupage.__doc__.find('\n\n', 100)].splitlines()[2:]
# Replace script name with optparse's substitution var, and rebuild string
USAGE = "\n".join(USAGE).replace("cupage", "%prog")

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
    parser.add_option("-t", "--timeout", type="int", metavar="30",
                         help="Timeout for network operations")
    parser.add_option("-v", "--verbose", action="store_true",
                      dest="verbose", help="Produce verbose output")
    parser.add_option("-q", "--quiet", action="store_false",
                      dest="verbose",
                      help="Output only matches and errors")

    options, args = parser.parse_args()

    return options, args

def main():
    """Main script handler"""
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        datefmt="%Y-%m-%dT%H:%M:%S%z")

    options, args = process_command_line()

    sites = libcupage.Sites()
    try:
        sites.load(options.config, options.database)
    except IOError:
        return 1
    for site in sites:
        if not args or site.name in args:
            if options.verbose:
                print "Checking %s..." % site.name
            site.check(options.timeout)
    if not options.no_write:
        sites.save(options.database)

if __name__ == '__main__':
    sys.exit(main())

