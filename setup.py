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
    name = "galah-updater",
    version = read("VERSION").strip(),
    author = "Galah Group LLC and other contributers",
    author_email = "john@galahgroup.com",
    description = "A package manager for Galah.",
    license = "Apache v2.0",
    keywords = "galah",
    url = "https://www.github.com/galah-group/galah-updater",
    packages = find_packages(),
    namespace_packages = ["galah", "galah.test"],
    long_description = read("README.rst"),
    install_requires = [
        "PyYAML==3.10",
        "PyCrypto==2.6"
    ],
    classifiers = [
        "License :: OSI Approved :: Apache Software License",
    ]
)
