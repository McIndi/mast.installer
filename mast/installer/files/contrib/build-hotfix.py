# -*- coding: utf-8 -*-
import os
import sys
import socket
import shutil
import zipfile
import urllib.request, urllib.error, urllib.parse
import requests
import subprocess
from time import sleep
from mast.cli import Cli
from textwrap import dedent
from io import StringIO
from shutil import make_archive
from mast.timestamp import Timestamp
from mast.logging import make_logger

__version__ = "{}-0".format(os.environ["MAST_VERSION"])

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


install_script = r'''
import os
import sys
import shutil
import logging
import platform
import subprocess

logger = logging.getLogger("hotfix-installation")
handler = logging.FileHandler("install.log")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


def render_template(string, mappings):
    for k, v in mappings.items():
        string = string.replace("<%{}%>".format(k), v)
    return string


def render_template_file(fname, mappings):
    with open(fname, "r") as fin:
        ret = render_template(fin.read(), mappings)
    return ret


def write_file(dst, content):
    with open(dst, "w") as fout:
        fout.write(content)


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


def main():
    here = os.getcwd()
    python = os.path.abspath(sys.executable)
    mast_home = os.path.abspath(os.path.join(sys.prefix, os.path.pardir))
    command = [python, "setup.py", "install", "--force"]
    dirs = [
        "mast.cli",
        "mast.config",
        "mast.cron",
        "mast.daemon",
        "mast.datapower.accounts",
        "mast.datapower.backups",
        "mast.datapower.crypto",
        "mast.datapower.datapower",
        "mast.datapower.deploy",
        "mast.datapower.deployment",
        "mast.datapower.developer",
        "mast.datapower.network",
        "mast.datapower.ssh",
        "mast.datapower.status",
        "mast.datapower.system",
        "mast.datapower.web",
        "mast.hashes",
        "mast.logging",
        "mast.plugins",
        "mast.plugin_utils",
        "mast.pprint",
        "mast.test",
        "mast.testsuite",
        "mast.timestamp",
        "mast.xor",
        "commandr",
        "cherrypy",
        "paramiko",
        "markdown",
        "python-ecdsa",
        "dulwich",
    ]
    dirs = [os.path.abspath(os.path.join(here, d)) for d in dirs]

    # Install Python packages from directories
    for d in dirs:
        msg = "Installing {}".format(d)
        logger.info(msg)
        print msg
        os.chdir(d)
        if "dulwich" in d:
            out, err = system_call([python, "setup.py", "--pure", "install", "--force"])
        else:
            out, err = system_call(command)
        logger.debug("out: {}".format(out))
        logger.debug("error: {}".format(err))
        if err:
            print
            print "An Error occurred while installing hotfix"
            print "Error is below, please contact mastsupport@mcindi.com"
            print "with below error"
            print
            print err
            sys.exit(-1)
    os.chdir(here)
    os.chdir("files")
    for root, dirs, files in os.walk("."):
        if root is not ".":
            d = root.split(os.path.sep)
            if d[-1] == "windows":
                if "Windows" in platform.system():
                    for f in files:
                        dst = os.path.join(mast_home, f)
                        src = os.path.join(root, f)
                        content = render_template_file(src, {"MAST_HOME": mast_home})
                        write_file(dst, content)
            elif d[-1] == "linux":
                if "Linux" in platform.system():
                    for f in files:
                        dst = os.path.join(mast_home, f)
                        src = os.path.join(root, f)
                        content = render_template_file(src, {"MAST_HOME": mast_home})
                        write_file(dst, content)
                        os.chmod(dst, 0755)
            else:
                dst = os.path.join(mast_home, *d[1:])
                for directory in dirs:
                    dst_dir = os.path.join(dst, directory)
                    if not os.path.exists(dst_dir):
                        os.mkdir(dst_dir)
                for f in files:
                    print os.path.join(root, f), "->", dst
                    shutil.copy(os.path.join(root, f), dst)

    print "\n\nhotfix installed"
    print "\nTo re-generate the latest documentation, please run"
    print "\t{}mast contrib/gendocs.py".format(mast_home + os.path.sep)

if __name__ == "__main__":
    main()
'''

now = Timestamp().timestamp
mast_home = os.environ["MAST_HOME"]

default_out_file = os.path.join(
    mast_home,
    "tmp",
    "hotfix.{}.zip".format(now))

default_build_dir = os.path.join(
    mast_home,
    "tmp",
    "{}-hotfix-build".format(now))

repos = [
    "https://github.com/McIndi/mast.cli/archive/master.zip",
    "https://github.com/McIndi/mast.config/archive/master.zip",
    "https://github.com/McIndi/mast.cron/archive/master.zip",
    "https://github.com/McIndi/mast.daemon/archive/master.zip",
    "https://github.com/McIndi/mast.datapower.accounts/archive/master.zip",
    "https://github.com/McIndi/mast.datapower.backups/archive/master.zip",
    "https://github.com/McIndi/mast.datapower.crypto/archive/master.zip",
    "https://github.com/McIndi/mast.datapower.datapower/archive/master.zip",
    "https://github.com/McIndi/mast.datapower.deploy/archive/master.zip",
    "https://github.com/McIndi/mast.datapower.deployment/archive/master.zip",
    "https://github.com/McIndi/mast.datapower.developer/archive/master.zip",
    "https://github.com/McIndi/mast.datapower.network/archive/master.zip",
    "https://github.com/McIndi/mast.datapower.ssh/archive/master.zip",
    "https://github.com/McIndi/mast.datapower.status/archive/master.zip",
    "https://github.com/mcindi/mast.datapower.system/archive/master.zip",
    "https://github.com/mcindi/mast.datapower.web/archive/master.zip",
    "https://github.com/mcindi/mast.hashes/archive/master.zip",
    "https://github.com/mcindi/mast.logging/archive/master.zip",
    "https://github.com/mcindi/mast.plugins/archive/master.zip",
    "https://github.com/mcindi/mast.plugin_utils/archive/master.zip",
    "https://github.com/mcindi/mast.pprint/archive/master.zip",
    "https://github.com/McIndi/mast.test/archive/master.zip",
    "https://github.com/McIndi/mast.testsuite/archive/master.zip",
    "https://github.com/mcindi/mast.timestamp/archive/master.zip",
    "https://github.com/mcindi/mast.xor/archive/master.zip",
    "https://github.com/tellapart/commandr/archive/master.zip",
    "https://github.com/cherrypy/cherrypy/archive/master.zip",
    "https://github.com/paramiko/paramiko/archive/master.zip",
    "https://github.com/waylan/Python-Markdown/archive/master.zip",
    "https://github.com/warner/python-ecdsa/archive/master.zip",
    "https://github.com/jelmer/dulwich/archive/master.zip"
]


def main(
        output_file=default_out_file,
        build_dir=default_build_dir,
        no_verify=False,
        install=False,
        remove_build_dir=False,
        timeout=60):
    r"""
    Build a hotfix containing the latest updates to MAST for IBM DataPower.

    After running this script, you will have a zip file (as defined by the
    --out-file option which defaults to $MAST_HOME/tmp/hotfix.zip). To install
    this hotfix, perform the following steps:

        1. Unzip the file anywhere
        2. Navigate to the directory which was extracted from the zip file
        3. Execute the relevant command for your operating system:

        Windows

        `C:\path\to\hotfix> <MAST_HOME>\anaconda\python install-hotfix.py`

        Linux

        `$ <MAST_HOME>/anaconda/bin/python install-hotfix.py`

        NOTE: If mastd is running on your host, you must restart it

        Troubleshooting

        This hotfix should install without incident. If there are any issues,
        please copy and paste the error you receive into an email to
        mastsupport@mcindi.com

    Options:

    output_file - The path and name of the zip file to output

    build_dir - The directory in which to build the hotfix.
    It will be created if it doesn't exist, and it must be empty.

    install - If specified, the hotfix will be installed in your
    local MAST installation.

    remove_build_dir - If specified, the build_dir will be removed
    upon completion. WARNING: If specified along with install, your
    install.log will be removed as well

    timeout - The number of seconds to wait for the server to respond
    """
    output_file = output_file.replace(".zip", "")
    verify = not no_verify
    socket.setdefaulttimeout(timeout)

    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    if os.listdir(build_dir):
        print("build-dir must be empty")
        sys.exit(1)
    # Create a directory to store the hotfix
    dist_dir = os.path.join(build_dir, "hotfix-{}".format(now))
    os.mkdir(dist_dir)

    # Write out the install script
    fname = os.path.join(dist_dir, "install-hotfix.py")
    with open(fname, "w") as fout:
        fout.write(install_script)

    # change directory to build_dir and clone all the repos
    cwd = os.getcwd()
    os.chdir(dist_dir)
    for repo in repos:
        print(repo)
        resp = requests.get(repo, verify=verify)
        zf = zipfile.ZipFile(StringIO(resp.content))
        zf.extractall()
        for item in zf.infolist():
            try:
                print("\t", item.filename)
            except UnicodeEncodeError:
                print("\t<UNABLE TO DISPLAY FILENAME>")

    # Rename directories
    _dirs = os.listdir(".")
    _dirs = [x for x in _dirs if "-master" in x]
    for directory in _dirs:
        os.rename(directory, directory.replace("-master", ""))

    # Get all files
    resp = requests.get(
        "https://github.com/McIndi/mast.installer/archive/master.zip",
        verify=verify)
    zf = zipfile.ZipFile(StringIO(resp.content))
    zf.extractall()

    shutil.copytree(
        os.path.join(
            "mast.installer-master",
            "mast",
            "installer",
            "files"),
        "files")
    shutil.rmtree("mast.installer-master")

    # Get out of build_dir so we can zip it up
    os.chdir(cwd)

    # zip up the dist_dir
    output_file = make_archive(output_file, "zip", dist_dir)

    # Install the hotfixes if user says so
    if install:
        print("\nInstalling hotfix...")
        os.chdir(dist_dir)
        python = sys.executable
        out, err = system_call([python, "install-hotfix.py"])

        print("Output of installation:\n")
        for line in out.splitlines():
            print("\t", line)

        if err:
            print("Errors were encountered during installation:\n")
            for line in err.splitlines():
                print("\t", line)
        else:
            print("No Errors were encountered during installation")
        print("See more details in log file: {}".format(os.path.join(
            dist_dir, "install.log")))
    if remove_build_dir:
        # Get out of build_dir so we can zip it up
        os.chdir(cwd)
        shutil.rmtree(build_dir)
    print("\n\nhotfix zip can be found here: {}".format(output_file))


if __name__ == "__main__":
    try:
        cli = Cli(main=main, description=dedent(main.__doc__))
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception(
            "An unhandled exception occurred during execution")
        raise
