#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""cupage - a tool to check for updates on web pages"""
# Copyright (C) 2009-2010 James Rowe;
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

# This has to be here, as libcupage uses 2.6 features.
import sys
if sys.version_info[:2] < (2, 6):
    print "Python v2.6, or later, is *required* for cupage!"
    sys.exit(1)

import libcupage

__version__ = libcupage.__version__
__date__ = libcupage.__date__
__author__ = libcupage.__author__
__copyright__ = libcupage.__copyright__
__license__ = libcupage.__license__
__credits__ = libcupage.__credits__
__history__ = libcupage.__history__

import atexit
import ConfigParser
import logging
import optparse
import os

from operator import attrgetter

# Pull the first paragraph from the docstring
USAGE = libcupage.__doc__[:libcupage.__doc__.find('\n\n', 100)].splitlines()[2:]
# Replace script name with optparse's substitution var, and rebuild string
USAGE = "\n".join(USAGE).replace("cupage", "%prog")

# pylint: disable-msg=C0103
success = libcupage.termstyle.green
fail = libcupage.termstyle.red
warn = libcupage.termstyle.yellow

def process_command_line():
    """Main command line interface"""
    parser = optparse.OptionParser(usage="%prog [options...] <site>...",
                                   version="%prog v" + __version__,
                                   description=USAGE)

    parser.set_defaults(config=os.path.expanduser("~/.cupage.conf"),
                        database=None, cache=os.path.expanduser("~/.cupage/"),
                        timeout=30)

    parser.add_option("-f", "--config", action="store",
                      metavar="~/.cupage.conf",
                      help="Config file to read page definitions from")
    parser.add_option("-d", "--database", action="store",
                      metavar="~/.cupage.db",
                      help="Database to store page data to(default based on "
                           "--config value)")
    parser.add_option("-c", "--cache", action="store", metavar="~/.cupage/",
                      help="Directory to store page cache")
    parser.add_option("--no-write", action="store_true",
                      help="Don't update cache or database")
    parser.add_option("--force", action="store_true",
                      help="Ignore frequency checks")
    parser.add_option("-t", "--timeout", type="int", metavar="30",
                      help="Timeout for network operations")
    parser.add_option("--list-sites", action="store_true",
                      help="List site matchers and required values")
    parser.add_option("-v", "--verbose", action="store_true",
                      dest="verbose", help="Produce verbose output")
    parser.add_option("-q", "--quiet", action="store_false",
                      dest="verbose",
                      help="Output only matches and errors")

    options, args = parser.parse_args()

    if options.database is None:
        options.database = "%s%sdb" % (os.path.splitext(options.config)[0],
                                       os.path.extsep)

    return options, args


def main():
    """Main script handler"""
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        datefmt="%Y-%m-%dT%H:%M:%S%z")

    options, args = process_command_line()

    if options.list_sites:
        if options.verbose:
            print "Supported site values and their non-standard values:"
            print
        for site, values in sorted(libcupage.SITES.items()):
            print "- %s (v%s)" % (site, values["added"])
            if "keys" in values:
                for item in values["keys"].items():
                    print "  * %s - %s" % item
        return 0

    sites = libcupage.Sites()
    try:
        sites.load(options.config, options.database)
    except IOError:
        print fail("Missing config file")
        return 66
    except ConfigParser.MissingSectionHeaderError:
        print fail("Error reading config file")
        return 65

    if not options.no_write:
        atexit.register(sites.save, options.database)

    if args:
        site_names = map(attrgetter("name"), sites)
        for arg in args:
            if arg not in site_names:
                print fail("Invalid site argument `%s'" % arg)
    for site in sorted(sites, key=attrgetter("name")):
        if not args or site.name in args:
            if options.verbose:
                print site
                print "Checking %s..." % site.name
            matches = site.check(options.cache, options.timeout, options.force,
                                 options.no_write)
            if matches:
                if options.verbose:
                    print "%s has new matches" % site.name
                for match in matches:
                    print success("   " + match)
            else:
                if options.verbose:
                    print "%s has no new matches" % site.name

if __name__ == '__main__':
    sys.exit(main())
