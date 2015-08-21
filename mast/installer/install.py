#!/usr/bin/env python
import cli
import os
import subprocess
import shutil
import logging
import platform
from tstamp import Timestamp

# TODO: make this conditional on platform
if "Windows" in platform.system():
    ANACONDA_INSTALL_SCRIPT = os.path.join(
        os.getcwd(),
        "scripts",
        "anaconda",
        "Anaconda-2.3.0-Windows-x86_64.exe")
elif "Linux" in platform.system():
    ANACONDA_INSTALL_SCRIPT = os.path.join(
        os.getcwd(),
        "scripts",
        "anaconda",
        "Anaconda-2.3.0-Linux-x86_64.sh")
INSTALL_DIR = os.getcwd()

# Move some of the logging options to the command line
t = Timestamp()
logging.basicConfig(
    filename="{}-mast-install.log".format(t.timestamp),
    filemode="w",
    format="level=%(levelname)s; datetime=%(asctime)s; process_name=%(processName)s; pid=%(process)d; thread=%(thread)d; module=%(module)s; function=%(funcName)s; line=%(lineno)d; message=%(message)s")
logger = logging.getLogger("mast.installer")
logger.setLevel(10)


def system_call(command):
    """
    system_call

    convenience method for shelling out commands. This is platform agnostic, but
    the commands sent in should not be.
    """
    stderr = subprocess.STDOUT
    pipe = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    stdout, stderr = pipe.communicate()
    return stdout, stderr


# TODO: add in conditionals around platform, and move some
# options to the command line.
def install_anaconda(prefix):
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
            "/D={}".format(prefix)]
        print command
    elif "" in platform.system():
        command = [
            ANACONDA_INSTALL_SCRIPT,
            "-b",
            "-p",
            "{}".format(prefix),
            "-f"]
    out = system_call(command)
    return out


# TODO: Tailor package installation based on options specified on the command line
# Should take into account the options surrounding installing Anaconda.
def install_packages(prefix):
    """
    install_packages

    This should install the necessary packages into the Anaconda installation
    in order for MAST to run.
    """
    _prefix = prefix
    prefix = os.path.join(os.path.realpath(prefix), "anaconda")
    directory = os.path.join(os.getcwd(), "packages")
#    out, err = system_call([os.path.join(prefix, "bin", "conda"), "install", "-y", "ipython-notebook"])
#    logger.debug("Installing IPython Notebook...Result: out: {}, err: {}".format(out, err))
#    out, err = system_call([os.path.join(prefix, "bin", "python"), os.path.join(directory, "ez_setup.py")])
#    logger.debug("Installing setuptools...Result: out: {}, err: {}".format(out, err))
#    out, err = system_call([os.path.join(prefix, "bin", "conda"), "install", "-y", "openpyxl"])
#    logger.debug("Installing openpyxl...Result: out: {}, err: {}".format(out, err))
    if "Windows" in platform.system():
        conda = os.path.join(prefix, "Scripts", "conda")
        pip = os.path.join(prefix, "Scripts", "pip")
        python = os.path.join(prefix, "python")
    elif "Linux" in platform.system():
        conda = os.path.join(prefix, "bin", "conda")
        pip = os.path.join(prefix, "bin", "pip")
        python = os.path.join(prefix, "bin", "python")

    out, err = system_call([conda, "install", "-y", "flask"])
    logger.debug("Installing flask...Result: out: {}, err: {}".format(out, err))

    out, err = system_call([conda, "install", "-y", "paramiko"])
    logger.debug("Installing paramiko...Result: out: {}, err: {}".format(out, err))

    out, err = system_call([pip, "install", "commandr"])
    logger.debug("Installing commandr...Result: out: {}, err: {}".format(out, err))

    out, err = system_call([pip, "install", "cherrypy"])
    logger.debug("Installing cherrypy...Result: out: {}, err: {}".format(out, err))

    out, err = system_call([pip, "install", "markdown"])
    logger.debug("Installing markdown...Result: out: {}, err: {}".format(out, err))

    for d in os.listdir(directory):
        _dir = os.path.join(directory, d)
        if os.path.exists(_dir) and os.path.isdir(_dir):
            os.chdir(_dir)
            out, err = system_call([python, "setup.py", "install"])
            logger.debug("Installing {}...Result: out: {}, err: {}".format(d, out, err))


def add_scripts(prefix):
    """
    add_scripts

    adds files and scripts needed in order to complete the mast installation.
    """
    if "Windows" in platform.system():
        with open(os.path.join(INSTALL_DIR, "files", "windows", "mast.bat"), "r") as fin:
            with open(os.path.join(prefix, "mast.bat"), "w") as fout:
                fout.write(fin.read().replace("<%MAST_HOME%>", prefix))
    elif "Linux" in platform.system():
        with open(os.path.join(INSTALL_DIR, "files", "linux", "mast"), "r") as fin:
            with open(os.path.join(prefix, "mast"), "w") as fout:
                fout.write(fin.read().replace("<%MAST_HOME%>", prefix))
        with open(os.path.join(INSTALL_DIR, "files", "linux", "notebook"), "r") as fin:
            with open(os.path.join(prefix, "notebook"), "w") as fout:
                fout.write(fin.read().replace("<%MAST_HOME%>", prefix))
        with open(os.path.join(INSTALL_DIR, "files", "linux", "mast-system"), "r") as fin:
            with open(os.path.join(prefix, "mast-system"), "w") as fout:
                fout.write(fin.read().replace("<%MAST_HOME%>", prefix))
        with open(os.path.join(INSTALL_DIR, "files", "linux", "mast-accounts"), "r") as fin:
            with open(os.path.join(prefix, "mast-accounts"), "w") as fout:
                fout.write(fin.read().replace("<%MAST_HOME%>", prefix))
        with open(os.path.join(INSTALL_DIR, "files", "linux", "mast-backups"), "r") as fin:
            with open(os.path.join(prefix, "mast-backups"), "w") as fout:
                fout.write(fin.read().replace("<%MAST_HOME%>", prefix))
        with open(os.path.join(INSTALL_DIR, "files", "linux", "mast-deployment"), "r") as fin:
            with open(os.path.join(prefix, "mast-deployment"), "w") as fout:
                fout.write(fin.read().replace("<%MAST_HOME%>", prefix))
        with open(os.path.join(INSTALL_DIR, "files", "linux", "mast-developer"), "r") as fin:
            with open(os.path.join(prefix, "mast-developer"), "w") as fout:
                fout.write(fin.read().replace("<%MAST_HOME%>", prefix))
        with open(os.path.join(INSTALL_DIR, "files", "linux", "mast-network"), "r") as fin:
            with open(os.path.join(prefix, "mast-network"), "w") as fout:
                fout.write(fin.read().replace("<%MAST_HOME%>", prefix))
        with open(os.path.join(INSTALL_DIR, "files", "linux", "mast-web"), "r") as fin:
            with open(os.path.join(prefix, "mast-web"), "w") as fout:
                fout.write(fin.read().replace("<%MAST_HOME%>", prefix))
        os.chmod(os.path.join(prefix, "mast"), 0755)
        os.chmod(os.path.join(prefix, "mast-system"), 0755)
        os.chmod(os.path.join(prefix, "mast-accounts"), 0755)
        os.chmod(os.path.join(prefix, "mast-backups"), 0755)
        os.chmod(os.path.join(prefix, "mast-deployment"), 0755)
        os.chmod(os.path.join(prefix, "mast-developer"), 0755)
        os.chmod(os.path.join(prefix, "mast-network"), 0755)
        os.chmod(os.path.join(prefix, "mast-web"), 0755)
        os.chmod(os.path.join(prefix, "notebook"), 0755)

    shutil.copytree(os.path.join(INSTALL_DIR, "files", "bin"), os.path.join(prefix, "bin"))
    shutil.copytree(os.path.join(INSTALL_DIR, "files", "etc"), os.path.join(prefix, "etc"))
    shutil.copytree(os.path.join(INSTALL_DIR, "files", "var"), os.path.join(prefix, "var"))
    shutil.copytree(os.path.join(INSTALL_DIR, "files", "usrbin"), os.path.join(prefix, "usrbin"))
    shutil.copytree(os.path.join(INSTALL_DIR, "files", "notebooks"), os.path.join(prefix, "notebooks"))

def main(prefix="."):
    """
    main

    install mast into specified directory.
    """
    prefix = os.path.realpath(prefix)
    print install_anaconda(prefix)
    print install_packages(prefix)
    add_scripts(prefix)

if __name__ == "__main__":
    _cli = cli.Cli(main=main)
    _cli.run()
