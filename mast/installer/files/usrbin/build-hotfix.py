# -*- coding: utf-8 -*-
"""
(c) McIndi Solutions LLC 2015

build-hotfix.py

Build a hotfix containing the latest updates to MAST for IBM DataPower.

After running this script, you will have a zip file (as defined by the
--out-file option which defaults to $MAST_HOME/tmp/hotfix.zip). To install
this hotfix, perform the following steps:

1. Unzip the file anywhere
2. Navigate to the directory which was extracted from the zip file
3. Execute the relevant command for your operating system:

__Windows__

`C:\path\to\hotfix> <MAST_HOME>\anaconda\python install-hotfix.py`

__Linux__

`$ <MAST_HOME>/anaconda/bin/python install-hotfix.py`

__NOTE__: If mastd is running on your host, you must restart it

# Troubleshooting

This hotfix should install without incident. If there are any issues,
please copy and paste the error you receive into an email to
mastsupport@mcindi.com


"""
import os
import sys
import zipfile
import subprocess
from mast.cli import Cli
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
        "mast.xor"
    ]
    dirs = [os.path.abspath(os.path.join(here, d)) for d in dirs]
    for d in dirs:
        msg = "Installing {}".format(d)
        logger.info(msg)
        print msg
        os.chdir(d)
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
    "https://github.com/mcindi/mast.xor.git"
]


def main(
        output_file=default_out_file,
        build_dir=default_build_dir,
        install=False):
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
        git.clone(repo, target=path)
    os.chdir(cwd)

    # zip up txhe dist_dir
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
    print "\n\nhotfix zip can be found here: {}".format(output_file)

if __name__ == "__main__":
    try:
        cli = Cli(main=main)
        cli.run()
    except SystemExit:
        pass
    except:
        make_logger("error").exception(
            "An unhandled exception occurred during execution")
        raise
