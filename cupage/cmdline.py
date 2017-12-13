#
# coding=utf-8
"""command_line - Command line interface for cupage"""
# Copyright © 2009-2014  James Rowe <jnrowe@gmail.com>
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
    print('Python v2.6, or later, is *required* for cupage!')
    sys.exit(1)


import atexit
import errno
import logging
import os
import re
import socket

from operator import attrgetter

import click
import configobj

import cupage

from .i18n import _
from . import (_version, utils)


#: Command line help string, for use with :mod:`argparse`
# Pull the first paragraph from the docstring
USAGE = cupage.__doc__[:cupage.__doc__.find('\n\n', 100)].splitlines()[2:]
# Replace script name with optparse's substitution var, and rebuild string
USAGE = '\n'.join(USAGE).replace('cupage', '%(prog)s')


class FrequencyParamType(click.ParamType):
    """Frequency parameter handler."""
    name = 'frequency'

    def convert(self, value, param, ctx):
        """Check given frequency is valid.

        :param str value: Value given to flag
        :param click.Argument param: Parameter being processed
        :param click.Context ctx: Current command context
        :rtype: :obj:`str`
        :return: String suitable for frequency checker
        """
        try:
            utils.parse_timedelta(value)
        except ValueError:
            self.fail(_('Invalid frequency value'))
        return value


def load_sites(config, database, pages):
    if database is None:
        database = '%s%sdb' % (os.path.splitext(config)[0], os.path.extsep)

    sites = cupage.Sites()
    try:
        sites.load(config, database)
    except IOError as e:
        print(utils.fail(e.message))
        return errno.EIO
    except ValueError:
        print(utils.fail(_('Error reading database file')))
        return errno.ENOMSG
    except TypeError:
        print(utils.fail(_('Error reading config file')))
        return errno.ENOENT

    # Check all named pages exist in config
    site_names = list(map(attrgetter('name'), sites))
    for page in pages:
        if page not in site_names:
            raise ValueError(_('Invalid site argument %r') % page)

    return sites


@click.group(help=_('A tool to check for updates on web pages'),
             epilog=_('Please report bugs to '
                      'https://github.com/JNRowe/cupage/issues'))
@click.version_option(_version.dotted)
@click.option('-v', '--verbose', flag_value=True,
              help=_('Produce verbose output.'))
@click.option('-q', '--quiet', 'verbose', flag_value=False,
              help=_('Output only matches and errors.'))
@click.pass_context
def cli(ctx, verbose):
    """Main command entry point.

    :param click.Context ctx: Current command context
    :param bool verbose: Whether to display verbose output
    """
    ctx.obj = {
        'verbose': verbose,
    }


@cli.command(help=_('Add definition to config file.'))
@click.option('-f', '--config', type=click.Path(exists=True, dir_okay=False),
              default=os.path.expanduser('~/.cupage.conf'),
              help=_('Config file to read page definitions from.'))
@click.option('-s', '--site', type=click.Choice(cupage.SITES.keys()),
              help=_('Site helper to use.'))
@click.option('-u', '--url', help=_('Site url to check.'))
@click.option('-t', '--match-type', default='tar',
              type=click.Choice(['re', 'tar', 'zip']),
              help=_('Pre-defined regular expression to use.'))
@click.option('-m', '--match', metavar='regex',
              help=_('Regular expression to use with --match-type=re.'))
@click.option('-q', '--frequency', type=FrequencyParamType(),
              help=_('Update check frequency.'))
@click.option('-x', '--select', help=_('Content selector.'))
@click.option('--selector', default='css', type=click.Choice(['css', 'xpath']),
              help=_('Selector method to use.'))
@click.argument('name')
def add(config, site, url, match_type, match, frequency, select,
        selector, name):
    """Add new site to config.

    :param str config: Location of config file
    :param str site: Site helper to match with
    :param str match_type: Filename match pattern
    :param str match: Regular expression to use when ``match_type`` is ``re``
    :param str frequency: Update frequency
    :param str select: Page content to check
    :param str site: Type of selector to use
    :param str name: Name for new entry
    """
    conf = configobj.ConfigObj(config)

    conf[name] = {}
    data = {
        'site': site,
        'url': url,
        'match_type': match_type,
        'match': match,
        'frequency': frequency,
        'select': select,
        'selector': selector,
    }
    # Don't store unused values
    for key, value in data.items():
        if value:
            conf[name][key] = value

    conf.write()


@cli.command(help=_('Check sites for updates.'))
@click.option('-f', '--config', type=click.Path(exists=True, dir_okay=False),
              default=os.path.expanduser('~/.cupage.conf'),
              help=_('Config file to read page definitions from.'))
@click.option('-d', '--database',
              type=click.Path(dir_okay=False, writable=True),
              help=_('Database to store page data to(default based on '
                     '--config value.)'))
@click.option('-c', '--cache', type=click.Path(file_okay=False, writable=True),
              default=os.path.expanduser('~/.cupage/'),
              help=_('Directory to store page cache.'))
@click.option('--write/--no-write', default=True,
              help=_("Whether to update cache and database."))
@click.option('--force/--no-force', help=_('Ignore frequency checks.'))
@click.option('-t', '--timeout', type=click.INT, metavar='30', default=30,
              help=_('Timeout for network operations.'))
@click.argument('pages', nargs=-1)
@click.pass_obj
def check(globs, config, database, cache, write, force, timeout, pages):
    """Check sites for updates.

    :param dict globs: Global options object
    :param str config: Location of config file
    :param str database: Location of database file
    :param str cache: Location of cache directory
    :param bool write: Whether to update cache/database
    :param bool force: Force update regardless of ``frequency`` setting
    :param datetime.timedelta frequency: Update frequency
    :param int timeout: Network timeout in seconds
    :type pages: ``list`` of ``str``
    :param pages: Pages to check
    """
    sites = load_sites(config, database, pages)
    if not isinstance(sites, cupage.Sites):
        raise IOError(_('Error processing config or database'))

    if write:
        if database is None:
            database = '%s%sdb' % (os.path.splitext(config)[0], os.path.extsep)
        atexit.register(sites.save, database)

    for site in sorted(sites, key=attrgetter('name')):
        if not pages or site.name in pages:
            if globs['verbose']:
                print(site)
                print(_('Checking %s...') % site.name)
            matches = site.check(cache, timeout, force, not write)
            if matches:
                if globs['verbose']:
                    print(_('%s has new matches') % site.name)
                for match in utils.sort_packages(matches):
                    print(utils.success(match))
            else:
                if globs['verbose']:
                    print(_('%s has no new matches') % site.name)


@cli.command(name='list',
             help=_('List definitions from config file.'))
@click.option('-f', '--config', type=click.Path(exists=True, dir_okay=False),
              default=os.path.expanduser('~/.cupage.conf'),
              help=_('Config file to read page definitions from.'))
@click.option('-d', '--database',
              type=click.Path(dir_okay=False, writable=True),
              help=_('Database to store page data to(default based on '
                     '--config value.)'))
@click.option('-m', '--match', type=re.compile,
              help=_('Match sites using regular expression.'))
@click.argument('pages', nargs=-1)
def list_conf(config, database, match, pages):
    """List site definitions in config file.

    :param str config: Location of config file
    :param str database: Location of database file
    :param str match: Display sites matching the given regular expression
    :type pages: ``list`` of ``str``
    :param pages: Pages to check
    """
    sites = load_sites(config, database, pages)
    for site in sorted(sites, key=attrgetter('name')):
        if not pages and not match:
            print(site)
        elif pages and site.name in pages:
            print(site)
        elif match and match.search(site.name):
            print(site)


@cli.command(name='list-sites', help='List supported site values.')
@click.pass_obj
def list_sites(globs):
    """List built-in site matcher definitions.

    :param dict globs: Global options object
    """
    if globs['verbose']:
        print(_('Supported site values and their non-standard values:'))
        print()
    for site, values in sorted(cupage.SITES.items()):
        print('- %s (v%s)' % (site, values['added']))
        if 'keys' in values:
            for item in values['keys'].items():
                print('  * %s - %s' % item)


@cli.command(help=_('Remove site from config.'))
@click.option('-f', '--config', type=click.Path(exists=True, dir_okay=False),
              default=os.path.expanduser('~/.cupage.conf'),
              help=_('Config file to read page definitions from.'))
@click.argument('pages', nargs=-1)
@click.pass_obj
def remove(globs, config, pages):
    """Remove sites for config file.

    :param dict globs: Global options object
    :param str config: Location of config file
    :type pages: ``list`` of ``str``
    :param pages: Pages to check
    """
    conf = configobj.ConfigObj(config, file_error=True)

    if pages:
        for page in pages:
            if page in conf.sections:
                print(utils.fail(_('Invalid site argument %r') % page))
                return False
    for page in pages:
        if globs['verbose']:
            print(_('Removing %s...') % page)
        del conf[page]
    conf.write()


def main():
    """Main script handler."""
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        datefmt='%Y-%m-%dT%H:%M:%S%z')

    try:
        cli()
    except socket.error as error:
        print(utils.fail(error.strerror or error.message))
        return errno.EADDRNOTAVAIL
    except (configobj.DuplicateError, IOError) as error:
        print(utils.fail(error.message))
        return errno.ENOENT
    except ValueError as error:
        print(utils.fail(error.message))
        return errno.EPERM
