#!/usr/bin/env python

import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "galah-installer",
    version = read("VERSION").strip(),
    author = "Galah Group LLC and other contributers",
    author_email = "john@galahgroup.com",
    description = "A tool for installing and maintaining Galah.",
    license = "Apache v2.0",
    keywords = "galah",
    url = "https://www.github.com/galah-group/galah-installer",
    packages = None,
    long_description = read("README.rst"),
    entry_points = {
        "console_scripts": [
            "galah-installer = installer.main:main"
        ]
    },
    install_requires = [
        "PyYAML==3.10"
    ],
    classifiers = [
        "License :: OSI Approved :: Apache Software License",
    ]
)
