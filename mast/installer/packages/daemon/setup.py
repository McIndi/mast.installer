import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "daemon",
    version = "2.0.0",
    author = "Sander Marechal",
    description = ("A utility to help create Unix Daemons"),
    license = "GPLv3",
    keywords = "unix linux daemon service",
    url = "http://github.com/mcindi/daemon",
    packages=['daemon'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: GPLv3",
    ],
)
