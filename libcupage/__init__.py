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

__version__ = "0.2.0"
__date__ = "2009-09-18"
__author__ = "James Rowe <jnrowe@gmail.com>"
__copyright__ = "Copyright (C) 2009 James Rowe"
__license__ = "GNU General Public License Version 3"
__credits__ = ""
__history__ = "See Git repository"

import ConfigParser
import gzip
import inspect
import logging
import os
import re
import socket
import sys
import time
import urllib2
import zlib

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from email.utils import (formatdate, parsedate)
except ImportError: # Python 2.4
    from email.Utils import (formatdate, parsedate)

from urlparse import urlparse

from lxml import html

if "timeout" in inspect.getargspec(urllib2.urlopen)[0]:
    _urlopen = lambda req, timeout: urllib2.urlopen(req, timeout=timeout)
else:
    logging.debug("Network timeout is not supported with python v%s"
                  % sys.version.split()[0])
    _urlopen = lambda req, timeout: urllib2.urlopen(req)

class Site(object):
    """Simple object for representing a web site"""

    def __init__(self, name, url, selector, select, match_type="tar",
                 match=None):
        """Initialise a new ``Site`` object"""
        self.name = name
        self.url = url
        self.selector = selector
        self.select = select
        self.match_type = match_type
        if self.match_type == "re":
            self.match = re.compile(match)
        elif match_type in ("gem", "tar", "zip"):
            self.match = self.package_re(self.name, match_type)
        self.etag = None
        self.modified = None
        self.matches = []

    def __str__(self):
        """Pretty printed ``Site`` string"""
        ret = [
            "%(name)s @ %(url)s using %(match_type)r matcher" % self.__dict__,
        ]
        if self.modified:
            ret.append(time.strftime(" on %Y-%m-%dT%H:%M",
                                     time.localtime(self.modified)))
        if self.matches:
            ret.append("\n    ")
            ret.append(", ".join(self.matches))
        else:
            ret.append("\n    No matches")
        return "".join(ret)

    def check(self, timeout=None):
        """Check site for updates"""
        try:
            page = self.fetch_page(timeout)
        except urllib2.HTTPError, e:
            if e.code == 304:
                return
            elif e.code == 404:
                print "%s returned a 404" % self.name
                return False
            raise
        if not page.url == self.url:
            print "%s moved to %s" % (self.name, page.url)

        try:
            data = page.read()
        except socket.timeout, e:
            print "%s timed out" % (self.name)
            return False
        if page.headers.get('content-encoding', '') == 'deflate':
            data = zlib.decompress(data, -zlib.MAX_WBITS)
        elif page.headers.get('content-encoding', '') == 'gzip':
            data = gzip.GzipFile(fileobj=StringIO(data)).read()

        if "etag" in page.headers.dict:
            self.etag = page.headers["etag"]
        if "last-modified" in page.headers.dict:
            self.modified = time.mktime(parsedate(page.headers["last-modified"]))

        if len(data) == 0:
            print "%s unchanged" % self.name

        doc = html.fromstring(data)
        if self.selector == "css":
            selected = doc.cssselect(self.select)
        elif self.selector == "xpath":
            selected = doc.xpath(self.select)
        matches = []
        for sel in selected:
            match = re.search(self.match, sel.get('href', ""))
            if match:
                matches.append(match.group())
        matches = sorted(matches)
        if not matches == self.matches:
            print "%s has new matches:" % self.name
            for match in matches:
                if match not in self.matches:
                    print "   ", match
            self.matches = matches

    def fetch_page(self, timeout=None):
        """Generate a web page file handle"""
        if not timeout:
            timeout = 30
        if not urlparse(self.url)[0] in ('file', 'ftp', 'http', 'https'):
            return ValueError("Invalid url %s" % self.url)
        request = urllib2.Request(self.url)
        request.add_header("User-Agent",
                           "cupage/%s +http://github.com/jnrowe/cupage/")
        if self.etag:
            request.add_header("If-None-Match", self.etag)
        if self.modified:
            request.add_header("If-Modified-Since", formatdate(self.modified))
        request.add_header("Accept-encoding", "deflate, gzip")
        return _urlopen(request, timeout=timeout)

    @staticmethod
    def package_re(name, ext):
        """Generate a compiled ``re`` for the package

        >>> c = Site.package_re("test", "tar")
        >>> re.match(c, "test-0.1.2.tar.bz2").group()
        'test-0.1.2.tar.bz2'
        >>> re.match(c, "test-0.1.2_rc2.tar.gz").group()
        'test-0.1.2_rc2.tar.gz'
        >>> c = Site.package_re("test", "zip")
        >>> re.match(c, "test-0.1.2-rc2.zip").group()
        'test-0.1.2-rc2.zip'
        >>> re.match(c, "test-0.1.2-pre2.zip").group()
        'test-0.1.2-pre2.zip'
        >>> c = Site.package_re("test_long", "gem")
        >>> re.match(c, "test_long-0.1.2.gem").group()
        'test_long-0.1.2.gem'
        """
        if ext == "tar":
            ext = "tar.(bz2|gz)"
        return re.compile(r"%s-([\d\.]+([_-](pre|rc)[\d]+)?)\.%s" % (name, ext))

    @staticmethod
    def parse(name, options, data):
        """Parse data generated by ``Sites.loader``"""
        if "site" in options:
            site = options["site"]
            selector = "css"
            match = options.get("match")
            if site == "debian":
                url = "http://ftp.debian.org/debian/pool/main/%s/%s/" \
                    % (name[0], name)
                select = "td a"
                match_type = "re"
                match = r"%s_[\d\.]+(\.orig\.tar|-\d+\.diff)\.gz" % name
            elif site == "google code":
                url = "http://code.google.com/p/%s/downloads/list" % name
                select = "td.id a"
                match_type = options.get("match_type", "tar")
            elif site == "hackage":
                url = "http://hackage.haskell.org/packages/archive/%s/" % name
                select = "pre a"
                match_type = "re"
                match = "^[0-9\.]+"
            elif site == "pypi":
                url = "http://pypi.python.org/packages/source/%s/%s/" \
                    % (name[0], name)
                select = "td a"
                match_type = options.get("match_type", "tar")
            else:
                raise ValueError("Invalid site option for %s" % site)
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
        site = Site(name, url, selector, select, match_type, match)
        if data:
            site.etag = data.get("etag")
            site.modified = data.get("modified")
            site.matches = data.get("matches")
        return site

    def state(self):
        """Return ``Site`` state for database storage"""
        return {"etag": self.etag, "modified": self.modified,
                "matches": self.matches}


class Sites(list):
    """``Site`` bundle wrapper"""
    def load(self, config_file, database):
        """Read sites from a user's config file and database"""
        conf = ConfigParser.ConfigParser()
        conf.read(config_file)
        if not conf.sections():
            logging.debug("Config file `%s' is empty" % config_file)
            raise IOError("Error reading config file")

        if os.path.exists(database):
            data = pickle.load(open(database))
        else:
            logging.debug("Database file `%s' doesn't exist" % database)
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
            data[site.name] =  site.state()
        pickle.dump(data, open(database, "w"), -1)

