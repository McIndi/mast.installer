#!/usr/bin/env python
import cli
import os
import sys
import subprocess
import shutil
import logging
import platform
from tstamp import Timestamp

cwd = sys._MEIPASS

if "Windows" in platform.system():
    ANACONDA_INSTALL_SCRIPT = os.path.join(
        cwd,
        "scripts",
        "anaconda",
        "Anaconda-2.4.0-Windows-x86_64.exe")
elif "Linux" in platform.system():
    if '32bit' in platform.architecture():
        ANACONDA_INSTALL_SCRIPT = os.path.join(
            cwd,
            "scripts",
            "anaconda",
            "anaconda-2.4.0-linux32-install.sh")
    elif '64bit' in platform.architecture():
        ANACONDA_INSTALL_SCRIPT = os.path.join(
            cwd,
            "scripts",
            "anaconda",
            "anaconda-2.4.0-linux64-install.sh")

INSTALL_DIR = cwd

# TODO: Move some of the logging options to the command line
t = Timestamp()
logging.basicConfig(
    filename="{}-mast-install.log".format(t.timestamp),
    filemode="w",
    format="level=%(levelname)s; datetime=%(asctime)s; "
           "process_name=%(processName)s; pid=%(process)d; "
           "thread=%(thread)d; module=%(module)s; "
           "function=%(funcName)s; line=%(lineno)d; message=%(message)s")
logger = logging.getLogger("mast.installer")
logger.setLevel(10)


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


# TODO: Move some options to the command line.
def _install_anaconda(prefix):
    """
    install_anaconda

    This will issue the command to install Anaconda into the specified
    directory.
    """
    prefix = os.path.join(os.path.realpath(prefix), "anaconda")
    if "Windows" in platform.system():
        command = [
            ANACONDA_INSTALL_SCRIPT,
            "/S",
            "/AddToPath=0",
            "/D={}".format(prefix)]
        print command
    elif "" in platform.system():
        command = [
            ANACONDA_INSTALL_SCRIPT,
            "-b",
            "-p",
            "{}".format(prefix),
            "-f"]
    out, err = system_call(command)
    logger.info(
        "Finished installing Anaconda Python distribution. "
        "Output: {}, err: {}".format(out, err))


# TODO: Tailor package installation based on options specified on the command line
# Should take into account the options surrounding installing Anaconda.
def _install_packages(prefix, net_install):
    """
    install_packages

    This should install the necessary packages into the Anaconda installation
    in order for MAST to run.
    """
    prefix = os.path.join(os.path.realpath(prefix), "anaconda")
    directory = os.path.join(sys._MEIPASS, "packages")

    if "Windows" in platform.system():
        python = os.path.join(prefix, "python")
        pip = os.path.join(prefix, "Scripts", "pip")
    elif "Linux" in platform.system():
        bin_dir = os.path.join(prefix, "bin")
        lib_dir = os.path.join(prefix, "lib")
        os.putenv('PYTHONPATH', '{}:{}'.format(bin_dir, lib_dir))

        # Fix for the SELinux issue on the 32 bit installer
        if "32bit" in platform.architecture():
            out, err = system_call([
                "execstack",
                "-c",
                os.path.join(
                    lib_dir,
                    "python2.7",
                    "lib-dynload",
                    "_ctypes.so")])
            logger.debug(
                "removing execstack issue on _ctypes.so:"
                "Result: out: {}, err: {}".format(out, err))

        python = os.path.join(prefix, "bin", "python")
        pip = os.path.join(prefix, "bin", "pip")

    logger.debug("PATH: {}".format(os.environ["PATH"]))
    try:
        logger.debug("PYTHONPATH: {}".format(os.environ["PYTHONPATH"]))
    except:
        pass

    if net_install:
        repos = [
            "git+https://github.com/mcindi/mast.xor",
            "git+https://github.com/mcindi/mast.timestamp",
            "git+https://github.com/mcindi/mast.pprint",
            "git+https://github.com/mcindi/mast.plugin_utils",
            "git+https://github.com/mcindi/mast.logging",
            "git+https://github.com/mcindi/mast.config",
            "git+https://github.com/mcindi/mast.plugins",
            "git+https://github.com/mcindi/mast.hashes",
            "git+https://github.com/mcindi/mast.datapower.accounts",
            "git+https://github.com/mcindi/mast.datapower.backups",
            "git+https://github.com/mcindi/mast.datapower.datapower",
            "git+https://github.com/mcindi/mast.datapower.deployment",
            "git+https://github.com/mcindi/mast.datapower.developer",
            "git+https://github.com/mcindi/mast.datapower.network",
            "git+https://github.com/mcindi/mast.datapower.ssh",
            "git+https://github.com/mcindi/mast.datapower.status",
            "git+https://github.com/mcindi/mast.datapower.system",
            "git+https://github.com/mcindi/mast.datapower.web",
            "git+https://github.com/mcindi/mast.daemon",
            "git+https://github.com/mcindi/mast.cron",
            "git+https://github.com/mcindi/mast.cli",
            "git+https://github.com/tellapart/commandr",
            "git+https://github.com/cherrypy/cherrypy",
            "git+https://github.com/paramiko/paramiko",
            "git+https://github.com/waylan/Python-Markdown",
            "git+https://github.com/warner/python-ecdsa"
        ]
        for repo in repos:
            print "installing", repo
            out, err = system_call([pip, "install", repo])
            if err:
                print "ERROR: See log for details"
            else:
                print "Done. See logs for details"
            logger.debug(
                "Installing {}...result: out: {}, err:".format(
                    repo, out, err))
    else:
        # Sort the packages
        dir_list = os.listdir(directory)
        dir_list.sort()
        # Switch pycrypto and paramiko for dependency reasons
        for d in dir_list:
            _dir = os.path.join(directory, d)
            if os.path.exists(_dir) and os.path.isdir(_dir):
                print "Installing", d
                os.chdir(_dir)
                if "ecdsa" in d:
                    with open("setup.py", "r") as fin:
                        content = fin.read()

                    content = content.replace(
                        "version=versioneer.get_version(),",
                        "version=0.13,")

                    with open("setup.py", "w") as fout:
                        fout.write(content)

                out, err = system_call([python, "setup.py", "install"])
                print "\tDone. See log for details."
                logger.debug(
                    "Installing {}...Result: out: {}, err: {}".format(
                        d, out, err))


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


def _add_scripts(prefix):
    """
    add_scripts

    adds files and scripts needed in order to complete the mast installation.
    """
    mapping = {"MAST_HOME": prefix}
    if "Windows" in platform.system():
        script_dir = os.path.join(INSTALL_DIR, "files", "windows")
        files = [
            "mast.bat",           "notebook.bat",
            "mast-system.bat",    "mast-accounts.bat",
            "mast-backups.bat",   "mast-deployment.bat",
            "mast-developer.bat", "mast-network.bat",
            "mast-web.bat",       "mastd.bat",
            "mast-ssh.bat"
        ]
    elif "Linux" in platform.system():
        script_dir = os.path.join(INSTALL_DIR, "files", "linux")
        files = [
            "mast",           "notebook",
            "mast-system",    "mast-accounts",
            "mast-backups",   "mast-deployment",
            "mast-developer", "mast-network",
            "mast-network",   "mast-web",
            "mast-ssh"
        ]

    for f in files:
        dst = os.path.join(prefix, f)
        src = os.path.join(script_dir, f)
        content = render_template_file(src, mapping)
        write_file(dst, content)
        if "Linux" in platform.system():
            os.chmod(dst, 0755)

    if "Windows" in platform.system():
        # copy python27.dll to site-packages/win32 directory to get around
        # issue when starting mastd
        src = os.path.join(prefix, "anaconda", "python27.dll")
        dst = os.path.join(
            prefix,
            "anaconda",
            "Lib",
            "site-packages",
            "win32",
            "python27.dll"
        )
        shutil.copyfile(src, dst)

    shutil.copytree(
        os.path.join(INSTALL_DIR, "files", "bin"),
        os.path.join(prefix, "bin"))
    shutil.copytree(
        os.path.join(INSTALL_DIR, "files", "etc"),
        os.path.join(prefix, "etc"))
    shutil.copytree(
        os.path.join(INSTALL_DIR, "files", "var"),
        os.path.join(prefix, "var"))
    shutil.copytree(
        os.path.join(INSTALL_DIR, "files", "usrbin"),
        os.path.join(prefix, "usrbin"))
    shutil.copytree(
        os.path.join(INSTALL_DIR, "files", "notebooks"),
        os.path.join(prefix, "notebooks"))
    shutil.copytree(
        os.path.join(INSTALL_DIR, "files", "tmp"),
        os.path.join(prefix, "tmp"))
    shutil.copytree(
        os.path.join(INSTALL_DIR, "files", "doc"),
        os.path.join(prefix, "doc"))


def install_anaconda(prefix):
    print "Installing Anaconda Python Distribution"
    try:
        _install_anaconda(prefix)
    except:
        print "An error occurred while installing Anaconda Python distribution"
        print "See log for details."
        logger.exception(
            "An error occurred while installing Anaconda Python distribution")
        sys.exit(-1)
    print "\tDone. See log for details"


def install_packages(prefix, net_install):
    print "Installing Python Packages"
    try:
        _install_packages(prefix, net_install)
    except:
        print "An error occurred while installing Python Packages"
        print "See log for details."
        logger.exception(
            "An error occurred while installing Python Packages")
        sys.exit(-1)
    print "\tDone. See log for details"


def add_scripts(prefix):
    print "Adding scripts"
    try:
        _add_scripts(prefix)
    except:
        print "An error occurred while adding scripts"
        print "See log for details."
        logger.exception(
            "An error occurred while adding scripts")
        sys.exit(-1)
    print "\tDone. See log for details"


def main(prefix=".", net_install=False):
    """
    main

    install mast into specified directory.
    """
    if prefix == ".":
        prefix = os.path.realpath(prefix)
        prefix = os.path.join(prefix, "mast")
    else:
        prefix = os.path.realpath(prefix)
    install_anaconda(prefix)
    install_packages(prefix, net_install)
    add_scripts(prefix)


if __name__ == "__main__":
    _cli = cli.Cli(main=main)
    _cli.run()
