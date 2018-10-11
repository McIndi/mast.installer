# -*- coding: utf-8 -*-
import subprocess
import platform
import urllib2
import shutil
import sys
import os
from resources import (
    pip_dependencies,
    conda_dependencies,
)

def system_call(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True):
    """
    # system_call

    helper function to shell out commands. This should be platform
    agnostic.
    """
    print("\n### {}".format(command))
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
    print("downloading {} -> {}".format(url, dst))
    opener = urllib2.build_opener()
    opener.addheaders = [('User-Agent', '00100')]
    response = opener.open(url)
    with open(dst, 'wb') as fp:
        shutil.copyfileobj(response, fp)


if "Windows" in platform.system():
    # Set Windows parameters here
    if "32bit" in platform.architecture():
        miniconda_installer = "Miniconda2-latest-Windows-x86.exe"
        miniconda_installer_url = "https://repo.continuum.io/miniconda/Miniconda2-latest-Windows-x86.exe"
    elif "64bit" in platform.architecture():
        miniconda_installer = "Miniconda2-latest-Windows-x86_64.exe"
        miniconda_installer_url = "https://repo.continuum.io/miniconda/Miniconda2-latest-Windows-x86_64.exe"
    spec_file = "install.spec.windows"
elif "Linux" in platform.system():
    # Set Linux parameters here
    if '32bit' in platform.architecture():
        miniconda_installer_url = "https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86.sh"
        miniconda_installer = "Miniconda2-latest-linux32-install.sh"
    elif '64bit' in platform.architecture():
        miniconda_installer_url = "https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh"
        miniconda_installer = "Miniconda2-latest-linux64-install.sh"
    spec_file = "install.spec.linux"

# Grab the miniconda installer
dst = os.path.join(
    "scripts",
    "miniconda",
    miniconda_installer
)
if not os.path.exists(dst):
    print "Downloading miniconda installer"
    download_file(
        miniconda_installer_url,
        dst
    )
    print "\tDone"
else:
    print "miniconda installer already downloaded, reusing."

# ensure up-to-date conda and pip
system_call(
    " ".join([
        sys.executable,
        "-m",
        "conda",
        "update",
        "conda",
        "--yes",
    ]),
    stdout=sys.stdout,
    stderr=sys.stderr,
)
system_call(
    " ".join([
        sys.executable,
        "-m",
        "pip",
        "install",
        "--upgrade",
        "pip",
    ]),
    stdout=sys.stdout,
    stderr=sys.stderr,
)


# Download packages
for dependency, url in conda_dependencies[platform.system()][platform.architecture()[0]].items():
    dst = os.path.join(
        "packages",
        url.split("/")[-1]
    )
    download_file(url, dst)
for dependency in pip_dependencies:
    system_call(
        " ".join([
            sys.executable,
            "-m",
            "pip",
            "download",
            "--exists-action",
            "i",
            "--dest",
            "packages",
            '"{}"'.format(dependency)
        ]),
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
# Pyinstaller bahaves strangely if the spec file doesn't end in .spec
print "Renaming spec file"
os.rename(spec_file, "install.spec")
print "\tDone."

# Build the installer executable
print "Building Executable installer"
system_call(
    " ".join(["pyinstaller", "--onefile", "install.spec"]),
    stdout=sys.stdout,
    stderr=sys.stderr,
)

# Rename the spec file to get ready for the next build
print "Renaming spec file"
os.rename("install.spec", spec_file)
print "\tDone."
