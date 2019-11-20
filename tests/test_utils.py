#
"""test_utils - Tests for cupage utils."""
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

from pytest import mark, raises

from cupage.utils import (charset_from_headers, parse_timedelta, sort_packages)


@mark.parametrize('string, dt', [
    ('3h', datetime.timedelta(0, 10800)),
    ('1d', datetime.timedelta(1)),
    ('1 d', datetime.timedelta(1)),
    ('0.5 y', datetime.timedelta(182, 43200)),
    ('0.5 Y', datetime.timedelta(182, 43200)),
])
def test_parse_timedelta(string, dt):
    """Test timedelta parsing functionality."""
    assert parse_timedelta(string) == dt


def test_parse_invalid_timedelta():
    """Test timedelta parsing error handling."""
    with raises(ValueError, match="Invalid 'frequency' value"):
        parse_timedelta('1 k')


@mark.parametrize('input, ordered', [
    (['pkg-0.1.tar.gz', 'pkg-0.2.1.tar.gz', 'pkg-0.2.tar.gz'],
     ['pkg-0.1.tar.gz', 'pkg-0.2.tar.gz', 'pkg-0.2.1.tar.gz']),
    (['v0.1.0', 'v0.11.0', 'v0.1.2'], ['v0.1.0', 'v0.1.2', 'v0.11.0']),
])
def test_sort_packages(input, ordered):
    """Test package sorting functionality."""
    assert sort_packages(input) == ordered


@mark.parametrize('headers, charset', [
    ({}, 'iso-8859-1'),
    ({'content-type': 'text/html; charset=utf-8'}, 'utf-8'),
    ({'content-type': 'text/html; charset=ISO-8859-1'}, 'ISO-8859-1'),
])
def test_charset_header(headers, charset):
    """Test character set header functionality."""
    assert charset_from_headers(headers) == charset
