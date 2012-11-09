import datetime

from expecter import expect

from cupage.utils import (parse_timedelta, sort_packages)


def test_parse_timedelta():
    expect(parse_timedelta("3h")) == datetime.timedelta(0, 10800)
    expect(parse_timedelta("1d")) == datetime.timedelta(1)
    expect(parse_timedelta("1 d")) == datetime.timedelta(1)
    expect(parse_timedelta("0.5 y")) == datetime.timedelta(182, 43200)
    expect(parse_timedelta("0.5 Y")) == datetime.timedelta(182, 43200)
    with expect.raises(ValueError, "Invalid 'frequency' value"):
        parse_timedelta("1 k")


def test_sort_packages():
    expect(sort_packages(['pkg-0.1.tar.gz', 'pkg-0.2.1.tar.gz', 'pkg-0.2.tar.gz'])) == \
        ['pkg-0.1.tar.gz', 'pkg-0.2.tar.gz', 'pkg-0.2.1.tar.gz']
    expect(sort_packages(['v0.1.0', 'v0.11.0', 'v0.1.2'])) == \
        ['v0.1.0', 'v0.1.2', 'v0.11.0']
