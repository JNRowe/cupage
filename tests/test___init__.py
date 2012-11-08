import re

from cupage import Site


def test_package_re():
    r"""
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
