#
# coding=utf-8
"""test_utils - Tests for cupage utils"""
# Copyright © 2012  James Rowe <jnrowe@gmail.com>
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

from expecter import expect
from nose2.tools import params

from cupage.utils import (charset_from_headers, parse_timedelta, sort_packages)


@params(
    ('3h', datetime.timedelta(0, 10800)),
    ('1d', datetime.timedelta(1)),
    ('1 d', datetime.timedelta(1)),
    ('0.5 y', datetime.timedelta(182, 43200)),
    ('0.5 Y', datetime.timedelta(182, 43200)),
)
def test_parse_timedelta(string, dt):
    expect(parse_timedelta(string)) == dt


def test_parse_invalid_timedelta():
    with expect.raises(ValueError, "Invalid 'frequency' value"):
        parse_timedelta('1 k')


@params(
    (['pkg-0.1.tar.gz', 'pkg-0.2.1.tar.gz', 'pkg-0.2.tar.gz'],
     ['pkg-0.1.tar.gz', 'pkg-0.2.tar.gz', 'pkg-0.2.1.tar.gz']),
    (['v0.1.0', 'v0.11.0', 'v0.1.2'], ['v0.1.0', 'v0.1.2', 'v0.11.0']),
)
def test_sort_packages(input, ordered):
    expect(sort_packages(input)) == ordered


@params(
    ({}, 'iso-8859-1'),
    ({'content-type': 'text/html; charset=utf-8'}, 'utf-8'),
    ({'content-type': 'text/html; charset=ISO-8859-1'}, 'ISO-8859-1'),
)
def test_charset_header(headers, charset):
    expect(charset_from_headers(headers)) == charset
