#
# coding=utf-8
"""cupage - a tool to check for updates on web pages"""
# Copyright © 2009-2013  James Rowe <jnrowe@gmail.com>
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
__author__ = 'James Rowe <jnrowe@gmail.com>'
__copyright__ = 'Copyright © 2009-2013  James Rowe'
__license__ = 'GNU General Public License Version 3'
__credits__ = ''
__history__ = 'See Git repository at https://github.com/JNRowe/cupage'

from email.utils import parseaddr

__doc__ += """.

cupage checks web pages and displays changes from the last run that match
a given criteria.  Its original purpose was to check web pages for new software
releases, but it is easily configurable and can be used for other purposes.

Thanks to the excellent lxml package you can use complex XPath and CSS
selectors to match elements within a page, if you wish.

:version: %s
:author: `%s <mailto:%s>`__
:copyright: %s
:status: WIP
:license: %s
""" % ((__version__, ) + parseaddr(__author__) + (__copyright__, __license__))

import datetime
import json
import logging
import os
import re
import socket
import ssl
import tempfile

try:
    # For Python 3
    import http.client as httplib
    import configparser
except ImportError:
    import httplib  # NOQA
    import ConfigParser as configparser  # NOQA

import httplib2

from lxml import html

from .i18n import _
from . import utils


#: User agent to use for HTTP requests
USER_AGENT = 'cupage/%s +https://github.com/JNRowe/cupage/' % __version__

#: Site specific configuration data
SITES = {
    'bitbucket': {
        'url': 'https://bitbucket.org/{user}/{name}/downloads',
        'select': 'td.name a.execute',
        'added': '0.7.0',
        'keys': {'user': 'bitbucket user name', },
    },
    'cpan': {
        'url': 'http://search.cpan.org/dist/{name}/',
        'select': 'td small a',
        'match_type': 're',
        'match': '{name}-[\d\.]+.tar.gz',
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
        'keys': {'user': 'GitHub user name', },
        'added': '0.3.1',
        'robots': 'false',
    },
    'google code': {
        'url': 'http://code.google.com/p/{name}/downloads/list',
        'select': 'td.id a',
        'added': '0.1.0',
        'deprecated': 'Uploads no longer supported, find another source',
    },
    'hackage': {
        'url': 'http://hackage.haskell.org/package/{name}',
        'match_func': 'hackage',
        'added': '0.1.0',
    },
    'luaforge': {
        'url': 'http://files.luaforge.net/releases/{name}/{name}}',
        'select': 'td a',
        'added': '0.7.0',
    },
    'pypi': {
        'url': 'https://pypi.python.org/simple/{name}/',
        'select': 'a',
        'added': '0.1.0',
        'match': '({name}-[0-9\.]+\.tar\.gz)(?:#.*)',
    },
    'rubyforge': {
        'url': 'http://rubyforge.org/frs/?group_id={group}',
        'select': 'dd a',
        'keys': {'group': 'Group identifier for file downloads', },
        'added': '0.7.0',
    },
    'savannah': {
        'url': 'http://download.savannah.gnu.org/releases/{name}/',
        'select': 'td a',
        'added': '0.7.0',
    },
    'sourceforge': {
        'url': 'http://sourceforge.net/api/file/index/project-name/{name}/rss',
        'match_func': 'sourceforge',
        'added': '0.7.1',
    },
    'vim-script': {
        'url': 'http://www.vim.org/scripts/script.php?script_id={script}',
        'select': 'td a',
        'match_type': 're',
        'match': 'download_script.php\?src_id=([\d]+)',
        'keys': {'script': 'script id on the vim website', },
        'added': '0.3.0',
    },
}


class Site(object):

    """Simple object for representing a web site."""

    def __init__(self, name, url, match_func='default', options=None,
                 frequency=None, robots=True, checked=None, matches=None):
        """Initialise a new ``Site`` object.

        :param str name: Site name
        :param str url: URL for site
        :param str match_func: Function to use for retrieving matches
        :param dict options: Options for :attr:`match_func`
        :param int frequency: Site check frequency
        :param bool robots: Whether to respect a host's :file:`robots.txt`
        :param datetime.datetime checked: Last checked date
        :param list matches: Previous matches

        """
        self.name = name
        self.url = url
        self.match_func = match_func
        self.options = options if options else {}
        re_verbose = 're_verbose' in options
        if options.get('match_type') == 're':
            self.match = re.compile(options['match'],
                                    flags=re.VERBOSE if re_verbose else 0)
        elif options.get('match_type') in ('gem', 'tar', 'zip'):
            self.match = self.package_re(self.name, options['match_type'],
                                         re_verbose)
        self.checked = checked
        self.frequency = frequency
        self.robots = robots
        self.matches = matches if matches else []

    def __repr__(self):
        return '%r(%r, %r, ...)' % (self.__class__.__name__, self.name,
                                    self.url)

    def __str__(self):
        """Pretty printed ``Site`` string."""
        ret = ['%s @ %s using %s matcher' % (self.name, self.url,
                                             self.match_func), ]
        if self.checked:
            ret.append(' last checked %s' % self.checked)
        if self.frequency:
            ret.append(' with a check frequency of %s' % self.frequency)
        if self.matches:
            ret.append('\n    ')
            ret.append(', '.join(utils.sort_packages(self.matches)))
        else:
            ret.append('\n    No matches')
        return ''.join(ret)

    def check(self, cache=None, timeout=None, force=False, no_write=False):
        """Check site for updates.

        :param str cache: :class:`httplib2.Http` cache location
        :param int timeout: Timeout value for :class:`httplib2.Http`
        :param bool force: Ignore configured check frequency
        :param bool no_write: Do not write to cache, useful for testing

        """
        if not force and self.frequency and self.checked:
            next_check = self.checked + self.frequency
            if datetime.datetime.utcnow() < next_check:
                print(utils.warn(_('%s is not due for check until %s')
                                 % (self.name, next_check)))
                return
        http = httplib2.Http(cache=cache, timeout=timeout,
                             ca_certs=utils.CA_CERTS)
        # hillbilly monkeypatch to allow us to still read the cache, but make
        # writing a NOP
        if no_write:
            http.cache.set = lambda x, y: True

        if self.robots and not os.getenv('CUPAGE_IGNORE_ROBOTS_TXT'):
            if not utils.robots_test(http, self.url, self.name, USER_AGENT):
                return False

        try:
            headers, content = http.request(self.url,
                                            headers={'User-Agent': USER_AGENT})
        except httplib2.ServerNotFoundError:
            print(utils.fail(_('Domain name lookup failed for %s')
                             % self.name))
            return False
        except ssl.SSLError as error:
            print(utils.fail(_('SSL error %s (%s)') % (self.name,
                                                       error.message)))
            return False
        except socket.timeout:
            print(utils.fail(_('Socket timed out on %s') % self.name))
            return False

        charset = utils.charset_from_headers(headers)

        if not headers.get('content-location', self.url) == self.url:
            print(utils.warn(_('%s moved to %s')
                             % (self.name, headers['content-location'])))
        if headers.status == httplib.NOT_MODIFIED:
            return
        elif headers.status in (httplib.FORBIDDEN, httplib.NOT_FOUND):
            print(utils.fail(_('%s returned %r')
                             % (self.name, httplib.responses[headers.status])))
            return False

        matches = getattr(self, 'find_%s_matches' % self.match_func)(content,
                                                                     charset)
        new_matches = [s for s in matches if not s in self.matches]
        self.matches = matches
        self.checked = datetime.datetime.utcnow()
        return new_matches

    def find_default_matches(self, content, charset):
        """Extract matches from content.

        :param str content: Content to search
        :param str charset: Character set for content

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

    def find_github_matches(self, content, charset):
        """Extract matches from GitHub content.

        :param str content: Content to search
        :param str charset: Character set for content

        """
        content = content.encode(charset)
        doc = json.loads(content)
        return sorted(tag['name'] for tag in doc)

    def find_hackage_matches(self, content, charset):
        """Extract matches from hackage content.

        :param str content: Content to search
        :param str charset: Character set for content

        """
        doc = html.fromstring(content)
        data = doc.cssselect('table tr')[0][1]
        return sorted(x.text for x in data.getchildren())

    def find_sourceforge_matches(self, content, charset):
        """Extract matches from sourceforge content.

        :param str content: Content to search
        :param str charset: Character set for content

        """
        # We use lxml.html here to sidestep part of the stupidity of RSS 2.0,
        # if a usable format on sf comes along we'll switch to it.
        doc = html.fromstring(content)
        matches = set()
        for x in doc.cssselect('item link'):
            if '/download' in x.tail:
                matches.add(x.tail.split('/')[-2])
        return sorted(list(matches))

    @staticmethod
    def package_re(name, ext, verbose=False):
        """Generate a compiled ``re`` for the package.

        :param str name: File name to check for
        :param str ext: File extension to check
        :param bool verbose: Whether to enable :data:`re.VERBOSE`

        """
        if ext == 'tar':
            ext = 'tar.(?:bz2|gz|xz)'
        match = r'%s-[\d\.]+(?:[_-](?:pre|rc)[\d]+)?\.%s' % (name, ext)
        return re.compile(match, flags=re.VERBOSE if verbose else 0)

    @staticmethod
    def parse(name, options, data):
        """Parse data generated by ``Sites.loader``.

        :param str name: Site name from config file
        :param dict options: Site options from config file
        :param data: Stored data from database file

        """
        def get_bool(name):
            """Read boolean option from config file values"""
            return options.get(name, '').lower() in ('1', 'true', 'on')

        if 'site' in options:
            try:
                site_opts = SITES[options['site']]
            except KeyError:
                raise ValueError('Invalid site option for %s' % name)
            if 'deprecated' in site_opts:
                print "%s: %s - %s" % (name, options['site'],
                                       site_opts['deprecated'])
            if 'keys' in site_opts:
                for key in site_opts['keys']:
                    if not key in options:
                        raise ValueError('%r is required for site=%s from %s'
                                         % (key, options['site'], name))
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
            robots = get_bool('robots')
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
                raise ValueError('missing select option for %s' % name)
            if match_options['match_type'] == 're' \
                and not match_options['match']:
                raise ValueError('missing match option for %s' % name)
            robots = get_bool('robots')
        else:
            raise ValueError('site or url not specified for %s' % name)
        frequency = options.get('frequency')
        if frequency:
            frequency = utils.parse_timedelta(frequency)
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
        """Read sites from a user's config file and database.

        :param str config_file: Config file to read
        :param str database: Database file to read

        """
        conf = configparser.ConfigParser()
        conf.read(config_file)
        if not conf.sections():
            logging.debug('Config file %r is empty', config_file)
            raise IOError('Error reading config file')

        data = {}
        if database and os.path.exists(database):
            data = json.load(open(database),
                             object_hook=utils.json_to_datetime)
        elif database:
            logging.debug("Database file %r doesn't exist", database)

        for name in conf.sections():
            options = {}
            for opt in conf.options(name):
                options[opt] = conf.get(name, opt)
            self.append(Site.parse(name, options, data.get(name, {})))

    def save(self, database):
        """Save ``Sites`` to the user's database.

        :param str database: Database file to write

        """
        data = {}
        for site in self:
            data[site.name] = site.state

        directory, filename = os.path.split(database)
        temp = tempfile.NamedTemporaryFile(prefix='.', dir=directory,
                                           delete=False)
        json.dump(data, temp, indent=4, cls=utils.CupageEncoder)
        os.rename(temp.name, database)
