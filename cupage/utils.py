#
"""utils - Utility functions for cupage"""
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

import datetime
import json
import os
import re
import socket
import sys
from contextlib import suppress
from urllib import robotparser
import urllib.parse as urlparse

import blessings
import httplib2


T = blessings.Terminal()


try:
    # httplib2 0.8 and above support setting certs via ca_certs_locater module,
    # making this dirty mess even dirtier
    assert [int(i) for i in httplib2.__version__.split('.')] >= [0, 8]
    import ca_certs_locater
except (AssertionError, ImportError):
    _HTTPLIB2_BUNDLE = os.path.realpath(os.path.dirname(httplib2.CA_CERTS))
    SYSTEM_CERTS = \
        not _HTTPLIB2_BUNDLE.startswith(os.path.dirname(httplib2.__file__))
    CA_CERTS = None
    CURL_CERTS = False
    if not SYSTEM_CERTS and sys.platform.startswith('linux'):
        for cert_file in ['/etc/ssl/certs/ca-certificates.crt',
                          '/etc/pki/tls/certs/ca-bundle.crt']:
            if os.path.exists(cert_file):
                CA_CERTS = cert_file
                SYSTEM_CERTS = True
                break
    elif not SYSTEM_CERTS and sys.platform.startswith('freebsd'):
        if os.path.exists('/usr/local/share/certs/ca-root-nss.crt'):
            CA_CERTS = '/usr/local/share/certs/ca-root-nss.crt'
            SYSTEM_CERTS = True
    elif os.path.exists(os.getenv('CURL_CA_BUNDLE', '')):
        CA_CERTS = os.getenv('CURL_CA_BUNDLE')
        CURL_CERTS = True
else:
    CA_CERTS = ca_certs_locater.get()


def parse_timedelta(delta):
    """Parse human readable frequency.

    :param str delta: Frequency to parse
    """
    match = re.match('^(\d+(?:|\.\d+)) *([hdwmy])$', delta, re.IGNORECASE)
    if not match:
        raise ValueError("Invalid 'frequency' value")
    value, units = match.groups()
    units = 'hdwmy'.index(units.lower())
    # hours per hour/day/week/month/year
    multiplier = (1, 24, 168, 672, 8760)
    return datetime.timedelta(hours=float(value) * multiplier[units])


def sort_packages(packages):
    """Order package list according to version number.

    :param list packages: Packages to sort
    """
    # Very ugly key function, but it handles the common case of varying
    # component length just about “Good Enough™”
    return sorted(packages,
                  key=lambda s: [i for i in s if i.isdigit() or i == '.'])


def robots_test(http, url, name, user_agent='*'):
    """Check whether a given URL is blocked by ``robots.txt``.

    :param http: :class:`httplib2.Http` object to use for requests
    :param str url: URL to check
    :param name: Site name being checked
    :param str user_agent: User agent to check in :file:`robots.txt`
    """
    parsed = urlparse.urlparse(url, 'http')
    if parsed.scheme.startswith('http'):
        robots_url = '{[scheme]}://{[netloc]}/robots.txt'.format(
            parsed._asdict())
        robots = robotparser.RobotFileParser(robots_url)
        try:
            headers, content = http.request(robots_url)
        except httplib2.ServerNotFoundError:
            print(fail(f'Domain name lookup failed for {name}'))
            return False
        except socket.timeout:
            print(fail(f'Socket timed out on {name}'))
            return False
        # Ignore errors 4xx errors for robots.txt
        if not str(headers.status).startswith('4'):
            robots.parse(content.splitlines())
            if not robots.can_fetch(user_agent, url):
                print(fail(f'Can’t check {name}, blocked by robots.txt'))
                return False


def _format_info(text, colour):
    return ' '.join([getattr(T, f'bold_white_on_{colour}')('*'),
                     getattr(T, f'bright_{colour}')(text)])


def success(text):
    """Format a success message with colour, if possible.

    :param str text: Text to format
    """
    return _format_info(text, 'green')


def fail(text):
    """Format a failure message with colour, if possible.

    :param str text: Text to format
    """
    return _format_info(text, 'red')


def warn(text):
    """Format a warning message with colour, if possible.

    :param str text: Text to format
    """
    return _format_info(text, 'yellow')


class CupageEncoder(json.JSONEncoder):

    """Custom JSON encoding for supporting ``datetime`` objects."""

    def default(self, obj):
        """Handle ``datetime`` objects when encoding as JSON.

        This simply falls through to :meth:`~json.JSONEncoder.default` if
        ``obj`` has no ``isoformat`` method.

        :param obj: Object to encode
        """
        with suppress(TypeError):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def json_to_datetime(obj):
    """Parse ``checked`` datetimes from ``cupage`` databases.

    :see: `json.JSONDecoder`

    :param obj: Object to decode
    """
    if 'checked' in obj:
        try:
            result = datetime.datetime.strptime(obj['checked'],
                                                '%Y-%m-%dT%H:%M:%S.%f')
        except TypeError:
            try:
                # <0.7 compatibility
                result = datetime.datetime.fromtimestamp(float(obj['checked']))
            except TypeError:
                result = None
        obj['checked'] = result
    return obj


def charset_from_headers(headers):
    """Parse charset from headers.

    :param httplib2.Response headers: Request headers
    :return: Defined encoding, or default to ISO-8859-1
    """
    match = re.search("charset=([^ ;]+)", headers.get('content-type', ""))
    if match:
        charset = match.groups()[0]
    else:
        charset = "iso-8859-1"
    return charset
