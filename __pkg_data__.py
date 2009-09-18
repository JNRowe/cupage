#
# vim: set sw=4 sts=4 et tw=80 fileencoding=utf-8:
#
"""Per-package configuration data"""
# Copyright (C) 2008  James Rowe
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

import sys

import libcupage
MODULE = libcupage

SCRIPTS = [cupage, ]

DESCRIPTION = MODULE.__doc__.splitlines()[0][:-1]
LONG_DESCRIPTION = "\n\n".join(MODULE.__doc__.split("\n\n")[1:2])

KEYWORDS = ["admin", "update", "web"]
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Other Audience",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.4",
    "Programming Language :: Python :: 2.5",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.1",
    "Topic :: Internet",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
    "Topic :: Internet :: WWW/HTTP :: Site Management",
    "Topic :: Internet :: WWW/HTTP :: Site Management :: Link Checking",
    "Topic :: Other/Nonlisted Topic",
    "Topic :: Text Processing",
    "Topic :: Text Processing :: Markup :: HTML",
    "Topic :: Text Processing :: Markup :: XML",
    "Topic :: Utilities",
]

OBSOLETES = []

GRAPH_TYPE = None

TEST_EXTRAGLOBS = {}

SCM = "git"

