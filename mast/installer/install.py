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
        "Anaconda-2.3.0-Windows-x86_64.exe")
elif "Linux" in platform.system():
    ANACONDA_INSTALL_SCRIPT = os.path.join(
        cwd,
        "scripts",
        "anaconda",
        "anaconda-2.3.0-linux-install.sh")
INSTALL_DIR = cwd

# TODO: Move some of the logging options to the command line
t = Timestamp()
logging.basicConfig(
    filename="{}-mast-install.log".format(t.timestamp),
    filemode="w",
    format="level=%(levelname)s; datetime=%(asctime)s; process_name=%(processName)s; pid=%(process)d; thread=%(thread)d; module=%(module)s; function=%(funcName)s; line=%(lineno)d; message=%(message)s")
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
    prefix = os.path.join(os.path.realpath(prefix), "anaconda")
    directory = os.path.join(sys._MEIPASS, "packages")

    if "Windows" in platform.system():
        python = os.path.join(prefix, "python")
    elif "Linux" in platform.system():
        bin_dir = os.path.join(prefix, "bin")
        lib_dir = os.path.join(prefix, "lib")
        os.putenv('PYTHONPATH','{}:{}'.format(bin_dir, lib_dir))
        
        # Fix for the SELinux issue
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

    logger.debug("PATH: {}".format(os.environ["PATH"]))
    try:
        logger.debug("PYTHONPATH: {}".format(os.environ["PYTHONPATH"]))
    except:
        pass

    # Sort the packages
    dir_list = os.listdir(directory)
    dir_list.sort()
    # Switch pycrypto and paramiko for dependency reasons
    a, b = dir_list.index("paramiko"), dir_list.index("pycrypto")
    dir_list[a], dir_list[b] = dir_list[b], dir_list[a]
    for d in dir_list:
        _dir = os.path.join(directory, d)
        if os.path.exists(_dir) and os.path.isdir(_dir):
            os.chdir(_dir)
            if "ecdsa" in d:
                out, err = system_call([python, "setup.py", "version"])
                with open("setup.py", "r") as fin:
                    content = fin.read()
                content = content.replace("version=versioneer.get_version(),", "version=0.13,")
                with open("setup.py", "w") as fout:
                    fout.write(content)
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
        with open(os.path.join(INSTALL_DIR, "files", "windows", "notebook.bat"), "r") as fin:
            with open(os.path.join(prefix, "notebook.bat"), "w") as fout:
                fout.write(fin.read().replace("<%MAST_HOME%>", prefix))
        with open(os.path.join(INSTALL_DIR, "files", "windows", "mast-system.bat"), "r") as fin:
            with open(os.path.join(prefix, "mast-system.bat"), "w") as fout:
                fout.write(fin.read().replace("<%MAST_HOME%>", prefix))
        with open(os.path.join(INSTALL_DIR, "files", "windows", "mast-accounts.bat"), "r") as fin:
            with open(os.path.join(prefix, "mast-accounts.bat"), "w") as fout:
                fout.write(fin.read().replace("<%MAST_HOME%>", prefix))
        with open(os.path.join(INSTALL_DIR, "files", "windows", "mast-backups.bat"), "r") as fin:
            with open(os.path.join(prefix, "mast-backups.bat"), "w") as fout:
                fout.write(fin.read().replace("<%MAST_HOME%>", prefix))
        with open(os.path.join(INSTALL_DIR, "files", "windows", "mast-deployment.bat"), "r") as fin:
            with open(os.path.join(prefix, "mast-deployment.bat"), "w") as fout:
                fout.write(fin.read().replace("<%MAST_HOME%>", prefix))
        with open(os.path.join(INSTALL_DIR, "files", "windows", "mast-developer.bat"), "r") as fin:
            with open(os.path.join(prefix, "mast-developer.bat"), "w") as fout:
                fout.write(fin.read().replace("<%MAST_HOME%>", prefix))
        with open(os.path.join(INSTALL_DIR, "files", "windows", "mast-network.bat"), "r") as fin:
            with open(os.path.join(prefix, "mast-network.bat"), "w") as fout:
                fout.write(fin.read().replace("<%MAST_HOME%>", prefix))
        with open(os.path.join(INSTALL_DIR, "files", "windows", "mast-web.bat"), "r") as fin:
            with open(os.path.join(prefix, "mast-web.bat"), "w") as fout:
                fout.write(fin.read().replace("<%MAST_HOME%>", prefix))
        with open(os.path.join(INSTALL_DIR, "files", "windows", "mastd.bat"), "r") as fin:
            with open(os.path.join(prefix, "mastd.bat"), "w") as fout:
                fout.write(fin.read().replace("<%MAST_HOME%>", prefix))
        # copy python27.dll to site-packages/win32 directory to get around
        # issue when starting mastd
        src = os.path.join(prefix, "anaconda", "python27.dll")
        dst = os.path.join(prefix, "anaconda", "Lib", "site-packages", "win32", "python27.dll")
        shutil.copyfile(src, dst)
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
        with open(os.path.join(INSTALL_DIR, "files", "linux", "mastd"), "r") as fin:
            with open(os.path.join(prefix, "mastd"), "w") as fout:
                fout.write(fin.read().replace("<%MAST_HOME%>", prefix))
        os.chmod(os.path.join(prefix, "mast"), 0755)
        os.chmod(os.path.join(prefix, "mast-system"), 0755)
        os.chmod(os.path.join(prefix, "mast-accounts"), 0755)
        os.chmod(os.path.join(prefix, "mast-backups"), 0755)
        os.chmod(os.path.join(prefix, "mast-deployment"), 0755)
        os.chmod(os.path.join(prefix, "mast-developer"), 0755)
        os.chmod(os.path.join(prefix, "mast-network"), 0755)
        os.chmod(os.path.join(prefix, "mast-web"), 0755)
        os.chmod(os.path.join(prefix, "mastd"), 0755)
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
