#!/usr/bin/env python
import os
import sys
import cli
import shutil
import logging
import platform
import subprocess
from tstamp import Timestamp
import dulwich.porcelain as git

cwd = sys._MEIPASS

if "Windows" in platform.system():
    if "32bit" in platform.architecture():
        ANACONDA_INSTALL_SCRIPT = os.path.join(
            cwd,
            "scripts",
            "anaconda",
            "Anaconda-2.4.0-Windows-x86.exe")
    elif "64bit" in platform.architecture():
        ANACONDA_INSTALL_SCRIPT = os.path.join(
            cwd,
            "scripts",
            "anaconda",
            "Anaconda-2.4.0-Windows-x86_64.exe")
elif "Linux" in platform.system():
    if '32bit' in platform.architecture():
        if "armv7l" in platform.machine():
            ANACONDA_INSTALL_SCRIPT = os.path.join(
                cwd,
                "scripts",
                "anaconda",
                "Miniconda-latest-Linux-armv7l.sh")
        else:
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
            "/RegisterPython=0",
            "/D={}".format(prefix)]
    elif "Linux" in platform.system():
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

    logger.info("Ensuring pip is installed")
    print "Ensuring pip is installed"
    out, err = system_call([python, "-m", "ensurepip"])
    if err:
        logger.error("An error occurred while ensuring pip is installed, {}".format(err))
        print "\tERROR: See log for details"
    else:
        logger.debug("Output of ensurepip, {}".format(out))
        print "\tDone, see log for details"
    logger.debug("PATH: {}".format(os.environ["PATH"]))
    try:
        logger.debug("PYTHONPATH: {}".format(os.environ["PYTHONPATH"]))
    except:
        pass

    if net_install:
        repos = [
            "https://github.com/McIndi/mast.cli/archive/master.zip",
            "https://github.com/McIndi/mast.config/archive/master.zip",
            "https://github.com/McIndi/mast.cron/archive/master.zip",
            "https://github.com/McIndi/mast.daemon/archive/master.zip",
            "https://github.com/McIndi/mast.datapower.accounts/archive/master.zip",
            "https://github.com/McIndi/mast.datapower.backups/archive/master.zip",
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
            "https://github.com/mcindi/mast.timestamp/archive/master.zip",
            "https://github.com/mcindi/mast.xor/archive/master.zip",
            "https://github.com/tellapart/commandr/archive/master.zip",
            "https://github.com/cherrypy/cherrypy/archive/master.zip",
            "https://github.com/paramiko/paramiko/archive/master.zip",
            "https://github.com/waylan/Python-Markdown/archive/master.zip",
            "https://github.com/warner/python-ecdsa/archive/master.zip",
            "https://github.com/jelmer/dulwich/archive/master.zip"
        ]
        for repo in repos:
            print "installing", repo

            resp = requests.get(repo)
            zf = zipfile.ZipFile(StringIO(resp.content))
            zf.extractall()
            for item in zf.infolist():
                print "\t", item.filename
            dirname = zf.infolist()[0].replace("/", "")
            # chdir & install

            cwd = os.getcwd()
            os.chdir(dirname)
            if "dulwich" in repo:
                out, err = system_call([python, "setup.py", "--pure", "install", "--force"])
            else:
                out, err = system_call([python, "setup.py", "install", "--force"])
            if err:
                print "\tERROR: check the log for details"
                logger.error(
                    "An error was encountered: {}".format(err))
            else:
                print "\tDONE: {} installed, check log for details".format(
                    repo)
                logger.debug(
                    "installed {}. out: {}, err: {}".format(repo, out, err))
            os.chdir(cwd)

    else:
        # Sort the packages
        dir_list = os.listdir(directory)
        dir_list.sort()
        print dir_list
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

                if "dulwich" in d:
                    out, err = system_call([python, "setup.py", "--pure", "install"])
                else:
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
            "mast-web",       "mast-ssh",
            "mastd"
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
    shutil.copytree(
        os.path.join(INSTALL_DIR, "files", "contrib"),
        os.path.join(prefix, "contrib"))


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


def _generate_docs(prefix):
    if "Windows" in platform.system():
        mast = os.path.join(prefix, "mast.bat")
    if "Linux" in platform.system():
        mast = os.path.join(prefix, "mast")
    out, err = system_call([mast, "contrib/gendocs.py"])
    print out
    if err:
        print "\n\nERROR:\n\n{}".format(err)


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


def generate_docs(prefix):
    print "Generating Documentation"
    try:
        _generate_docs(prefix)
    except:
        print "An error occurred generating documentation"
        print "See log for details"
        logger.exception(
            "An error occurred generating documentation")
        raise
    print "\tDone. See log for details."

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
