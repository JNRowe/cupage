#
"""conf - Sphinx configuration information."""
# Copyright © 2011-2014  James Rowe <jnrowe@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
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

import os
import sys
from contextlib import suppress
from subprocess import CalledProcessError, PIPE, run
from typing import Dict, List, Optional, Tuple

root_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, root_dir)

import cupage  # NOQA: E402

on_rtd = 'READTHEDOCS' in os.environ
if not on_rtd:
    import sphinx_rtd_theme

extensions: List[str] = \
    [f'sphinx.ext.{ext}' for ext in ['autodoc', 'coverage', 'doctest',
                                     'intersphinx', 'napoleon', 'viewcode']] \
    + [f'sphinxcontrib.{ext}' for ext in ['blockdiag', ]] \
    + ['sphinx_autodoc_typehints', 'sphinx_click.ext']

if not on_rtd:
    # Only activate spelling if it is installed.  It is not required in the
    # general case and we don’t have the granularity to describe this in a
    # clean way
    try:
        from sphinxcontrib import spelling  # NOQA: F401
    except ImportError:
        pass
    else:
        extensions.append('sphinxcontrib.spelling')

source_suffix = '.rst'

project = 'cupage'
author = 'James Rowe'
copyright = f'2009-2019  {author}'

release = cupage._version.dotted
version = release.rsplit('.', 1)[0]

modindex_common_prefix = [
    'cupage.',
]

rst_epilog = """
.. |CSS| replace:: :abbr:`CSS (Cascading Style Sheets)`
.. |JSON| replace:: :abbr:`JSON (JavaScript Object Notation)`
.. |PyPI| replace:: :abbr:`PyPI (Python Package Index)`
.. |modref| replace:: :mod:`cupage`
"""

modindex_common_prefix = [
    'cupage.',
]

# readthedocs.org handles this setup for their builds, but it is nice to see
# approximately correct builds on the local system too
if not on_rtd:
    html_theme = 'sphinx_rtd_theme'
    html_theme_path: List[str] = [
        sphinx_rtd_theme.get_html_theme_path(),
    ]

pygments_style = 'sphinx'
with suppress(CalledProcessError):
    proc = run(
        ['git', 'log', '--pretty=format:%ad [%h]', '--date=short', '-n1'],
        stdout=PIPE)
    html_last_updated_fmt = proc.stdout.decode()

html_baseurl = 'https://cupage.readthedocs.io/'

man_pages: Tuple[str, str, str, List[str], int] = [('cupage.1', 'cupage',
                                                    'cupage Documentation', [
                                                        'James Rowe',
                                                    ], 1)]

# Autodoc extension settings
autoclass_content = 'init'
autodoc_default_options: Dict[str, Optional[str]] = {
    'members': None,
}

# intersphinx extension settings
intersphinx_mapping: Dict[str, str] = {
    k: (v, os.getenv(f'SPHINX_{k.upper()}_OBJECTS'))
    for k, v in {
        'click': 'https://click.palletsprojects.com/en/7.x/',
        'jnrbase': 'https://jnrbase.readthedocs.io/en/latest/',
        'python': 'https://docs.python.org/3/',
    }.items()
}

# spelling extension settings
spelling_ignore_acronyms = False
spelling_ignore_python_builtins = False
spelling_ignore_importable_modules = False
spelling_lang = 'en_GB'
spelling_word_list_filename = 'wordlist.txt'

# napoleon extension settings
napoleon_numpy_docstring = False
