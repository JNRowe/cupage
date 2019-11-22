#
"""utils - Utility functions for cupage."""
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

import os
import re
import socket
import sys
from urllib import robotparser
import urllib.parse as urlparse

import httplib2
from jnrbase import colourise

try:
    # httplib2 0.8 and above support setting certs via ca_certs_locater module,
    # making this dirty mess even dirtier
    if [int(i) for i in httplib2.__version__.split('.')] < [0, 8]:
        raise ImportError('no ca_certs_locater support')
    import ca_certs_locater
except (AssertionError, ImportError):
    _HTTPLIB2_BUNDLE = os.path.realpath(os.path.dirname(httplib2.CA_CERTS))
    SYSTEM_CERTS = \
        not _HTTPLIB2_BUNDLE.startswith(os.path.dirname(httplib2.__file__))
    CA_CERTS = None
    if not SYSTEM_CERTS and sys.platform.startswith('linux'):
        for cert_file in [
                '/etc/ssl/certs/ca-certificates.crt',
                '/etc/pki/tls/certs/ca-bundle.crt'
        ]:
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
else:
    CA_CERTS = ca_certs_locater.get()


def sort_packages(packages):
    """Order package list according to version number.

    Args:
        packages (list): Packages to sort
    """
    # Very ugly key function, but it handles the common case of varying
    # component length just about “Good Enough™”
    return sorted(packages,
                  key=lambda s: [i for i in s if i.isdigit() or i == '.'])


def robots_test(http, url, name, user_agent='*'):
    """Check whether a given URL is blocked by ``robots.txt``.

    Args:
        http (httplib2.Http): Object to use for requests
        url (str): URL to check
        name (str): Site name being checked
        user_agent (str): User agent to check in :file:`robots.txt`
    """
    parsed = urlparse.urlparse(url, 'http')
    if parsed.scheme.startswith('http'):
        robots_url = '{[scheme]}://{[netloc]}/robots.txt'.format(
            parsed._asdict())
        robots = robotparser.RobotFileParser(robots_url)
        try:
            headers, content = http.request(robots_url)
        except httplib2.ServerNotFoundError:
            colourise.pfail(f'Domain name lookup failed for {name}')
            return False
        except socket.timeout:
            colourise.pfail(f'Socket timed out on {name}')
            return False
        # Ignore errors 4xx errors for robots.txt
        if not str(headers.status).startswith('4'):
            robots.parse(content.splitlines())
            if not robots.can_fetch(user_agent, url):
                colourise.pfail(f'Can’t check {name}, blocked by robots.txt')
                return False


def term_link(__target, name=None):
    """Generate a terminal hyperlink.

    See https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda.

    Args:
        __target (str): Hyperlink target
        name (str): Target name

    Returns:
        str: Formatted hyperlink for terminal output
    """
    if not name:
        name = os.path.basename(__target)
    return f'\033]8;;{__target}\007{name}\033]8;;\007'


def charset_from_headers(headers):
    """Parse charset from headers.

    Args:
        headers (httplib2.Response): Request headers

    Returns:
        Defined encoding, or default to ISO-8859-1
    """
    match = re.search('charset=([^ ;]+)', headers.get('content-type', ''))
    if match:
        charset = match.groups()[0]
    else:
        charset = 'iso-8859-1'
    return charset
