#
"""test___init__ - Tests for cupage package."""
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

import re

from pytest import mark

from cupage import Site


@mark.parametrize('name, ext, pkgs, pattern', [
    ('test', 'tar', [
        'test-0.1.2.tar.bz2', 'test-0.1.2_rc2.tar.gz', 'test-0.1.2.tar.xz'
    ], 'test-[\\d\\.]+(?:[_-](?:pre|rc)[\\d]+)?\\.tar.(?:bz2|gz|xz)'),
    ('test', 'zip', ['test-0.1.2-rc2.zip', 'test-0.1.2-pre2.zip'
                     ], 'test-[\\d\\.]+(?:[_-](?:pre|rc)[\\d]+)?\\.zip'),
    ('test_long', 'gem', [
        'test_long-0.1.2.gem',
    ], 'test_long-[\\d\\.]+(?:[_-](?:pre|rc)[\\d]+)?\\.gem'),
])
def test_package_re(name, ext, pkgs, pattern):
    """Test file matching functionality."""
    c = Site.package_re(name, ext)
    for pkg in pkgs:
        assert re.match(c, pkg).group() == pkg
    assert c.pattern == pattern
