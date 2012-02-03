#
# coding=utf-8
"""utils - Utility functions for cupage"""
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

import re
import robotparser
import socket
import time
import urlparse

import blessings
import httplib2


T = blessings.Terminal()


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
    '1970-01-01T00:00:00'
    >>> isoformat(987654321)
    '2001-04-19T04:25:21'
    """
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(secs))


def sort_packages(packages):
    """Order package list according to version number

    >>> sort_packages(['pkg-0.1.tar.gz', 'pkg-0.2.1.tar.gz', 'pkg-0.2.tar.gz'])
    ['pkg-0.1.tar.gz', 'pkg-0.2.tar.gz', 'pkg-0.2.1.tar.gz']
    """
    # Very ugly key function, but it removes the need to mangle unicode/str
    # objects for digit tests
    return sorted(packages, key=lambda s: [i for i in s if i.isdigit()])


def robots_test(http, url, name, user_agent="*"):
    """Check whether a given URL is blocked by robots.txt"""
    parsed = urlparse.urlparse(url, "http")
    if parsed.scheme.startswith("http"):
        robots_url = "%(scheme)s://%(netloc)s/robots.txt" \
            % parsed._asdict()
        robots = robotparser.RobotFileParser(robots_url)
        try:
            headers, content = http.request(robots_url)
        except httplib2.ServerNotFoundError:
            print fail("Domain name lookup failed for %s" % name)
            return False
        except socket.timeout:
            print fail("Socket timed out on %s" % name)
            return False
        # Ignore errors 4xx errors for robots.txt
        if not str(headers.status).startswith("4"):
            robots.parse(content.splitlines())
            if not robots.can_fetch(user_agent, url):
                print fail("Can't check %s, blocked by robots.txt" % name)
                return False


def _format_info(text, colour):
    return "%s %s" % (getattr(T, 'bold_white_on_%s' % colour)('*'),
                      getattr(T, 'bright_%s' % colour)(text))


def success(text):
    return _format_info(text, 'green')


def fail(text):
    return _format_info(text, 'red')


def warn(text):
    return _format_info(text, 'yellow')
