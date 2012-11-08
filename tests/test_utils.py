from cupage.utils import (parse_timedelta, sort_packages)


def test_parse_timedelta():
    """
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


def test_sort_packages():
    """
    >>> sort_packages(['pkg-0.1.tar.gz', 'pkg-0.2.1.tar.gz', 'pkg-0.2.tar.gz'])
    ['pkg-0.1.tar.gz', 'pkg-0.2.tar.gz', 'pkg-0.2.1.tar.gz']
    >>> sort_packages(['v0.1.0', 'v0.11.0', 'v0.1.2'])
    ['v0.1.0', 'v0.1.2', 'v0.11.0']
    """
