'''Script to build an update package for mast.

The update package will be an executable which will
contain:
    * an updated Python installer
    * Updated packages of dependencies
    * Updated mast packages
    * updated contrib scripts

The updater will perform an in-place upgrade of mast
while preserving the original Python installation
to facilitate a roll-back if needed.
'''
import os
import sys
import shutil
import logging
import argparse
import subprocess
from pathlib import Path
from textwrap import dedent

import requests

class RawTextWithDefaultsHelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter,
):
    pass

parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=RawTextWithDefaultsHelpFormatter,
)
parser.add_argument(
    '-d',
    '--dest',
    default=Path(__file__).parent,
    help='The destination directory for the update package',
)
parser.add_argument(
    '-w',
    '--work-directory',
    default=Path(__file__).parent.joinpath('tmp'),
    help='A temporary directory for this script to store/modify files.'
)
parser.add_argument(
    '-l',
    '--log-file',
    default=Path(__file__).parent.joinpath('build-update.log'),
    help='The path/filename to write logs to for the build. '
         'The log will be overwriten on each invocation.',
)
parser.add_argument(
    '-V',
    '--python-version',
    default='3.11.6',
    help='The version of Python to target for the upgrade',
)
args = parser.parse_args()

def _setup_logging(args):
    level = logging.DEBUG
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log = logging.getLogger(__name__)
    file_handler = logging.FileHandler(
        filename=args.log_file,
        mode='w',
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler(
        stream=sys.stdout,
    )
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)

    log.addHandler(stream_handler)
    log.addHandler(file_handler)
    log.setLevel(level)
    return log

def main(args):
    log = _setup_logging(args)
    log.debug(f'Received args: {args}')

    # Create the working directory
    work_dir = Path(args.work_directory)
    work_dir.mkdir(parents=True, exist_ok=True)

    # Download python embedable zip
    python_zip_url = f'https://www.python.org/ftp/python/{args.python_version}/python-{args.python_version}-embed-amd64.zip'
    response = requests.get(python_zip_url)
    zip_filename = work_dir.joinpath(f'python-{args.python_version}-embed-amd64.zip')
    with zip_filename.open('wb') as fout:
        fout.write(response.content)
    log.info(f'zip_filename: {zip_filename}')

    # Unzip python
    tmp_python_dir = work_dir.joinpath('python').joinpath(args.python_version)
    tmp_python_dir.mkdir(parents=True, exist_ok=True)
    shutil.unpack_archive(zip_filename, tmp_python_dir)
    zip_filename.unlink()

    # Remove ._pth files
    for filename in tmp_python_dir.glob('*._pth'):
        filename.unlink()

    # Download python installer
    python_installer_url = f'https://www.python.org/ftp/python/{args.python_version}/python-{args.python_version}-amd64.exe'
    response = requests.get(python_installer_url)
    installer_filename = work_dir.joinpath(f'python-{args.python_version}-amd64.exe')
    with installer_filename.open('wb') as fout:
        fout.write(response.content)
    log.info(f'installer_filename: {installer_filename}')

    # Install to temporary location
    tmp_python_installation = work_dir.joinpath("tmp_python")
    tmp_python_installation.mkdir(parents=True, exist_ok=True)
    command = f'{installer_filename} InstallAllUsers=0 TargetDir={tmp_python_installation} DefaultJustForMeTargetDir={tmp_python_installation} DefaultCustomTargetDir={tmp_python_installation} AssociateFiles=0 Shortcuts=0 Include_doc=0 Include_launcher=0 InstallLauncherAllUsers=0 Include_test=0 Include_tools=0 /passive'
    ret = subprocess.run(command, check=True)

    # Copy TKinter files to embeded distribution
    tcl_directory = tmp_python_installation.joinpath('tcl')
    tkinter_directory = tmp_python_installation.joinpath('Lib').joinpath('tkinter')
    shutil.copytree(tcl_directory, tmp_python_dir.joinpath('tcl'))
    shutil.copytree(tkinter_directory, tmp_python_dir.joinpath('Lib').joinpath('tkinter'))
    tmp_python_dir.joinpath('DLLs').mkdir(parents=True, exist_ok=True)
    for _filename in ('_tkinter.pyd', 'tcl86t.dll', 'tk86t.dll'):
        shutil.copy(tmp_python_installation.joinpath('DLLs').joinpath(_filename), tmp_python_dir.joinpath('DLLs'))    

    # Uninstall from temporary location
    command = f'{installer_filename} /passive /uninstall'
    ret = subprocess.run(command, check=True)
    tmp_python_installation.rmdir()
    installer_filename.unlink()

    # Download get-pip
    get_pip_url = 'https://bootstrap.pypa.io/get-pip.py'
    get_pip_filename = tmp_python_dir.joinpath('get-pip.py')
    response = requests.get(get_pip_url)
    with get_pip_filename.open('wb') as fout:
        fout.write(response.content)
    log.info(f'get-pip filename: {get_pip_filename}')

    # Run get-pip
    command = f'{str(tmp_python_dir.joinpath("python.exe"))} {str(get_pip_filename)}'
    ret = subprocess.run(command)
    log.info(ret)

    # Install pip dependencies
    pip_install_command = f'{tmp_python_dir.joinpath("Scripts").joinpath("pip.exe")} install -r {os.environ["MAST_HOME"]}\\requirements.txt'
    log.info(f'pip install command: {pip_install_command}')
    out = subprocess.run(pip_install_command, check=True)
    log.info(out)

    # Download zip of mast.installer repo
    repo_zip_url = 'https://github.com/McIndi/mast.installer/archive/refs/heads/python-3.zip'
    repo_zip_filename = work_dir.joinpath('mast.installer.zip')
    response = requests.get(repo_zip_url)
    with repo_zip_filename.open('wb') as fout:
        fout.write(response.content)
    extract_directory = work_dir.joinpath('mast.installer')
    shutil.unpack_archive(repo_zip_filename, extract_directory)
    repo_zip_filename.unlink()

    # Copy .bat file from windows subdirectory to the dist directory
    windows_script_dir = extract_directory.joinpath('mast.installer-python-3')
    windows_script_dir = windows_script_dir.joinpath('mast').joinpath('installer')
    windows_script_dir = windows_script_dir.joinpath('files').joinpath('windows')
    for batch_script in windows_script_dir.glob('*.bat'):
        shutil.copy(batch_script, work_dir)
    
    # Copy nested directories
    files_dir = extract_directory.joinpath('mast.installer-python-3')
    files_dir = files_dir.joinpath('mast').joinpath('installer').joinpath('files')
    shutil.copytree(files_dir.joinpath('contrib'), work_dir.joinpath('contrib'))
    shutil.copytree(files_dir.joinpath('etc'), work_dir.joinpath('etc'))
    shutil.copytree(files_dir.joinpath('var'), work_dir.joinpath('var'))
    
    # Create empty directories
    work_dir.joinpath('bin').mkdir(exist_ok=True)
    work_dir.joinpath('doc').mkdir(exist_ok=True)
    work_dir.joinpath('tmp').mkdir(exist_ok=True)
    work_dir.joinpath('usrbin').mkdir(exist_ok=True)

    # Remove extract directory
    shutil.rmtree(extract_directory)

    # Zip everything up
    archive_filename = Path(args.dest).joinpath(
        f'mast_win64_py{args.python_version}',
    )
    shutil.make_archive(
        archive_filename,
        'zip',
        work_dir,
        '.',
    )

    return 0

# def render_template(string, mappings):
#     for k, v in list(mappings.items()):
#         string = string.replace("<%{}%>".format(k), v)
#     return string

if __name__ == '__main__':
    sys.exit(main(args))