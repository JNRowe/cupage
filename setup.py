#! /usr/bin/python -tt

from setuptools import setup

# Hack to import _version file without importing cupage/__init__.py, its
# purpose is to allow import without requiring dependencies at this point.
_version = {}
execfile('cupage/_version.py', {}, _version)

install_requires = map(str.strip, open('extra/requirements.txt').readlines())


setup(
    name='cupage',
    version=_version['dotted'],
    description='A tool to check for updates on web pages',
    long_description=open("README.rst").read(),
    author="James Rowe",
    author_email="jnrowe@gmail.com",
    url="https://github.com/JNRowe/cupage",
    license="GPL-3",
    keywords="admin update web",
    packages=['cupage', ],
    entry_points={'console_scripts': ['cupage = cupage.commandline:main', ]},
    install_requires=install_requires,
    zip_safe=False,
    test_suite="nose.collector",
    tests_require=['nose', ],
    classifiers=[
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
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
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
    ],
)
