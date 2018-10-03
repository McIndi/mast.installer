# -*- coding: utf-8 -*-
import subprocess
import platform
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
    opener = urllib2.build_opener()
    opener.addheaders = [('User-Agent', '00100')]
    response = opener.open(url)
    with open(dst, 'wb') as fp:
        shutil.copyfileobj(response, fp)


if "Windows" in platform.system():
    # Set Windows parameters here
    if "32bit" in platform.architecture():
        anaconda_installer = "Miniconda2-latest-Windows-x86.exe"
        anaconda_installer_url = "http://repo.continuum.io/miniconda/Miniconda2-latest-Windows-x86.exe"
    elif "64bit" in platform.architecture():
        anaconda_installer = "Miniconda2-latest-Windows-x86_64.exe"
        anaconda_installer_url = "http://repo.continuum.io/miniconda/Miniconda2-latest-Windows-x86_64.exe"
    spec_file = "install.spec.windows"
elif "Linux" in platform.system():
    # Set Linux parameters here
    if '32bit' in platform.architecture():
        anaconda_installer_url = "http://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86.sh"
        anaconda_installer = "Miniconda2-latest-linux32-install.sh"
    elif '64bit' in platform.architecture():
        anaconda_installer_url = "http://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh"
        anaconda_installer = "Miniconda2-latest-linux64-install.sh"
    spec_file = "install.spec.linux"

# Grab the Anaconda installer
dst = os.path.join(
    "scripts",
    "anaconda",
    anaconda_installer)
if not os.path.exists(dst):
    print "Downloading Anaconda installer"
    download_file(
        anaconda_installer_url,
        dst)
    print "\tDone"
else:
    print "Anaconda installer already downloaded, reusing."

# Pyinstaller bahaves strangely if the spec file doesn't end in .spec
print "Renaming spec file"
os.rename(spec_file, "install.spec")
print "\tDone."

# Build the installer executable
print "Building Executable installer"
out, err = system_call(["pyinstaller", "--onefile", "install.spec"])
if not err:
    print "\tExecutable built"
    print "\tOutput of build: {}".format(out)
else:
    print "\tAn Error occurred:"
    print "\nError: {}".format(err)
    print "\nOutput: {}".format(out)

# Rename the spec file to get ready for the next build
print "Renaming spec file"
os.rename("install.spec", spec_file)
print "\tDone."
