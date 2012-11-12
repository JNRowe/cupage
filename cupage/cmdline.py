#
# coding=utf-8
"""command_line- Command line interface for cupage"""
# Copyright (C) 2009-2012  James Rowe <jnrowe@gmail.com>
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

# This has to be here, as cupage uses 2.6 features.
import sys
if sys.version_info[:2] < (2, 6):
    print "Python v2.6, or later, is *required* for cupage!"
    sys.exit(1)


import atexit
import errno
import logging
import os

from operator import attrgetter

import argparse
import aaargh
import configobj

import cupage

from .i18n import _
from . import (_version, utils)


#: Command line help string, for use with :mod:`argparse`
# Pull the first paragraph from the docstring
USAGE = cupage.__doc__[:cupage.__doc__.find('\n\n', 100)].splitlines()[2:]
# Replace script name with optparse's substitution var, and rebuild string
USAGE = "\n".join(USAGE).replace("cupage", "%(prog)s")

APP = aaargh.App(description=USAGE,
                 epilog=_("Please report bugs to jnrowe@gmail.com"))


def frequency_typecheck(string):
    if utils.parse_timedelta(string):
        return string
    else:
        raise argparse.ArgumentTypeError('Invalid frequency value')


@APP.cmd(help='add definition to config file')
@APP.cmd_arg("-f", "--config", metavar="~/.cupage.conf",
             default=os.path.expanduser("~/.cupage.conf"),
             help=_("config file to read page definitions from"))
@APP.cmd_arg('-s', '--site', choices=cupage.SITES.keys(),
             help=_('site helper to use'))
@APP.cmd_arg('-u', '--url', metavar='url', help=_('site url to check'))
@APP.cmd_arg('-t', '--match-type', default='tar',
             choices=['gem', 're', 'tar', 'zip'],
             help=_('pre-defined regular expression to use'))
@APP.cmd_arg('-m', '--match', metavar='regex',
             help=_('regular expression to use with --match-type=re'))
@APP.cmd_arg('-q', '--frequency', metavar='frequency',
             type=frequency_typecheck, help='update check frequency')
@APP.cmd_arg('-x', '--select', metavar='selector', help=_('content selector'))
@APP.cmd_arg('--selector', default='css', choices=['css', 'xpath'],
             help=_('selector method to use'))
@APP.cmd_arg('name', help=_('site name'))
def add(verbose, config, site, url, match_type, match, frequency, select,
        selector, name):
    conf = configobj.ConfigObj(config)

    conf[name] = {
        'site': site,
        'url': url,
        'match_type': match_type,
        'match': match,
        'frequency': frequency,
        'select': select,
        'selector': selector,
    }
    # Flush unused values
    for key, value in conf[name].items():
        if not value:
            conf[name].pop(key)

    conf.write()


@APP.cmd(help='check sites for updates')
@APP.cmd_arg("-f", "--config", metavar="~/.cupage.conf",
             default=os.path.expanduser("~/.cupage.conf"),
             help=_("config file to read page definitions from"))
@APP.cmd_arg("-d", "--database", metavar="~/.cupage.db",
             help=_("database to store page data to(default based on --config "
                    "value)"))
@APP.cmd_arg("-c", "--cache", metavar="~/.cupage/",
             default=os.path.expanduser("~/.cupage/"),
             help=_("directory to store page cache"))
@APP.cmd_arg("--no-write", action="store_true",
             help=_("don't update cache or database"))
@APP.cmd_arg("--force", action="store_true", help=_("ignore frequency checks"))
@APP.cmd_arg("-t", "--timeout", type=int, metavar="30", default=30,
             help=_("timeout for network operations"))
@APP.cmd_arg('pages', nargs='*', help=_('pages to check'))
def check(verbose, config, database, cache, no_write, force, timeout, pages):
    if database is None:
        database = "%s%sdb" % (os.path.splitext(config)[0], os.path.extsep)

    sites = cupage.Sites()
    try:
        sites.load(config, database)
    except IOError as e:
        print utils.fail(e.message)
        return errno.EIO
    except ValueError:
        print utils.fail(_("Error reading database file"))
        return errno.ENOMSG
    except configobj.ConfigObjError:
        print utils.fail(_("Error reading config file"))
        return errno.ENOENT

    if not no_write:
        atexit.register(sites.save, database)

    if pages:
        site_names = map(attrgetter("name"), sites)
        for page in pages:
            if page not in site_names:
                print utils.fail(_('Invalid site argument %r') % page)
                return False
    for site in sorted(sites, key=attrgetter("name")):
        if not pages or site.name in pages:
            if verbose:
                print site
                print _("Checking %s...") % site.name
            matches = site.check(cache, timeout, force, no_write)
            if matches:
                if verbose:
                    print _("%s has new matches") % site.name
                for match in utils.sort_packages(matches):
                    print utils.success(match)
            else:
                if verbose:
                    print _("%s has no new matches") % site.name


@APP.cmd(name='list', help='list definitions from config file')
@APP.cmd_arg("-f", "--config", metavar="~/.cupage.conf",
             default=os.path.expanduser("~/.cupage.conf"),
             help=_("config file to read page definitions from"))
@APP.cmd_arg("-d", "--database", metavar="~/.cupage.db",
             help=_("database to store page data to(default based on --config "
                    "value)"))
@APP.cmd_arg('pages', nargs='*', help=_('pages to display'))
def list_conf(verbose, config, database, pages):
    if database is None:
        database = "%s%sdb" % (os.path.splitext(config)[0], os.path.extsep)

    sites = cupage.Sites()
    try:
        sites.load(config, database)
    except IOError as e:
        print utils.fail(e.message)
        return errno.EIO
    except configobj.ConfigObjError:
        print utils.fail(_("Error reading config file"))
        return errno.ENOENT

    if pages:
        site_names = map(attrgetter("name"), sites)
        for page in pages:
            if page not in site_names:
                print utils.fail(_("Invalid site argument %r") % page)
                return False
    for site in sorted(sites, key=attrgetter("name")):
        if not pages or site.name in pages:
            print site


@APP.cmd(name='list-sites', help='list supported site values')
def list_sites(verbose):
    if verbose:
        print _("Supported site values and their non-standard values:")
        print
    for site, values in sorted(cupage.SITES.items()):
        print "- %s (v%s)" % (site, values["added"])
        if "keys" in values:
            for item in values["keys"].items():
                print "  * %s - %s" % item


@APP.cmd(help='remove site from config')
@APP.cmd_arg("-f", "--config", metavar="~/.cupage.conf",
             default=os.path.expanduser("~/.cupage.conf"),
             help=_("config file to read page definitions from"))
@APP.cmd_arg('pages', nargs='*', help=_('pages to remove'))
def remove(verbose, config, pages):
    conf = configobj.ConfigObj(config)

    if pages:
        for page in pages:
            if page not in conf.sections:
                print utils.fail(_("Invalid site argument %r") % page)
                return False
    for page in pages:
        if verbose:
            print _("Removing %s...") % page
        conf.pop(page)
    conf.write()


def main():
    """Main script handler."""
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        datefmt="%Y-%m-%dT%H:%M:%S%z")

    APP.arg('--version', action='version',
            version="%%(prog)s %s" % _version.dotted)
    APP.arg("-v", "--verbose", action="store_true", dest="verbose",
            help=_("produce verbose output"))
    APP.arg("-q", "--quiet", action="store_false", dest="verbose",
            help=_("output only matches and errors"))

    try:
        APP.run()
    except IOError as error:
        print(utils.fail(error.message))
        return 2
