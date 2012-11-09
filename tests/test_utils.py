import datetime

from expecter import expect
from nose2.tools import params

from cupage.utils import (parse_timedelta, sort_packages)


@params(
    ("3h", datetime.timedelta(0, 10800)),
    ("1d", datetime.timedelta(1)),
    ("1 d", datetime.timedelta(1)),
    ("0.5 y", datetime.timedelta(182, 43200)),
    ("0.5 Y", datetime.timedelta(182, 43200)),
)
def test_parse_timedelta(string, dt):
    expect(parse_timedelta(string)) == dt


def test_parse_invalid_timedelta():
    with expect.raises(ValueError, "Invalid 'frequency' value"):
        parse_timedelta("1 k")


@params(
    (['pkg-0.1.tar.gz', 'pkg-0.2.1.tar.gz', 'pkg-0.2.tar.gz'],
     ['pkg-0.1.tar.gz', 'pkg-0.2.tar.gz', 'pkg-0.2.1.tar.gz']),
    (['v0.1.0', 'v0.11.0', 'v0.1.2'], ['v0.1.0', 'v0.1.2', 'v0.11.0']),
)
def test_sort_packages(input, ordered):
    expect(sort_packages(input)) == ordered
