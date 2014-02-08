#! /usr/bin/env python
# coding=utf-8
"""setup.py - Build and installation support"""
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

import imp

from sys import version_info

from setuptools import setup

# Hack to import _version file without importing cupage/__init__.py, its
# purpose is to allow import without requiring dependencies at this point.
ver_file = open('cupage/_version.py')
_version = imp.load_module('_version', ver_file, ver_file.name,
                           ('.py', ver_file.mode, imp.PY_SOURCE))

def parse_requires(file):
    deps = []
    req_file = open('extra/%s' % file)
    entries = map(str.strip, req_file.readlines())
    for dep in entries:
        if dep.startswith('-r '):
            deps.extend(parse_requires(dep.split()[1]))
        else:
            deps.append(dep)
    return deps

install_requires = parse_requires('requirements-py%s%s.txt' % version_info[:2])

setup(
    name='cupage',
    version=_version.dotted,
    description='A tool to check for updates on web pages',
    long_description=open('README.rst').read(),
    author='James Rowe',
    author_email='jnrowe@gmail.com',
    url='https://github.com/JNRowe/cupage',
    license='GPL-3',
    keywords='admin update web',
    packages=['cupage', ],
    entry_points={'console_scripts': ['cupage = cupage.cmdline:main', ]},
    install_requires=install_requires,
    zip_safe=False,
    tests_require=['nose2', 'expecter'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Other Audience',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Internet :: WWW/HTTP :: Site Management :: Link Checking',
        'Topic :: Other/Nonlisted Topic',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Markup :: XML',
        'Topic :: Utilities',
    ],
)
