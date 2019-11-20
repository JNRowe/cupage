#
"""command_line - Command line interface for cupage."""
# Copyright © 2009-2014  James Rowe <jnrowe@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
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

import atexit
import errno
import logging
import os
import re
import socket

from operator import attrgetter

import click
import configobj

from jnrbase.attrdict import ROAttrDict
from jnrbase.human_time import parse_timedelta
from jnrbase import colourise

import cupage

from . import (_version, utils)


class FrequencyParamType(click.ParamType):
    """Frequency parameter handler."""

    name = 'frequency'

    def convert(self, value, param, ctx):
        """Check given frequency is valid.

        Args:
            value (str): Value given to flag
            param (click.Argument): Parameter being processed
            ctx (click.Context): Current command context

        Returns:
            str: String suitable for frequency checker
        """
        try:
            parse_timedelta(value)
        except ValueError:
            self.fail('Invalid frequency value')
        return value


def load_sites(config, database, pages):
    """Load site data.

    Args:
        config (str): Location of config file
        database (str): Location of database file
        pages (list of str): Pages to check

    Returns:
        Sites: Imported site data
    """
    if database is None:
        database = '{}{}db'.format(os.path.splitext(config)[0], os.path.extsep)

    sites = cupage.Sites()
    try:
        sites.load(config, database)
    except IOError as e:
        colourise.pfail(e.message)
        return errno.EIO
    except ValueError:
        colourise.pfail('Error reading database file')
        return errno.ENOMSG
    except TypeError:
        colourise.pfail('Error reading config file')
        return errno.ENOENT

    # Check all named pages exist in config
    site_names = list(map(attrgetter('name'), sites))
    for page in pages:
        if page not in site_names:
            raise ValueError(f'Invalid site argument {page!r}')

    return sites


@click.group(epilog='Please report bugs to '
             'https://github.com/JNRowe/cupage/issues')
@click.version_option(_version.dotted)
@click.option('-v',
              '--verbose',
              flag_value=True,
              help='Produce verbose output.')
@click.option('-q',
              '--quiet',
              'verbose',
              flag_value=False,
              help='Output only matches and errors.')
@click.pass_context
def cli(ctx, verbose):
    """A tool to check for updates on web pages.

    \f

    Args:
        ctx (click.Context): Current command context
        verbose (bool): Whether to display verbose output
    """
    ctx.obj = ROAttrDict(verbose=verbose)


@cli.command()
@click.option('-f',
              '--config',
              type=click.Path(exists=True, dir_okay=False),
              default=os.path.expanduser('~/.cupage.conf'),
              help='Config file to read page definitions from.')
@click.option('-s',
              '--site',
              type=click.Choice(cupage.SITES.keys()),
              help='Site helper to use.')
@click.option('-u', '--url', help='Site url to check.')
@click.option('-t',
              '--match-type',
              default='tar',
              type=click.Choice(['re', 'tar', 'zip']),
              help='Pre-defined regular expression to use.')
@click.option('-m',
              '--match',
              metavar='regex',
              help='Regular expression to use with --match-type=re.')
@click.option('-q',
              '--frequency',
              type=FrequencyParamType(),
              help='Update check frequency.')
@click.option('-x', '--select', help='Content selector.')
@click.option('--selector',
              default='css',
              type=click.Choice(['css', 'xpath']),
              help='Selector method to use.')
@click.argument('name')
def add(config, site, url, match_type, match, frequency, select, selector,
        name):
    """Add new site definition to config file.

    \f

    Args:
        config (str): Location of config file
        site (str): Site helper to match with
        match_type (str): Filename match pattern
        match (str): Regular expression to use when ``match_type`` is ``re``
        frequency (str): Update frequency
        select (str): Page content to check
        site (str): Type of selector to use
        name (str): Name for new entry
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
    # Don’t store unused values
    for key, value in data.items():
        if value:
            conf[name][key] = value

    conf.write()


@cli.command(hidden=True)
def bug_data():
    """Produce data for cupage bug reports."""
    import sys
    from importlib import import_module

    click.echo(f'* OS: {sys.platform}')
    click.echo(f'* `cupage` version: {_version.dotted}')
    click.echo('* `python` version: {}'.format(sys.version.replace('\n', '|')))
    click.echo()

    for m in ['click', 'configobj', 'cssselect', 'httplib2', 'jnrbase',
              'lxml']:
        if m not in sys.modules:  # pragma: no cover
            try:
                import_module(m)
            except ModuleNotFoundError:
                continue
        ver = getattr(sys.modules[m], '__version__', '*Unknown version*')
        link = utils.term_link(f'https://pypi.org/project/{m}/', f'`{m}`')
        click.echo(f'* {link}: {ver}')


@cli.command()
@click.option('-f',
              '--config',
              type=click.Path(exists=True, dir_okay=False),
              default=os.path.expanduser('~/.cupage.conf'),
              help='Config file to read page definitions from.')
@click.option('-d',
              '--database',
              type=click.Path(dir_okay=False, writable=True),
              help='Database to store page data to(default based on '
              '--config value.)')
@click.option('-c',
              '--cache',
              type=click.Path(file_okay=False, writable=True),
              default=os.path.expanduser('~/.cupage/'),
              help='Directory to store page cache.')
@click.option('--write/--no-write',
              default=True,
              help="Whether to update cache and database.")
@click.option('--force/--no-force', help='Ignore frequency checks.')
@click.option('-t',
              '--timeout',
              type=click.INT,
              metavar='30',
              default=30,
              help='Timeout for network operations.')
@click.argument('pages', nargs=-1)
@click.pass_obj
def check(globs, config, database, cache, write, force, timeout, pages):
    """Check sites for updates.

    \f

    Args:
        globs (AttrDict): Global options object
        config (str): Location of config file
        database (str): Location of database file
        cache (str): Location of cache directory
        write (bool): Whether to update cache/database
        force (bool): Force update regardless of ``frequency`` setting
        frequency (datetime.timedelta): Update frequency
        timeout (int): Network timeout in seconds
        pages (list of str): Pages to check
    """
    sites = load_sites(config, database, pages)
    if not isinstance(sites, cupage.Sites):
        raise IOError('Error processing config or database')

    if write:
        if database is None:
            database = '{}{}db'.format(
                os.path.splitext(config)[0], os.path.extsep)
        atexit.register(sites.save, database)

    for site in sorted(sites, key=attrgetter('name')):
        if not pages or site.name in pages:
            if globs.verbose:
                click.echo(site)
                click.echo(f'Checking {site.name}…')
            matches = site.check(cache, timeout, force, not write)
            if matches:
                if globs.verbose:
                    click.echo(f'{site.name} has new matches')
                for match in utils.sort_packages(matches):
                    colourise.psuccess(match)
            else:
                if globs.verbose:
                    click.echo(f'{site.name} has no new matches')


@cli.command(name='list')
@click.option('-f',
              '--config',
              type=click.Path(exists=True, dir_okay=False),
              default=os.path.expanduser('~/.cupage.conf'),
              help='Config file to read page definitions from.')
@click.option('-d',
              '--database',
              type=click.Path(dir_okay=False, writable=True),
              help='Database to store page data to(default based on '
              '--config value.)')
@click.option('-m',
              '--match',
              type=re.compile,
              help='Match sites using regular expression.')
@click.argument('pages', nargs=-1)
def list_conf(config, database, match, pages):
    """List site definitions in config file.

    \f

    Args:
        config (str): Location of config file
        database (str): Location of database file
        match (str): Display sites matching the given regular expression
        pages (list of str): Pages to check
    """
    sites = load_sites(config, database, pages)
    for site in sorted(sites, key=attrgetter('name')):
        if not pages and not match:
            click.echo(site)
        elif pages and site.name in pages:
            click.echo(site)
        elif match and match.search(site.name):
            click.echo(site)


@cli.command(name='list-sites')
@click.pass_obj
def list_sites(globs):
    """List built-in site matcher definitions.

    \f

    Args:
        globs (AttrDict): Global options object
    """
    if globs.verbose:
        click.echo('Supported site values and their non-standard values:')
        click.echo()
    for site, values in sorted(cupage.SITES.items()):
        click.echo(f'- {site} (v{values["added"]})')
        if 'keys' in values:
            for item in values['keys'].items():
                click.echo(f'  * {item[0]} - {item[1]}')


@cli.command()
@click.option('-f',
              '--config',
              type=click.Path(exists=True, dir_okay=False),
              default=os.path.expanduser('~/.cupage.conf'),
              help='Config file to read page definitions from.')
@click.argument('pages', nargs=-1)
@click.pass_obj
def remove(globs, config, pages):
    """Remove sites for config file.

    \f

    Args:
        globs (AttrDict): Global options object
        config (str): Location of config file
        pages (list of str): Pages to check
    """
    conf = configobj.ConfigObj(config, file_error=True)

    if pages:
        for page in pages:
            if page in conf.sections:
                colourise.pfail(f'Invalid site argument {page!r}')
                return False
    for page in pages:
        if globs.verbose:
            click.echo(f'Removing {page}…')
        del conf[page]
    conf.write()


def main():
    """Main script handler."""
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        datefmt='%Y-%m-%dT%H:%M:%S%z')

    try:
        cli()
    except socket.error as error:
        colourise.pfail(error.strerror or str(error))
        return errno.EADDRNOTAVAIL
    except (configobj.DuplicateError, IOError) as error:
        colourise.pfail(str(error))
        return errno.ENOENT
    except ValueError as error:
        colourise.pfail(str(error))
        return errno.EPERM
