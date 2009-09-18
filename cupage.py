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

from email.utils import parseaddr
__doc__ += """

cupage checks for updates on one or more web pages specified in a simple config
file.

A simple config example is::

.. code-block:: ini

    # dev-python
    [pep8]
    site = pypi
    match_type = tar
    [pyisbn]
    url = http://www.jnrowe.ukfsn.org/_downloads/
    select = pre > a
    match_type = tar

In the first example we only need to specify the type of archive as the page
location and search patterns are set up based on the value of ``site``.  In the
second example we specify a page location and also a CSS based selector to
check.

@version: %s
@author: U{%s <mailto:%s>}
@copyright: %s
@status: WIP
@license: %s
""" % ((__version__, ) + parseaddr(__author__) + (__copyright__, __license__))

import ConfigParser
import cPickle
import cStringIO
import gzip
import logging
import optparse
import os
import re
import sys
import time
import urllib2
import zlib

from email.utils import formatdate
from urlparse import urlparse

from lxml import html

# Pull the first paragraph from the docstring
USAGE = __doc__[:__doc__.find('\n\n', 100)].splitlines()[2:]
# Replace script name with optparse's substitution var, and rebuild string
USAGE = "\n".join(USAGE).replace("cupage", "%prog")

TIMEOUT = 30

class Site(object):
    package = lambda ext: re.compile(r"[a-z0-9]+-([0-9\.]+)%s" % ext)
    gem = package("gem")
    tar = package("tar.(bz2|gz)")
    zip = package("zip")

    def __init__(self, name, url, selector, select, match_type="re",
                 match=None):
        self.name = name
        self.url = url
        self.selector = selector
        self.select = select
        self.match_type = match_type if match_type else "re"
        if self.match_type == "re":
            self.match = re.compile(match)
        elif match_type in ("gem", "tar", "zip"):
            self.match = getattr(self, match_type)
        self.etag = None
        self.modified = None
        self.matches = []

    def __str__(self):
        s = "%(name)s @ %(url)s using %(match_type)r matcher" % self.__dict__
        if self.modified:
            s += time.strftime(" on %Y-%m-%dT%H:%M",
                               time.localtime(self.modified))
        if self.matches:
            s += "\n"
            for match in self.matches:
                s += "    %s" % match
        else:
            s += "\n    No matches"
        return s

    def check(self):
        page = self.fetch_page()
        if not page.url == self.url:
            print "%s moved to %s" % (self.name, page.url)

        data = page.read()
        if page.headers.get('content-encoding', '') == 'deflate':
            data = zlib.decompress(data, -zlib.MAX_WBITS)
        elif page.headers.get('content-encoding', '') == 'gzip':
            data = gzip.GzipFile(fileobj=cStringIO.StringIO(data)).read()

        if "etag" in page.headers.dict:
            self.etag = page.headers["etag"]
        if "last-modified" in page.headers.dict:
            self.modified = page.headers["last-modified"]

        if len(data) == 0:
            print "%s unchanged" % self.name

        doc = html.fromstring(data)
        if self.selector == "css":
            selected = doc.cssselect(self.select)
        elif self.selector == "xpath":
            selected = doc.xpath(self.select)
        matches = []
        for sel in selected:
            match = re.search(self.match, sel.attrib['href'])
            if match:
                matches.append(match.group())
        matches = sorted(matches)
        if not matches == self.matches:
            print "%s has new matches:" % self.name
            for match in filter(lambda s: not s in self.matches, matches):
                print "   ", match
            self.matches = matches

    def fetch_page(self):
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
        return urllib2.urlopen(request, timeout=TIMEOUT)

    @staticmethod
    def parse(name, options, data):
        if "site" in options:
            site = options["site"]
            selector = "css"
            match = None
            if site == "google code":
                url = "http://code.google.com/p/%s/downloads/list" % name
                select = "td.id a"
                match_type = options.get("match_type", "tar")
            elif site == "hackage":
                url = "http://hackage.haskell.org/packages/archive/%s/" % name
                select = "pre a"
                match_type = "tar"
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
            match_type = options.get("match_type")
            if not match_type:
                raise ValueError("missing match_type option for %s" % name)
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
        return {"etag": self.etag, "modified": self.modified,
                "matches": self.matches}


class Sites(list):
    def load(self, config_file, database):
        """Read sites from a user's config file"""
        conf = ConfigParser.ConfigParser()
        conf.read(config_file)
        if not conf.sections():
            logging.debug("Config file `%s' is empty" % config_file)
            raise IOError("Error reading config file")

        if os.path.exists(database):
            data = cPickle.load(open(database))
        else:
            logging.debug("Database file `%s' doesn't exist" % database)
            data = {}

        for name in conf.sections():
            options = {}
            for opt in conf.options(name):
                options[opt] = conf.get(name, opt)
            self.append(Site.parse(name, options, data.get(name)))

    def save(self, database):
        data = {}
        for site in self:
            data[site.name] =  site.state()
        cPickle.dump(data, open(database, "w"), -1)


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

    parser.add_option("-v", "--verbose", action="store_true",
                      dest="verbose", help="produce verbose output")
    parser.add_option("-q", "--quiet", action="store_false",
                      dest="verbose",
                      help="output only matches and errors")

    options, args = parser.parse_args()

    return options, args

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        datefmt="%Y-%m-%dT%H:%M:%S%z")

    options, args = process_command_line()

    sites = Sites()
    try:
        sites.load(options.config, options.database)
    except IOError:
        return 1
    for site in sites:
        if not args or site.name in args:
            if options.verbose:
                print "Checking %s..." % site.name
            site.check()
    if not options.no_write:
        sites.save(options.database)

if __name__ == '__main__':
    sys.exit(main())

