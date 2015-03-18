#!/usr/bin/env python

"""
    TWDLT
    Copyright (C) 2013 Sam Rudge

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from setuptools import setup, find_packages
import sys, os
 
version = '0.2.1'

setup(name='twdlt',
    version=version,
    author='Sam Rudge',
    author_email='sr@gopotato.co.uk',
    packages=['twdlt'],
    include_package_data=False,
    zip_safe=False,
    entry_points="""
    [console_scripts]
    twdlt = twdlt:cli
    """
    )