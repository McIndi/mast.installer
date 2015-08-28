# -*- coding: utf-8 -*-
import subprocess
import urllib2
import shutil
import os

def system_call(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=False):
    """
    # system_call

    helper function to shell out commands. This should be platform
    agnostic.
    """
    stderr = subprocess.STDOUT
    pipe = subprocess.Popen(
        command,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        shell=shell)
    stdout, stderr = pipe.communicate()
    return stdout, stderr


def download_file(url, dst):
    """helper function to stream a file from url to dst"""
    req = urllib2.urlopen(url)
    with open(dst, 'wb') as fp:
        shutil.copyfileobj(req, fp)


# Grab the Anaconda installer
dst = os.path.join(
    "scripts",
    "anaconda",
    "Anaconda-2.3.0-Windows-x86_64.exe")
download_file(
    "https://3230d63b5fc54e62148e-c95ac804525aac4b6dba79b00b39d1d3"
    ".ssl.cf1.rackcdn.com/Anaconda-2.3.0-Windows-x86_64.exe",
    dst)

# Pyinstaller bahaves strangely if the spec file doesn't end in .spec
os.rename("install.spec.windows", "install.spec")

# Build the installer executable
out, err = system_call(["pyinstaller", "--onefile", "install.spec"])
