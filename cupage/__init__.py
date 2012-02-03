#
# coding=utf-8
"""cupage - a tool to check for updates on web pages"""
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

from . import _version

__version__ = _version.dotted
__date__ = _version.date
__author__ = "James Rowe <jnrowe@gmail.com>"
__copyright__ = "Copyright (C) 2009-2012  James Rowe"
__license__ = "GNU General Public License Version 3"
__credits__ = ""
__history__ = "See Git repository at https://github.com/JNRowe/cupage"

from email.utils import parseaddr

__doc__ += """.

%%prog checks web pages and displays changes from the last run that match
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
import httplib
import json
import logging
import os
import re
import socket
import tempfile

import configobj
import httplib2

from lxml import html

from . import utils


USER_AGENT = "cupage/%s +https://github.com/JNRowe/cupage/" % __version__

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
        "re_verbose": True,
        "match": r"""{name}_[\d\.]+
                     (?:\.orig\.tar|-\d+\.(?:diff|debian.tar))
                     \.(?:bz2|gz)""",
        "added": "0.3.0",
    },
    "failpad": {
        "url": "https://launchpad.net/{name}/+download",
        "select": "table.listing td a",
        "added": "0.5.0",
    },
    "github": {
        "url": "https://api.github.com/repos/{user}/{name}/tags",
        "match_func": "github",
        "keys": {"user": "GitHub user name", },
        "added": "0.3.1",
        "robots": "false",
    },
    "google code": {
        "url": "http://code.google.com/p/{name}/downloads/list",
        "select": "td.id a",
        "added": "0.1.0",
    },
    "hackage": {
        "url": "http://hackage.haskell.org/package/{name}",
        "match_func": "hackage",
        "added": "0.1.0",
    },
    "pypi": {
        "url": "http://pypi.python.org/simple/{name}/",
        "select": "a",
        "added": "0.1.0",
        "match": "({name}-[0-9\.]+\.tar\.gz)(?:#.*)",
    },
    "vim-script": {
        "url": "http://www.vim.org/scripts/script.php?script_id={script}",
        "select": "td a",
        "match_type": "re",
        "match": "download_script.php\?src_id=([\d]+)",
        "keys": {"script": "script id on the vim website", },
        "added": "0.3.0",
    },
}


class Site(object):
    """Simple object for representing a web site"""

    def __init__(self, name, url, match_func="default", options=None,
                 frequency=None, robots=True, checked=None, matches=None):
        """Initialise a new ``Site`` object"""
        self.name = name
        self.url = url
        self.match_func = match_func
        self.options = options if options else {}
        re_verbose = 're_verbose' in options
        if options.get("match_type") == "re":
            self.match = re.compile(options["match"],
                                    flags=re.VERBOSE if re_verbose else 0)
        elif options.get("match_type") in ("gem", "tar", "zip"):
            self.match = self.package_re(self.name, options["match_type"],
                                         re_verbose)
        self.checked = checked
        self.frequency = frequency
        self.robots = robots
        self.matches = matches if matches else []

    def __str__(self):
        """Pretty printed ``Site`` string"""
        ret = ["%s @ %s using %s matcher" % (self.name, self.url,
                                             self.match_func), ]
        if self.checked:
            ret.append(" last checked %s" % self.checked)
        if self.frequency:
            ret.append(" with a check frequency of %s" % self.frequency)
        if self.matches:
            ret.append("\n    ")
            ret.append(", ".join(utils.sort_packages(self.matches)))
        else:
            ret.append("\n    No matches")
        return "".join(ret)

    def check(self, cache=None, timeout=None, force=False, no_write=False):
        """Check site for updates"""
        if self.frequency and self.checked:
            next_check = self.checked + self.frequency
            if datetime.datetime.utcnow() < next_check and not force:
                print utils.warn("%s is not due for check until %s"
                                 % (self.name, next_check))
                return
        # Disable SSL validation as 0.7 forces it, but includes very few certs
        http = httplib2.Http(cache=cache, timeout=timeout,
                             disable_ssl_certificate_validation=True)
        # hillbilly monkeypatch to allow us to still read the cache, but make
        # writing a NOP
        if no_write:
            http.cache.set = lambda x, y: True

        if self.robots and not os.getenv("CUPAGE_IGNORE_ROBOTS_TXT"):
            if not utils.robots_test(http, self.url, self.name, USER_AGENT):
                return False

        try:
            headers, content = http.request(self.url,
                                            headers={"User-Agent": USER_AGENT})
        except httplib2.ServerNotFoundError:
            print utils.fail("Domain name lookup failed for %s" % self.name)
            return False
        except socket.timeout:
            print utils.fail("Socket timed out on %s" % self.name)
            return False

        if not headers.get("content-location", self.url) == self.url:
            print utils.warn("%s moved to %s"
                       % (self.name, headers["content-location"]))
        if headers.status == httplib.NOT_MODIFIED:
            return
        elif headers.status in (httplib.FORBIDDEN, httplib.NOT_FOUND):
            print utils.fail("%s returned %r"
                             % (self.name, httplib.responses[headers.status]))
            return False

        matches = getattr(self, "find_%s_matches" % self.match_func)(content)
        new_matches = filter(lambda s: s not in self.matches, matches)
        self.matches = matches
        self.checked = datetime.datetime.utcnow()
        return new_matches

    def find_default_matches(self, content):
        """Extract matches from content"""
        doc = html.fromstring(content)
        if self.options["selector"] == "css":
            selected = doc.cssselect(self.options["select"])
        elif self.options["selector"] == "xpath":
            selected = doc.xpath(self.options["select"])
        # We use a set to remove duplicates
        matches = set()
        for sel in selected:
            match = re.search(self.match, sel.get('href', ""))
            if match:
                groups = match.groups()
                matches.add(groups[0] if groups else match.group())
        return sorted(list(matches))

    def find_github_matches(self, content):
        """Extract matches from GitHub content"""
        doc = json.loads(content)
        return [tag['name'] for tag in doc]

    def find_hackage_matches(self, content):
        """Extract matches from hackage content"""
        doc = html.fromstring(content)
        data = doc.cssselect('table tr')[0][1]
        return [x.text for x in data.getchildren()]

    @staticmethod
    def package_re(name, ext, verbose=False):
        r"""Generate a compiled ``re`` for the package

        >>> c = Site.package_re("test", "tar")
        >>> re.match(c, "test-0.1.2.tar.bz2").group()
        'test-0.1.2.tar.bz2'
        >>> re.match(c, "test-0.1.2_rc2.tar.gz").group()
        'test-0.1.2_rc2.tar.gz'
        >>> c.pattern
        'test-[\\d\\.]+(?:[_-](?:pre|rc)[\\d]+)?\\.tar.(?:bz2|gz)'
        >>> c = Site.package_re("test", "zip")
        >>> re.match(c, "test-0.1.2-rc2.zip").group()
        'test-0.1.2-rc2.zip'
        >>> re.match(c, "test-0.1.2-pre2.zip").group()
        'test-0.1.2-pre2.zip'
        >>> c.pattern
        'test-[\\d\\.]+(?:[_-](?:pre|rc)[\\d]+)?\\.zip'
        >>> c = Site.package_re("test_long", "gem")
        >>> re.match(c, "test_long-0.1.2.gem").group()
        'test_long-0.1.2.gem'
        >>> c.pattern
        'test_long-[\\d\\.]+(?:[_-](?:pre|rc)[\\d]+)?\\.gem'
        """
        if ext == "tar":
            ext = "tar.(?:bz2|gz)"
        match = r"%s-[\d\.]+(?:[_-](?:pre|rc)[\d]+)?\.%s" % (name, ext)
        return re.compile(match, flags=re.VERBOSE if verbose else 0)

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
                        raise ValueError("%r is required for site=%s from %s"
                                         % (key, options["site"], name))
            options["name"] = name  # For .format usage

            def get_val(name, default=None):
                """Get option from site defaults with local override"""
                return options.get(name, site_opts.get(name, default))

            match_func = get_val("match_func", "default")
            url = get_val("url").format(**options)  # pylint: disable-msg=W0142
            match_options = {
                "selector": get_val("selector", "css"),
                "select": get_val("select"),
                "match_type": get_val("match_type", "tar"),
                "re_verbose": get_val("re_verbose", False),
                "match": get_val("match", "").format(**options),
            }  # pylint: disable-msg=W0142,C0301
            robots = "robots" in options and options.as_bool("robots")
        elif "url" in options:
            match_func = options.get("match_func", "default")
            url = options["url"]
            match_options = {
                "selector": options.get("selector", "css"),
                "select": options.get("select"),
                "match_type": options.get("match_type", "tar"),
                "match": options.get("match"),
            }
            if not match_options["select"]:
                raise ValueError("missing select option for %s" % name)
            if match_options["match_type"] == "re" \
                and not match_options["match"]:
                raise ValueError("missing match option for %s" % name)
            robots = "robots" in options and options.as_bool("robots")
        else:
            raise ValueError("site or url not specified for %s" % name)
        frequency = options.get("frequency")
        if frequency:
            frequency = utils.parse_timedelta(frequency)
        site = Site(name, url, match_func, match_options, frequency, robots,
                    data.get("checked"), data.get("matches"))
        return site

    def state(self):
        """Return ``Site`` state for database storage"""
        return {"matches": self.matches, "checked": self.checked}


class Sites(list):
    """``Site`` bundle wrapper"""

    def load(self, config_file, database):
        """Read sites from a user's config file and database"""
        conf = configobj.ConfigObj(config_file, file_error=True)
        if not conf.sections:
            logging.debug("Config file `%s' is empty", config_file)
            raise IOError("Error reading config file")

        if os.path.exists(database):
            data = json.load(open(database),
                             object_hook=utils.json_to_datetime)
        else:
            logging.debug("Database file `%s' doesn't exist", database)
            data = {}

        for name, options in conf.items():
            self.append(Site.parse(name, options, data.get(name, {})))

    def save(self, database):
        """Save ``Sites`` to the user's database"""
        data = {}
        for site in self:
            data[site.name] = site.state()

        directory, filename = os.path.split(database)
        temp = tempfile.NamedTemporaryFile(prefix='.', dir=directory,
                                           delete=False)
        json.dump(data, temp, indent=4, cls=utils.CupageEncoder)
        os.rename(temp.name, database)
