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

import datetime
import json
import re
import robotparser
import socket
import urlparse

import blessings
import httplib2


T = blessings.Terminal()


def parse_timedelta(delta):
    """Parse human readable frequency

    >>> parse_timedelta("3h")
    datetime.timedelta(0, 10800)
    >>> parse_timedelta("1d")
    datetime.timedelta(1)
    >>> parse_timedelta("1 d")
    datetime.timedelta(1)
    >>> parse_timedelta("0.5 y")
    datetime.timedelta(182, 43200)
    >>> parse_timedelta("0.5 Y")
    datetime.timedelta(182, 43200)
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
    multiplier = (1, 24, 168, 672, 8760)
    return datetime.timedelta(hours=float(value) * multiplier[units])


def sort_packages(packages):
    """Order package list according to version number

    >>> sort_packages(['pkg-0.1.tar.gz', 'pkg-0.2.1.tar.gz', 'pkg-0.2.tar.gz'])
    ['pkg-0.1.tar.gz', 'pkg-0.2.tar.gz', 'pkg-0.2.1.tar.gz']
    >>> sort_packages(['v0.1.0', 'v0.11.0', 'v0.1.2'])
    ['v0.1.0', 'v0.1.2', 'v0.11.0']
    """
    # Very ugly key function, but it handles the common case of varying
    # component length just about "Good Enough™"
    return sorted(packages,
                  key=lambda s: [i for i in s if i.isdigit() or i == '.'])


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


class CupageEncoder(json.JSONEncoder):
    """Custom JSON encoding for supporting ``datetime`` objects"""
    def default(self, obj):
        try:
            return obj.isoformat()
        except TypeError:
            pass
        return json.JSONEncoder.default(self, obj)


def json_to_datetime(obj):
    """Parse datetime objects from ``cupage`` databases"""
    if "checked" in obj:
        try:
            result = datetime.datetime.strptime(obj['checked'],
                                                '%Y-%m-%dT%H:%M:%S.%f')
        except TypeError:
            try:
                # <0.7 compatibility
                result = datetime.datetime.fromtimestamp(float(obj['checked']))
            except TypeError:
                result = None
        obj["checked"] = result
    return obj
