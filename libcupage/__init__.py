#! /usr/bin/python -tt
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""cupage - a tool to check for updates on web pages""" \
    # pylint: disable-msg=W0622
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

__version__ = "0.4.0"
__date__ = "2010-01-22"
__author__ = "James Rowe <jnrowe@gmail.com>"
__copyright__ = "Copyright (C) 2009-2010 James Rowe"
__license__ = "GNU General Public License Version 3"
__credits__ = ""
__history__ = "See Git repository"

from email.utils import parseaddr

__doc__ += """.

%%prog checks web pages and displays changes from the last run that match
a given criteria.  Its original purpose was to check web pages for new software
releases, but it is easily configurable and can be used for other purposes.

Thanks to the excellent lxml package you can use complex XPath and CSS selectors
to match elements within a page.

:version: %s
:author: `%s <mailto:%s>`__
:copyright: %s
:status: WIP
:license: %s
""" % ((__version__, ) + parseaddr(__author__) + (__copyright__, __license__))

import ConfigParser
import json
import logging
import os
import re
import socket
import time

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import httplib2

from lxml import html

try:
    import termstyle
except ImportError:
    termstyle = None # pylint: disable-msg=C0103

# Select colours if terminal is a tty.
if termstyle:
    # pylint: disable-msg=E1101,C0103
    termstyle.auto()
    success = termstyle.green
    fail = termstyle.red
    warn = termstyle.yellow
else:
    # pylint: disable-msg=C0103
    success = fail = warn = str

USER_AGENT = "cupage/%s +http://github.com/JNRowe/cupage/" % __version__

SITES = {
    "cpan": {
        "url": "http://search.cpan.org/dist/{name}/",
        "select": "td small a",
        "match_type": "re",
        "match": "{name}-[\d\.]+.tar.gz",
        "added": "0.4.0",
    },
    "debian": {
        "url": "http://ftp.debian.org/debian/pool/main/{name[0]}/{name}/",
        "select": "td a",
        "match_type": "re",
        "match": r"{name}_[\d\.]+(\.orig\.tar|-\d+\.diff)\.gz",
        "added": "0.3.0",
    },
    "github": {
        "url": "http://github.com/{user}/{name}/downloads",
        "select": "td a",
        "match_type": "re",
        "match": "/{user}/{name}/tarball/.*",
        "keys": ["user", ],
        "added": "0.3.1",
    },
    "google code": {
        "url": "http://code.google.com/p/{name}/downloads/list",
        "select": "td.id a",
        "added": "0.1.0",
    },
    "hackage": {
        "url": "http://hackage.haskell.org/package/{name}",
        "select": "li a",
        "match_type": "re",
        "match": "{name}-[0-9\.]+\.tar\.gz",
        "added": "0.1.0",
    },
    "pypi": {
        "url": "http://pypi.python.org/packages/source/{name[0]}/{name}/",
        "select": "td a",
        "added": "0.1.0",
    },
    "vim-script": {
        "url": "http://www.vim.org/scripts/script.php?script_id={script}",
        "select": "td a",
        "match_type": "re",
        "match": "download_script.php\?src_id=[\d]+",
        "keys": ["script", ],
        "added": "0.3.0",
    },
}

def parse_timedelta(delta):
    """Parse human readable frequency

    >>> parse_timedelta("1d")
    24.0
    >>> parse_timedelta("1 d")
    24.0
    >>> parse_timedelta("0.5 y")
    30660.0
    >>> parse_timedelta("0.5 Y")
    30660.0
    >>> parse_timedelta("1 k")
    Traceback (most recent call last):
        ...
    ValueError: Invalid 'frequency' value
    """
    match = re.match("^(\d+(?:|\.\d+)) *([hdwmy])$", delta, re.IGNORECASE)
    if not match:
        raise ValueError("Invalid 'frequency' value")
    value, units = match.groups()
    units = "hdwmy".index(units.lower())
    # hours per hour/day/week/month/year
    multiplier = (1, 24, 168, 4704, 61320)
    return float(value) * multiplier[units]


def isoformat(secs):
    """Format a epoch offset in an ISO-8601 compliant way

    >>> isoformat(0)
    '1970-01-01T01:00:00'
    >>> isoformat(987654321)
    '2001-04-19T05:25:21'
    """
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(secs))


class Site(object):
    """Simple object for representing a web site"""

    def __init__(self, name, url, selector, select, match_type="tar",
                 match=None, frequency=None):
        """Initialise a new ``Site`` object"""
        self.name = name
        self.url = url
        self.selector = selector
        self.select = select
        self.match_type = match_type
        if self.match_type == "re":
            self.match = re.compile(match)
            self._match = match
        elif match_type in ("gem", "tar", "zip"):
            self.match, self._match = self.package_re(self.name, match_type)
        self.checked = None
        self.frequency = frequency
        self.matches = []

    def __str__(self):
        """Pretty printed ``Site`` string"""
        ret = [
            "%(name)s @ %(url)s using %(match_type)r matcher" % self.__dict__,
        ]
        if self.match_type == "re":
            ret.append("(%r)" % self._match)
        if self.checked:
            ret.append(" last checked %s" % isoformat(self.checked))
        if self.frequency:
            ret.append(time.strftime(" with a check frequency of %s hours",
                                     time.localtime(self.frequency)))
        if self.matches:
            ret.append("\n    ")
            ret.append(", ".join(self.matches))
        else:
            ret.append("\n    No matches")
        return "".join(ret)

    def check(self, cache=None, timeout=None, force=False, no_write=False):
        """Check site for updates"""
        if self.frequency and self.checked:
            next_check = self.checked + (self.frequency * 3600)
            if time.time() < next_check and not force:
                print warn("%s is not due for check until %s"
                           % (self.name, isoformat(next_check)))
                return
        http = httplib2.Http(cache=cache, timeout=timeout)
        # hillbilly monkeypatch to allow us to still read the cache, but make
        # writing a NOP.
        if no_write:
            http.cache.set = lambda x, y: True
        try:
            headers, content = http.request(self.url,
                                            headers={"User-Agent": USER_AGENT})
        except httplib2.ServerNotFoundError:
            print fail("Domain name lookup failed for %s" % self.name)
            return False
        except socket.timeout:
            print fail("Socket timed out on %s" % self.name)
            return False

        if headers.status == 304:
            return
        elif headers.status in (403, 404):
            print fail("%s returned a %s" % (self.name, headers.status))
            return False

        matches = self.find_matches(content)
        if not matches == self.matches:
            print "%s has new matches" % self.name
            for match in matches:
                if match not in self.matches:
                    print success("   " + match)
            self.matches = matches
        self.checked = time.time()

    def find_matches(self, content):
        """Extract matches from content"""
        doc = html.fromstring(content)
        if self.selector == "css":
            selected = doc.cssselect(self.select)
        elif self.selector == "xpath":
            selected = doc.xpath(self.select)
        # We use a set to remove duplicates
        matches = set()
        for sel in selected:
            match = re.search(self.match, sel.get('href', ""))
            if match:
                matches.add(match.group())
        return sorted(list(matches))

    @staticmethod
    def package_re(name, ext):
        r"""Generate a compiled ``re`` for the package

        >>> c, m = Site.package_re("test", "tar")
        >>> re.match(c, "test-0.1.2.tar.bz2").group()
        'test-0.1.2.tar.bz2'
        >>> re.match(c, "test-0.1.2_rc2.tar.gz").group()
        'test-0.1.2_rc2.tar.gz'
        >>> m
        'test-[\\d\\.]+([_-](pre|rc)[\\d]+)?\\.tar.(bz2|gz)'
        >>> c, m = Site.package_re("test", "zip")
        >>> re.match(c, "test-0.1.2-rc2.zip").group()
        'test-0.1.2-rc2.zip'
        >>> re.match(c, "test-0.1.2-pre2.zip").group()
        'test-0.1.2-pre2.zip'
        >>> m
        'test-[\\d\\.]+([_-](pre|rc)[\\d]+)?\\.zip'
        >>> c, m = Site.package_re("test_long", "gem")
        >>> re.match(c, "test_long-0.1.2.gem").group()
        'test_long-0.1.2.gem'
        >>> m
        'test_long-[\\d\\.]+([_-](pre|rc)[\\d]+)?\\.gem'
        """
        if ext == "tar":
            ext = "tar.(bz2|gz)"
        match = r"%s-[\d\.]+([_-](pre|rc)[\d]+)?\.%s" % (name, ext)
        return re.compile(match), match

    @staticmethod
    def parse(name, options, data):
        """Parse data generated by ``Sites.loader``"""
        if "site" in options:
            try:
                site_opts = SITES[options["site"]]
            except KeyError:
                raise ValueError("Invalid site option for %s" % name)
            if "keys" in site_opts:
                for key in site_opts["keys"]:
                    if not key in options:
                        raise ValueError("'%s' is required for site=%s from %s"
                                         % (key, options["site"], name))
            options["name"] = name # For .format usage
            selector = site_opts.get("selector", "css")
            url = site_opts["url"].format(**options) # pylint: disable-msg=W0142
            select = site_opts["select"]
            match_type = site_opts.get("match_type", "tar")
            match = site_opts.get("match", "").format(**options) \
                # pylint: disable-msg=W0142
        elif "url" in options:
            url = options["url"]
            selector = options.get("selector", "css")
            select = options.get("select")
            if not select:
                raise ValueError("missing select option for %s" % name)
            match_type = options.get("match_type", "tar")
            match = options.get("match")
            if match_type == "re" and not match:
                raise ValueError("missing match option for %s" % name)
        else:
            raise ValueError("site or url not specified for %s" % name)
        frequency = options.get("frequency")
        if frequency:
            frequency = parse_timedelta(frequency)
        site = Site(name, url, selector, select, match_type, match, frequency)
        if data:
            site.checked = data.get("checked")
            site.matches = data.get("matches")

        return site

    def state(self):
        """Return ``Site`` state for database storage"""
        return {"matches": self.matches, "checked": self.checked}


class Sites(list):
    """``Site`` bundle wrapper"""

    def load(self, config_file, database):
        """Read sites from a user's config file and database"""
        conf = ConfigParser.ConfigParser()
        conf.read(config_file)
        if not conf.sections():
            logging.debug("Config file `%s' is empty", config_file)
            raise IOError("Error reading config file")

        if os.path.exists(database):
            data = json.load(open(database))
        else:
            logging.debug("Database file `%s' doesn't exist", database)
            data = {}

        for name in conf.sections():
            options = {}
            for opt in conf.options(name):
                options[opt] = conf.get(name, opt)
            self.append(Site.parse(name, options, data.get(name)))

    def save(self, database):
        """Save ``Sites`` to the user's database"""
        data = {}
        for site in self:
            data[site.name] = site.state()
        json.dump(data, open(database, "w"), indent=4)
