#
"""cupage - a tool to check for updates on web pages.

cupage checks web pages and displays changes from the last run that match
a given criteria.  Its original purpose was to check web pages for new software
releases, but it is easily configurable and can be used for other purposes.

Thanks to the excellent lxml package you can use complex XPath and CSS
selectors to match elements within a page, if you wish.
"""
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

from . import _version

__version__ = _version.dotted
__date__ = _version.date
__copyright__ = 'Copyright (C) 2009-2014  James Rowe'

import datetime
import json
import logging
import os
import re
import socket
import ssl
import tempfile
import http.client as httplib

import configobj
import httplib2

from jnrbase.human_time import parse_timedelta
from jnrbase import colourise, json_datetime
from lxml import html

from . import utils

#: User agent to use for HTTP requests
USER_AGENT = f'cupage/{__version__} (https://github.com/JNRowe/cupage/)'

#: Site specific configuration data
SITES = {
    'bitbucket': {
        'url': 'https://bitbucket.org/{user}/{name}/downloads',
        'select': 'td.name a.execute',
        'added': '0.7.0',
        'keys': {
            'user': 'bitbucket user name',
        },
    },
    'cpan': {
        'url': 'http://search.cpan.org/dist/{name}/',
        'select': 'td small a',
        'match_type': 're',
        'match': r'{name}-[\d\.]+.tar.gz',
        'added': '0.4.0',
    },
    'debian': {
        'url': 'http://ftp.debian.org/debian/pool/main/{name[0]}/{name}/',
        'select': 'td a',
        'match_type': 're',
        're_verbose': True,
        'match': r"""{name}_[\d\.]+
                     (?:\.orig\.tar|-\d+\.(?:diff|debian.tar))
                     \.(?:bz2|gz|xz)""",
        'added': '0.3.0',
    },
    'failpad': {
        'url': 'https://launchpad.net/{name}/+download',
        'select': 'table.listing td a',
        'added': '0.5.0',
    },
    'github': {
        'url': 'https://api.github.com/repos/{user}/{name}/tags',
        'match_func': 'github',
        'keys': {
            'user': 'GitHub user name',
        },
        'added': '0.3.1',
        'robots': 'false',
    },
    'google code': {
        'url':
        'https://www.googleapis.com/storage/v1/b/google-code-archive/o'
        '/v2%2Fcode.google.com%2F{name}%2Fdownloads-page-1.json'
        '?alt=media',
        'match_func':
        'google_code',
        'select':
        'td.id a',
        'added':
        '0.1.0',
        'deprecated':
        'Uploads no longer supported, find another source',
    },
    'hackage': {
        'url': 'http://hackage.haskell.org/package/{name}',
        'match_func': 'hackage',
        'added': '0.1.0',
    },
    'luaforge': {
        'url': 'http://files.luaforge.net/releases/{name}/{name}',
        'select': 'td a',
        'added': '0.7.0',
    },
    'pypi': {
        'url': 'https://pypi.python.org/simple/{name}/',
        'select': 'a',
        'added': '0.1.0',
        'match': r'({name}-[0-9\.]+\.tar\.gz)(?:#.*)',
        'transform': str.lower,
    },
    'savannah': {
        'url': 'http://download.savannah.gnu.org/releases/{name}/',
        'select': 'td a',
        'added': '0.7.0',
    },
    'sourceforge': {
        'url':
        'https://sourceforge.net/api/file/index/project-name/{name}/rss',
        'match_func': 'sourceforge',
        'added': '0.7.1',
    },
    'vim-script': {
        'url': 'http://www.vim.org/scripts/script.php?script_id={script}',
        'select': 'td a',
        'match_type': 're',
        'match': r'download_script.php\?src_id=([\d]+)',
        'keys': {
            'script': 'script id on the vim website',
        },
        'added': '0.3.0',
    },
}


class Site:
    """Simple object for representing a web site."""
    def __init__(self,
                 name,
                 url,
                 match_func='default',
                 options=None,
                 frequency=None,
                 robots=True,
                 checked=None,
                 matches=None):
        """Initialise a new ``Site`` object.

        Args:
            name (str): Site name
            url (str): URL for site
            match_func (str): Function to use for retrieving matches
            options (dict): Options for :attr:`match_func`
            frequency (int): Site check frequency
            robots (bool): Whether to respect a host’s :file:`robots.txt`
            checked (datetime.datetime): Last checked date
            matches (list): Previous matches
        """
        self.name = name
        self.url = url
        self.match_func = match_func
        self.options = options if options else {}
        re_verbose = 're_verbose' in options
        if options.get('match_type') == 're':
            self.match = re.compile(options['match'],
                                    flags=re.VERBOSE if re_verbose else 0)
        elif options.get('match_type') in ('tar', 'zip'):
            self.match = self.package_re(self.name, options['match_type'],
                                         re_verbose)
        self.checked = checked
        self.frequency = frequency
        self.robots = robots
        self.matches = matches if matches else []

    def __repr__(self):
        """String representation for use in REPL."""
        return f'{self.__class__.__name__!r}({self.name!r}, {self.url!r}, ...)'

    def __str__(self):
        """Pretty printed ``Site`` string."""
        ret = [
            f'{self.name} @ {self.url} using {self.match_func} matcher',
        ]
        if self.checked:
            ret.append(f' last checked {self.checked}')
        if self.frequency:
            ret.append(f' with a check frequency of {self.frequency}')
        if self.matches:
            ret.append('\n    ')
            ret.append(', '.join(utils.sort_packages(self.matches)))
        else:
            ret.append('\n    No matches')
        return ''.join(ret)

    def check(self, cache=None, timeout=None, force=False, no_write=False):
        """Check site for updates.

        Args:
            cache (str): :class:`httplib2.Http` cache location
            timeout (int): Timeout value for :class:`httplib2.Http`
            force (bool): Ignore configured check frequency
            no_write (bool): Do not write to cache, useful for testing
        """
        if not force and self.frequency and self.checked:
            next_check = self.checked + self.frequency
            if datetime.datetime.utcnow() < next_check:
                colourise.pwarn(
                    f'{self.name} is not due for check until {next_check}')
                return
        http = httplib2.Http(cache=cache,
                             timeout=timeout,
                             ca_certs=utils.CA_CERTS)
        # hillbilly monkeypatch to allow us to still read the cache, but make
        # writing a NOP
        if no_write:
            http.cache.set = lambda *_: True

        if cache and not os.path.exists(f'{cache}/CACHEDIR.TAG'):
            with open(f'{cache}/CACHEDIR.TAG', 'w') as f:
                f.writelines([
                    'Signature: 8a477f597d28d172789f06886806bc55\n',
                    '# This file is a cache directory tag created by cupage.\n',
                    '# For information about cache directory tags, see:\n',
                    '#   http://www.brynosaurus.com/cachedir/\n',
                ])

        if self.robots and not os.getenv('CUPAGE_IGNORE_ROBOTS_TXT'):
            if not utils.robots_test(http, self.url, self.name, USER_AGENT):
                return False

        try:
            headers, content = http.request(self.url,
                                            headers={'User-Agent': USER_AGENT})
        except httplib2.ServerNotFoundError:
            colourise.pfail(f'Domain name lookup failed for {self.name}')
            return False
        except ssl.SSLError as error:
            colourise.pfail(f'SSL error {self.name} ({error})')
            return False
        except socket.timeout:
            colourise.pfail(f'Socket timed out on {self.name}')
            return False

        charset = utils.charset_from_headers(headers)

        if not headers.get('content-location', self.url) == self.url:
            colourise.pwarn(
                f'{self.name} moved to {headers["content-location"]}')
        if headers.status == httplib.NOT_MODIFIED:
            return
        elif headers.status in (httplib.FORBIDDEN, httplib.NOT_FOUND):
            colourise.pfail(
                '{self}.name returned {httplib.responses[headers.status]!r}')
            return False

        matches = getattr(self, f'find_{self.match_func}_matches')(content,
                                                                   charset)
        new_matches = [s for s in matches if not s in self.matches]
        self.matches = matches
        self.checked = datetime.datetime.utcnow()
        return new_matches

    def find_default_matches(self, content, charset):
        """Extract matches from content.

        Args:
            content (str): Content to search
            charset (str): Character set for content
        """
        doc = html.fromstring(content)
        if self.options['selector'] == 'css':
            selected = doc.cssselect(self.options['select'])
        elif self.options['selector'] == 'xpath':
            selected = doc.xpath(self.options['select'])
        # We use a set to remove duplicates the lazy way
        matches = set()
        for sel in selected:
            match = re.search(self.match, sel.get('href', ''))
            if match:
                groups = match.groups()
                matches.add(groups[0] if groups else match.group())
        return sorted(list(matches))

    def find_google_code_matches(self, content, charset):
        """Extract matches from Google Code content.

        Args:
            content (str): Content to search
            charset (str): Character set for content
        """
        content = content.encode(charset)
        doc = json.loads(content)
        return sorted(tag['filename'] for tag in doc['downloads'])

    def find_github_matches(self, content, charset):
        """Extract matches from GitHub content.

        Args:
            content (str): Content to search
            charset (str): Character set for content
        """
        content = content.encode(charset)
        doc = json.loads(content)
        return sorted(tag['name'] for tag in doc)

    def find_hackage_matches(self, content, charset):
        """Extract matches from hackage content.

        Args:
            content (str): Content to search
            charset (str): Character set for content
        """
        doc = html.fromstring(content)
        data = doc.cssselect('table tr')[0][1]
        return sorted(x.text for x in data.getchildren())

    def find_sourceforge_matches(self, content, charset):
        """Extract matches from sourceforge content.

        Args:
            content (str): Content to search
            charset (str): Character set for content
        """
        # We use lxml.html here to sidestep part of the stupidity of RSS 2.0,
        # if a usable format on sf comes along we’ll switch to it.
        doc = html.fromstring(content)
        matches = set()
        for x in doc.cssselect('item link'):
            if '/download' in x.tail:
                matches.add(x.tail.split('/')[-2])
        return sorted(list(matches))

    @staticmethod
    def package_re(name, ext, verbose=False):
        """Generate a compiled ``re`` for the package.

        Args:
            name (str): File name to check for
            ext (str): File extension to check
            verbose (bool): Whether to enable :data:`re.VERBOSE`
        """
        if ext == 'tar':
            ext = 'tar.(?:bz2|gz|xz)'
        match = rf'{name}-[\d\.]+(?:[_-](?:pre|rc)[\d]+)?\.{ext}'
        return re.compile(match, flags=re.VERBOSE if verbose else 0)

    @staticmethod
    def parse(name, options, data):
        """Parse data generated by ``Sites.loader``.

        Args:
            name (str): Site name from config file
            options (configobj.ConfigObj): Site options from config file
            data (dict): Stored data from database file
        """
        if 'site' in options:
            try:
                site_opts = SITES[options['site']]
            except KeyError:
                raise ValueError(f'Invalid site option for {name}')
            if 'deprecated' in site_opts:
                print(f'{name}: {options["site"]} - {site_opts["deprecated"]}')
            if 'keys' in site_opts:
                for key in site_opts['keys']:
                    if not key in options:
                        raise ValueError(
                            f'{key!r} is required for site={options["site"]} '
                            f'from {name}')
            if 'transform' in site_opts:
                name = site_opts['transform'](name)
            options['name'] = name  # For .format usage

            def get_val(name, default=None):
                """Get option from site defaults with local override."""
                return options.get(name, site_opts.get(name, default))

            match_func = get_val('match_func', 'default')
            url = get_val('url').format(**options)  # pylint: disable-msg=W0142
            match_options = {
                'selector': get_val('selector', 'css'),
                'select': get_val('select'),
                'match_type': get_val('match_type', 'tar'),
                're_verbose': get_val('re_verbose', False),
                'match': get_val('match', '').format(**options),
            }  # pylint: disable-msg=W0142,C0301
            if 'robots' in options:
                robots = options.as_bool('robots')
            else:
                robots = True
        elif 'url' in options:
            match_func = options.get('match_func', 'default')
            url = options['url']
            match_options = {
                'selector': options.get('selector', 'css'),
                'select': options.get('select'),
                'match_type': options.get('match_type', 'tar'),
                'match': options.get('match'),
            }
            if not match_options['select']:
                raise ValueError(f'missing select option for {name}')
            if match_options['match_type'] == 're' \
                    and not match_options['match']:
                raise ValueError(f'missing match option for {name}')
            if 'robots' in options:
                robots = options.as_bool('robots')
            else:
                robots = True
        else:
            raise ValueError(f'site or url not specified for {name}')
        frequency = options.get('frequency')
        if frequency:
            frequency = parse_timedelta(frequency)
        site = Site(name, url, match_func, match_options, frequency, robots,
                    data.get('checked'), data.get('matches'))
        return site

    @property
    def state(self):
        """Return ``Site`` state for database storage."""
        return {'matches': self.matches, 'checked': self.checked}


class Sites(list):
    """``Site`` bundle wrapper."""
    def load(self, config_file, database=None):
        """Read sites from a user’s config file and database.

        Args:
            config_file (str): Config file to read
            database (str): Database file to read
        """
        conf = configobj.ConfigObj(config_file, file_error=True)
        if not conf.sections:
            logging.debug('Config file %r is empty', config_file)
            raise IOError('Error reading config file')

        data = {}
        if database and os.path.exists(database):
            data = json_datetime.load(open(database))
        elif database:
            logging.debug('Database file %r doesn’t exist', database)

        for name, options in conf.items():
            self.append(Site.parse(name, options, data.get(name, {})))

    def save(self, database):
        """Save ``Sites`` to the user’s database.

        Args:
            database (str): Database file to write
        """
        data = {}
        for site in self:
            data[site.name] = site.state

        directory, _ = os.path.split(database)
        temp = tempfile.NamedTemporaryFile(prefix='.',
                                           dir=directory,
                                           delete=False)
        json_datetime.dump(data, temp)
        os.rename(temp.name, database)
