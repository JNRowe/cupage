import re

from expecter import expect
from nose2.tools import params

from cupage import Site


@params(
    ("test", "tar", ["test-0.1.2.tar.bz2", "test-0.1.2_rc2.tar.gz"],
     'test-[\\d\\.]+(?:[_-](?:pre|rc)[\\d]+)?\\.tar.(?:bz2|gz)'),

    ("test", "zip", ["test-0.1.2-rc2.zip", "test-0.1.2-pre2.zip"],
     'test-[\\d\\.]+(?:[_-](?:pre|rc)[\\d]+)?\\.zip'),
    ("test_long", "gem", ["test_long-0.1.2.gem", ],
     'test_long-[\\d\\.]+(?:[_-](?:pre|rc)[\\d]+)?\\.gem'),
)
def test_package_re(name, ext, pkgs, pattern):
    c = Site.package_re(name, ext)
    for pkg in pkgs:
        expect(re.match(c, pkg).group()) == pkg
    expect(c.pattern) == pattern
