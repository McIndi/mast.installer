#!/usr/bin/env python
import os
import sys
import cli
import shutil
import logging
import platform
import urllib2
import zipfile
import subprocess
from tstamp import Timestamp
from cStringIO import StringIO
from resources import (
    pip_dependencies,
    conda_dependencies,
)

cwd = sys._MEIPASS

if "Windows" in platform.system():
    if "32bit" in platform.architecture():
        ANACONDA_INSTALL_SCRIPT = os.path.join(
            cwd,
            "scripts",
            "miniconda",
            "Miniconda2-latest-Windows-x86.exe")
    elif "64bit" in platform.architecture():
        ANACONDA_INSTALL_SCRIPT = os.path.join(
            cwd,
            "scripts",
            "miniconda",
            "Miniconda2-latest-Windows-x86_64.exe")
elif "Linux" in platform.system():
    if '32bit' in platform.architecture():
        ANACONDA_INSTALL_SCRIPT = os.path.join(
            cwd,
            "scripts",
            "miniconda",
            "Miniconda2-latest-linux32-install.sh")
    elif '64bit' in platform.architecture():
        ANACONDA_INSTALL_SCRIPT = os.path.join(
            cwd,
            "scripts",
            "miniconda",
            "Miniconda2-latest-linux64-install.sh")

INSTALL_DIR = cwd

# TODO: Move some of the logging options to the command line
t = Timestamp()
filename = "{}-mast-install.log".format(t.timestamp)
logging.basicConfig(
    filename=filename,
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


# TODO: Move some options to the command line.
def install_anaconda(prefix):
    """
    install_anaconda

    This will issue the command to install Anaconda into the specified
    directory.
    """
    prefix = os.path.join(os.path.realpath(prefix), "miniconda")
    if "Windows" in platform.system():
        command = [
            ANACONDA_INSTALL_SCRIPT,
            "/S",
            "/AddToPath=0",
            "/RegisterPython=0",
            "/D={}".format(prefix)]
    elif "Linux" in platform.system():
        command = " ".join([
            ANACONDA_INSTALL_SCRIPT,
            "-b",
            "-p",
            "{}".format(prefix),
            "-f"])
    out, err = system_call(command, stdout=sys.stdout, stderr=sys.stderr)
    print(out)
    print(err)


# TODO: Tailor package installation based on options specified on the command line
# Should take into account the options surrounding installing Anaconda.
def _install_packages(prefix, net_install):
    """
    install_packages

    This should install the necessary packages into the Anaconda installation
    in order for MAST to run.
    """
    prefix = os.path.join(os.path.realpath(prefix), "miniconda")
    directory = os.path.join(sys._MEIPASS, "packages")
    tmp_dir = os.path.join(sys._MEIPASS, "tmp")
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    if "Windows" in platform.system():
        python = os.path.join(prefix, "python")
    elif "Linux" in platform.system():
        bin_dir = os.path.join(prefix, "bin")
        lib_dir = os.path.join(prefix, "lib")
        os.putenv('PYTHONPATH', '{}:{}'.format(bin_dir, lib_dir))

        # Fix for the SELinux issue on the 32 bit installer
        if "32bit" in platform.architecture() and "armv7l" not in platform.machine():
            system_call(
                [
                    "execstack",
                    "-c",
                    os.path.join(
                        lib_dir,
                        "python2.7",
                        "lib-dynload",
                        "_ctypes.so"
                    )
                ],
                stdout=sys.stdout,
                stderr=sys.stderr,
            )

        python = os.path.join(prefix, "bin", "python")

    print("\tEnsuring pip is installed")
    system_call(
        [python, "-m", "ensurepip"],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

    if net_install:
        for dependency in conda_dependencies[platform.system()][platform.architecture()[0]].keys():
            print("### installing: {}".format(dependency))
            system_call(
                " ".join([
                    python,
                    "-m",
                    "install",
                    dependency,
                ]),
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
        for dependency in pip_dependencies:
            print("### installing: {}".format(dependency))

            system_call(
                " ".join([
                    python,
                    "-m",
                    "pip",
                    "install",
                    '"{}"'.format(dependency),
                ]),
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
    else:
        for dependency in conda_dependencies[platform.system()][platform.architecture()[0]].keys():
            print("### installing: {}".format(dependency))
            _dependency = list(
                filter(
                    lambda filename: (dependency.lower() in filename.lower()) and (".tar.bz2" in filename),
                    os.listdir(directory)
                )
            )
            _dependency = os.path.join(directory, _dependency[0])

            system_call(
                " ".join([
                    python,
                    "-m",
                    "conda",
                    "install",
                    "--offline",
                    _dependency,
                ]),
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
        for dependency in pip_dependencies:
            print("### installing: {}".format(dependency))
            _dependency = dependency
            if "git+" in dependency:
                _dependency = dependency.split("/")[-1].split("#")[0]
            system_call(
                " ".join([
                    python,
                    "-m",
                    "pip",
                    "install",
                    "--no-index",
                    "--find-links",
                    directory,
                    '"{}"'.format(_dependency),
                ]),
                stdout=sys.stdout,
                stderr=sys.stderr,
            )


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
            "mast.bat",
            "notebook.bat",
            "mast-system.bat",
            "mast-accounts.bat",
            "mast-backups.bat",
            "mast-crypto.bat",
            "mast-deployment.bat",
            "mast-developer.bat",
            "mast-network.bat",
            "test-mast.bat",
            "mast-web.bat",
            "mastd.bat",
            "mast-ssh.bat",
            "set-env.bat"
        ]
    elif "Linux" in platform.system():
        script_dir = os.path.join(INSTALL_DIR, "files", "linux")
        files = [
            "mast",
            "notebook",
            "mast-system",
            "mast-accounts",
            "mast-backups",
            "mast-crypto",
            "mast-deployment",
            "mast-developer",
            "mast-network",
            "test-mast",
            "mast-web",
            "mast-ssh",
            "mastd",
            "set-env"
        ]

    for f in files:
        dst = os.path.join(prefix, f)
        src = os.path.join(script_dir, f)
        print("{} -> {}".format(src, dst))
        content = render_template_file(src, mapping)
        write_file(dst, content)
        if "Linux" in platform.system():
            os.chmod(dst, 0755)

    if "Windows" in platform.system():
        # copy python27.dll to site-packages/win32 directory to get around
        # issue when starting mastd
        src = os.path.join(prefix, "miniconda", "python27.dll")
        dst = os.path.join(
            prefix,
            "miniconda",
            "Lib",
            "site-packages",
            "win32",
            "python27.dll"
        )
        shutil.copyfile(src, dst)
        for filename in ["pythoncom27.dll", "pythoncomloader27.dll", "pywintypes27.dll"]:
            src = os.path.join(
                prefix,
                "miniconda",
                "Lib",
                "site-packages",
                "pywin32_system32",
                filename,
            )
            dst = os.path.join(
                prefix,
                "miniconda",
                "Lib",
                "site-packages",
                "win32",
                filename,
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
    shutil.copytree(
        os.path.join(INSTALL_DIR, "files", "contrib"),
        os.path.join(prefix, "contrib"))


def generate_docs(prefix):
    if "Windows" in platform.system():
        mast = os.path.join(prefix, "mast.bat")
    if "Linux" in platform.system():
        mast = os.path.join(prefix, "mast")
    system_call(
        " ".join([mast, "contrib/gendocs.py"]),
        stdout=sys.stdout,
        stderr=sys.stderr,
    )


def install_packages(prefix, net_install):
    print "Installing Python Packages"
    _install_packages(prefix, net_install)


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



def main(prefix="", net_install=False):
    """
    install mast into specified directory. Defaults to `$PWD/mast`.

    Parameters:

    * prefix: The location to which to install mast. If not provided,
    it will install mast to a "mast" subdirectory of the location of
    the installer. If you want it installed anywhere specific provide
    that (either full or relative) to this parameter
    * net_install: If specified, the latest versions of all modules will
    be downloaded from the internet and installed as opposed to just the
    versions shipped with the installer
    """
    if prefix == "":
        prefix = os.path.realpath(prefix)
        prefix = os.path.join(prefix, "mast")
    else:
        prefix = os.path.realpath(prefix)
    install_anaconda(prefix)
    install_packages(prefix, net_install)
    add_scripts(prefix)
    generate_docs(prefix)

if __name__ == "__main__":
    _cli = cli.Cli(main=main)
    _cli.run()
