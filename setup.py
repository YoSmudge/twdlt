#!/usr/bin/env python
 
from setuptools import setup, find_packages
import sys, os
 
version = '0.0.1'

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