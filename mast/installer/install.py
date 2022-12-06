
import os
import sys
import cli
from shutil import *
import logging
import platform
import urllib.request, urllib.error, urllib.parse
import zipfile
import subprocess
from tstamp import Timestamp
from io import StringIO
from resources import (
    pip_dependencies,
    conda_dependencies,
)

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


def print(s):
    logger.info(s)
    sys.stdout.write("{}{}".format(s.rstrip(), os.linesep))
    sys.stdout.flush()


def copytree(src, dst, symlinks=False, ignore=None):
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    if not os.path.exists(dst):
        os.makedirs(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                copy2(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error) as why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as err:
            errors.extend(err.args[0])
    try:
        copystat(src, dst)
    except WindowsError:
        # can't copy file access times on Windows
        pass
    except OSError as why:
        errors.extend((src, dst, str(why)))
    if errors:
        raise Error(errors)

cwd = sys._MEIPASS

if "Windows" in platform.system():
    if "32bit" in platform.architecture():
        ANACONDA_INSTALL_SCRIPT = os.path.join(
            cwd,
            "scripts",
            "miniconda",
            "Miniconda3-latest-Windows-x86.exe")
    elif "64bit" in platform.architecture():
        ANACONDA_INSTALL_SCRIPT = os.path.join(
            cwd,
            "scripts",
            "miniconda",
            "Miniconda3-latest-Windows-x86_64.exe")
elif "Linux" in platform.system():
    if '32bit' in platform.architecture():
        ANACONDA_INSTALL_SCRIPT = os.path.join(
            cwd,
            "scripts",
            "miniconda",
            "Miniconda3-latest-linux32-install.sh")
    elif '64bit' in platform.architecture():
        ANACONDA_INSTALL_SCRIPT = os.path.join(
            cwd,
            "scripts",
            "miniconda",
            "Miniconda3-latest-linux64-install.sh")
elif "Darwin" in platform.system():
    if '64bit' in platform.architecture():
        ANACONDA_INSTALL_SCRIPT = os.path.join(
            cwd,
            "scripts",
            "miniconda",
            "Miniconda3-latest-macosx64-install.sh")

INSTALL_DIR = cwd


def system_call(command):
    """
    # system_call

    helper function to shell out commands. This should be platform
    agnostic.
    """
    print("\n### {}".format(command))
    stderr = subprocess.STDOUT
    pipe = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
    )
    stdout, stderr = pipe.communicate()
    print(stdout)


# TODO: Move some options to the command line.
def install_anaconda(prefix):
    """
    install_anaconda

    This will issue the command to install Anaconda into the specified
    directory.
    """
    prefix = os.path.join(os.path.realpath(prefix), "miniconda")
    if "Windows" in platform.system():
        command = " ".join([
            ANACONDA_INSTALL_SCRIPT,
            "/S",
            "/AddToPath=0",
            "/RegisterPython=0",
            "/D={}".format(prefix)])
    elif "Linux" in platform.system():
        command = " ".join([
            ANACONDA_INSTALL_SCRIPT,
            "-b",
            "-p",
            "{}".format(prefix),
            "-f"])
    elif "Darwin" in platform.system():
        command = " ".join([
            ANACONDA_INSTALL_SCRIPT,
            "-b",
            "-p",
            "{}".format(prefix),
            "-f"])
    system_call(command)


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
        python = os.path.join(prefix, "bin", "python")
    elif "Darwin" in platform.system():
        bin_dir = os.path.join(prefix, "bin")
        lib_dir = os.path.join(prefix, "lib")
        os.putenv('PYTHONPATH', '{}:{}'.format(bin_dir, lib_dir))

        # Fix for the SELinux issue on the 32 bit installer
        if "32bit" in platform.architecture() and "armv7l" not in platform.machine():
            system_call(
                " ".join([
                    "execstack",
                    "-c",
                    os.path.join(
                        lib_dir,
                        "python2.7",
                        "lib-dynload",
                        "_ctypes.so"
                    )
                ]),
            )

        python = os.path.join(prefix, "bin", "python")

    print("\tEnsuring pip is installed")
    system_call(
        " ".join([python, "-m", "ensurepip"]),
    )

    if net_install:
        for dependency in list(conda_dependencies[platform.system()][platform.architecture()[0]].keys()):
            print("### installing: {}".format(dependency))
            system_call(
                " ".join([
                    python,
                    "-m",
                    "conda",
                    "install",
                    dependency,
                ]),
            )
        for dependency in pip_dependencies:
            print("### installing: {}".format(dependency))

            if dependency == "lxml":
                system_call(
                    " ".join([
                        python,
                        "-m",
                        "pip",
                        "install",
                        "--only-binary",
                        ":all:",
                        '"{}"'.format(dependency),
                    ]),
                )
            else:
                system_call(
                    " ".join([
                        python,
                        "-m",
                        "pip",
                        "install",
                        '"{}"'.format(dependency),
                    ]),
                )

    else:
        for dependency in list(conda_dependencies[platform.system()][platform.architecture()[0]].keys()):
            print("### installing: {}".format(dependency))
            _dependency = list(
                [filename for filename in os.listdir(directory) if (dependency.lower() in filename.lower()) and (".tar.bz2" in filename)]
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
            )
        for dependency in pip_dependencies:
            print("### installing: {}".format(dependency))
            _dependency = dependency
            if "git+" in dependency:
                _dependency = dependency.split("/")[-1].split("@")[0]
            if "mast" in dependency:
                system_call(
                    " ".join([
                        python,
                        "-m",
                        "pip",
                        "install",
                        "--no-index",
                        "--force-reinstall",
                        "--find-links",
                        directory,
                        '"{}"'.format(_dependency),
                    ]),
                )
            else:
                if dependency == "lxml":
                    system_call(
                        " ".join([
                            python,
                            "-m",
                            "pip",
                            "install",
                            "--upgrade",
                            "--no-index",
                            "--only-binary",
                            ":all:",
                            "--find-links",
                            directory,
                            '"{}"'.format(_dependency),
                        ]),
                    )
                else:
                    system_call(
                        " ".join([
                            python,
                            "-m",
                            "pip",
                            "install",
                            "--upgrade",
                            "--no-index",
                            "--find-links",
                            directory,
                            '"{}"'.format(_dependency),
                        ]),
                    )



def render_template(string, mappings):
    for k, v in list(mappings.items()):
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
            "mast-system.bat",
            "mast-accounts.bat",
            "mast-backups.bat",
            "mast-crypto.bat",
            "mast-deployment.bat",
            "mast-developer.bat",
            "mast-network.bat",
            "test-mast.bat",
            "mast-version.bat",
            "mast-web.bat",
            "mastd.bat",
            "mast-ssh.bat",
            "set-env.bat",
        ]
    elif "Linux" in platform.system():
        script_dir = os.path.join(INSTALL_DIR, "files", "linux")
        files = [
            "mast",
            "mast-system",
            "mast-accounts",
            "mast-backups",
            "mast-crypto",
            "mast-deployment",
            "mast-developer",
            "mast-network",
            "test-mast",
            "mast-version",
            "mast-web",
            "mast-ssh",
            "mastd",
            "set-env",
        ]
    elif "Darwin" in platform.system():
        script_dir = os.path.join(INSTALL_DIR, "files", "linux")
        files = [
            "mast",
            "mast-system",
            "mast-accounts",
            "mast-backups",
            "mast-crypto",
            "mast-deployment",
            "mast-developer",
            "mast-network",
            "test-mast",
            "mast-version",
            "mast-web",
            "mast-ssh",
            "mastd",
            "set-env",
        ]

    for f in files:
        dst = os.path.join(prefix, f)
        src = os.path.join(script_dir, f)
        print("{} -> {}".format(src, dst))
        content = render_template_file(src, mapping)
        write_file(dst, content)
        if "Linux" in platform.system():
            os.chmod(dst, 0o755)
        if "Darwin" in platform.system():
            os.chmod(dst, 0o755)

    if "Windows" in platform.system():
        pass
        # Temporarily disable this python27 stuff, do we need for python3
        # copy python27.dll to site-packages/win32 directory to get around
        # issue when starting mastd
        # src = os.path.join(prefix, "miniconda", "python27.dll")
        # dst = os.path.join(
        #     prefix,
        #     "miniconda",
        #     "Lib",
        #     "site-packages",
        #     "win32",
        #     "python27.dll"
        # )
        # copyfile(src, dst)
        # for filename in ["pythoncom27.dll", "pythoncomloader27.dll", "pywintypes27.dll"]:
        #     src = os.path.join(
        #         prefix,
        #         "miniconda",
        #         "Lib",
        #         "site-packages",
        #         "pywin32_system32",
        #         filename,
        #     )
        #     dst = os.path.join(
        #         prefix,
        #         "miniconda",
        #         "Lib",
        #         "site-packages",
        #         "win32",
        #         filename,
        #     )
        #     copyfile(src, dst)
    copytree(
        os.path.join(INSTALL_DIR, "files", "bin"),
        os.path.join(prefix, "bin")
    )
    copytree(
        os.path.join(INSTALL_DIR, "files", "etc"),
        os.path.join(prefix, "etc")
    )
    copytree(
        os.path.join(INSTALL_DIR, "files", "var"),
        os.path.join(prefix, "var")
    )
    copytree(
        os.path.join(INSTALL_DIR, "files", "usrbin"),
        os.path.join(prefix, "usrbin")
    )
    copytree(
        os.path.join(INSTALL_DIR, "files", "tmp"),
        os.path.join(prefix, "tmp")
    )
    copytree(
        os.path.join(INSTALL_DIR, "files", "doc"),
        os.path.join(prefix, "doc")
    )
    copytree(
        os.path.join(INSTALL_DIR, "files", "contrib"),
        os.path.join(prefix, "contrib")
    )


def generate_docs(prefix):
    if "Windows" in platform.system():
        mast = os.path.join(prefix, "mast.bat")
    if "Linux" in platform.system():
        mast = os.path.join(prefix, "mast")
    if "Darwin" in platform.system():
        mast = os.path.join(prefix, "mast")
    system_call(
        " ".join([mast, "contrib/gendocs.py"]),
    )


def install_packages(prefix, net_install):
    print("Installing Python Packages")
    _install_packages(prefix, net_install)


def add_scripts(prefix):
    print("Adding scripts")
    try:
        _add_scripts(prefix)
    except:
        print("An error occurred while adding scripts")
        print("See log for details.")
        logger.exception(
            "An error occurred while adding scripts")
        sys.exit(-1)
    print("\tDone. See log for details")



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
