# -*- coding: utf-8 -*-
import os
import sys
import shutil
import zipfile
import requests
import subprocess
from mast.cli import Cli
from textwrap import dedent
from cStringIO import StringIO
from dulwich import porcelain as git
from mast.timestamp import Timestamp
from mast.logging import make_logger


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


def zipdir(path, filename):
    zipf = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(path):
        for f in files:
            zipf.write(
                os.path.join(root, f),
                os.path.relpath(
                    os.path.join(root, f),
                    os.path.join(path, '..')
                )
            )
    zipf.close()


install_script = '''
import os
import sys
import shutil
import logging
import subprocess

logger = logging.getLogger("hotfix-installation")
handler = logging.FileHandler("install.log")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


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
        "mast.timestamp",
        "mast.xor",
        "commandr",
        "cherrypy",
        "paramiko",
        "Python-Markdown",
        "python-ecdsa",
        "dulwich"
    ]
    dirs = [os.path.abspath(os.path.join(here, d)) for d in dirs]

    # Install Python packages from directories
    for d in dirs:
        msg = "Installing {}".format(d)
        logger.info(msg)
        print msg
        os.chdir(d)
        if d == "dulwich":
            out, err = system_call([python, "setup.py", "--pure", "install", "--force"])
        else:
            out, err = system_call(command)
        logger.debug("out: \\n{}".format(out))
        logger.debug("error: \\n{}".format(err))
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
            print os.path.join(*d[1:])
            dst = os.path.join(mast_home, *d[1:])
            for f in files:
                fqp = os.path.join(dst, f)
                print "Copying file {}".format(fqp)
                print os.path.join(root, f), "->", dst
                shutil.copy(os.path.join(root, f), dst)


    print "hotfix installed"


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
    "https://github.com/mcindi/mast.cli.git",
    "https://github.com/mcindi/mast.config.git",
    "https://github.com/mcindi/mast.cron.git",
    "https://github.com/mcindi/mast.daemon.git",
    "https://github.com/mcindi/mast.datapower.accounts.git",
    "https://github.com/mcindi/mast.datapower.backups.git",
    "https://github.com/mcindi/mast.datapower.datapower.git",
    "https://github.com/mcindi/mast.datapower.deploy.git",
    "https://github.com/mcindi/mast.datapower.deployment.git",
    "https://github.com/mcindi/mast.datapower.developer.git",
    "https://github.com/mcindi/mast.datapower.network.git",
    "https://github.com/mcindi/mast.datapower.ssh.git",
    "https://github.com/mcindi/mast.datapower.status.git",
    "https://github.com/mcindi/mast.datapower.system.git",
    "https://github.com/mcindi/mast.datapower.web.git",
    "https://github.com/mcindi/mast.hashes.git",
    "https://github.com/mcindi/mast.logging.git",
    "https://github.com/mcindi/mast.plugins.git",
    "https://github.com/mcindi/mast.plugin_utils.git",
    "https://github.com/mcindi/mast.pprint.git",
    "https://github.com/mcindi/mast.timestamp.git",
    "https://github.com/mcindi/mast.xor.git",
    "https://github.com/tellapart/commandr.git",
    "https://github.com/cherrypy/cherrypy.git",
    "https://github.com/paramiko/paramiko.git",
    "https://github.com/waylan/Python-Markdown.git",
    "https://github.com/warner/python-ecdsa.git",
    "https://github.com/jelmer/dulwich.git"
]


def main(
        output_file=default_out_file,
        build_dir=default_build_dir,
        install=False,
        remove_build_dir=False):
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
    """
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    if os.listdir(build_dir):
        print "build-dir must be empty"
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
        path = repo.split("/")[-1].replace(".git", "")
        fqp = os.path.abspath(os.path.join(dist_dir, path))
        print "\nCloning {} to {}".format(repo, fqp)
        git.clone(repo, target=path)

    # Get all files
    resp = requests.get(
        "https://github.com/McIndi/mast.installer/archive/master.zip")
    zf = zipfile.ZipFile(StringIO(resp.content))
    zf.extractall()
    shutil.rmtree(
        os.path.join("mast.installer-master",
                     "mast",
                     "installer",
                     "files",
                     "windows"))
    shutil.rmtree(
        os.path.join("mast.installer-master",
                     "mast",
                     "installer",
                     "files",
                     "linux"))
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
    zipdir(dist_dir, output_file)

    # Install the hotfixes if user says so
    if install:
        print "\nInstalling hotfix..."
        os.chdir(dist_dir)
        python = sys.executable
        out, err = system_call([python, "install-hotfix.py"])

        print "Output of installation:\n"
        for line in out.splitlines():
            print "\t", line

        if err:
            print "Errors were encountered during installation:\n"
            for line in err.splitlines():
                print "\t", line
        else:
            print "No Errors were encountered during installation"
        print "See more details in log file: {}".format(os.path.join(
            dist_dir, "install.log"))
    if remove_build_dir:
        shutil.rmtree(build_dir)
    print "\n\nhotfix zip can be found here: {}".format(output_file)


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
