# -*- coding: utf-8 -*-
import re
import os
import sys
from mast.cli import Cli
from mast.timestamp import Timestamp
from mast.datapower import datapower
from mast.logging import make_logger

def _exit(ret_code=-1):
    print("An error occurred, see log for details.")
    sys.exit(ret_code)

cli = Cli()


@cli.command()
def to_dp(appliances=[],
          credentials=[],
          timeout=120,
          no_check_hostname=False,
          local_dir="",
          remote_dir="",
          domain="default",
          recursive=False,
          overwrite=False,
          create_dir=False,
          followlinks=False,
          dry_run=False,
          ignore_errors=False):
    """Syncs files from local_dir to remote_dir in the specified
    domain. If the recursive flag is specified, then local_dir
    is recursed"""
    logger = make_logger("fs-sync")
    remote_dir = remote_dir.rstrip("/")
    location = remote_dir.split(":")[0] + ":"

    check_hostname = not no_check_hostname
    env = datapower.Environment(
        appliances,
        credentials,
        timeout,
        check_hostname=check_hostname)

    if not os.path.exists(local_dir):
        logger.error("{} does not exist or is not a directory")
        _exit()

    for appl in env.appliances:
        filestore = appl.get_filestore(domain=domain,
                                       location=location)
        print((appl.hostname))
        print(("\t{}".format(domain)))
        files = []
        if recursive:
            for root, dirs, _files in os.walk(local_dir, followlinks=followlinks):
                __files = [os.path.join(root, f) for f in _files]
                files.extend(__files)
        else:
            files = [os.path.join(local_dir, f)
                     for f in os.listdir(local_dir)
                     if os.path.isfile(os.path.join(local_dir, f))]
        targets = ["/".join([remote_dir, f.replace(local_dir, "")])
                   for f in files]
        targets = [x.replace(os.path.sep, "/") for x in targets]
        targets = [x.replace("//", "/") for x in targets]
        targets = [re.sub(r":[/]*", r":///", x) for x in targets]
        files = list(zip(files, targets))

        for f in files:
            print(("\t\t{}  ->  {}".format(f[0], f[1])))
            if not dry_run:
                try:
                    filestore = upload_file(appl, domain, f, overwrite, create_dir, ignore_errors, filestore)
                except:
                    logger.exception("An error has occurred uploading "
                                     "{} to {} on {}:{}".format(f[0],
                                                                f[1],
                                                                appl.hostname,
                                                                domain))
                    print("\t\t\tERROR uploading above file stacktrace is in the logs:")
                    if ignore_errors:
                        pass
                    else:
                        raise


@cli.command()
def from_dp(appliances=[],
            credentials=[],
            timeout=120,
            no_check_hostname=False,
            location="",
            out_dir="tmp",
            domains=["all-domains"],
            recursive=False,
            ignore_errors=False):
    """This will get all of the files from a directory on the appliances
    in the specified domain."""
    logger = make_logger("fs-sync")
    check_hostname = not no_check_hostname
    env = datapower.Environment(
        appliances,
        credentials,
        timeout,
        check_hostname=check_hostname)

    for appliance in env.appliances:
        logger.info("Syncing with {}".format(appliance.hostname))
        print((appliance.hostname))
        _domains = domains
        if "all-domains" in _domains:
            _domains = appliance.domains
        for domain in _domains:
            print(("\t", domain))
            _out_dir = os.path.join(out_dir, appliance.hostname)
            print(("\t\t", location, "->", _out_dir))
            if not os.path.exists(_out_dir) or not os.path.isdir(_out_dir):
                logger.info("Making directory {}".format(_out_dir))
                os.makedirs(_out_dir)
            try:
                download_directory(appliance,
                                   location,
                                   _out_dir,
                                   domain,
                                   recursive=recursive,
                                   ignore_errors=ignore_errors)
            except:
                logger.exception("An error occurred during download of "
                                 "{} to {} from {}:{}".format(location,
                                                              _out_dir,
                                                              appliance.hostname,
                                                              domain))
                print("\t\t\tERROR downloading above directory stacktrace can be found in the logs")
                if ignore_errors:
                    pass
                else:
                    raise

def upload_file(appl, domain, f, overwrite, create_dir, ignore_errors, filestore=None):
    logger = make_logger("fs-sync")

    dirname = "/".join(f[1].split("/")[:-1])
    location = dirname.split(":")[0] + ":"
    if filestore is None:
        filestore = appl.get_filestore(domain=domain,
                                       location=location)

    if create_dir:
        if (not appl.directory_exists(dirname, domain, filestore)) and (not appl.location_exists(dirname, domain, filestore)):
            print(("\t\t\tCreating Directory {}".format(dirname)))
            resp = appl.CreateDir(domain=domain, Dir=dirname)
            if "<error-log>" in resp.text:
                logger.error("An error occurred creating directory {} on {}:{}".format(dirname, appl.hostname, domain))
                print("\t\t\t\tERROR Creating directory, stack trace can be found in the logs")
                if not ignore_errors:
                    raise datapower.AuthenticationFailure
            filestore = appl.get_filestore(domain=domain,
                                           location=location)
    else:
        if (not appl.directory_exists(dirname, domain, filestore)) and (not appl.location_exists(dirname, domain, filestore)):
            logger.error(
                "Directory {} does not exist in {} domain on {}".format(
                    dirname, domain, appl.hostname))
            _exit()
    resp = appl.set_file(f[0], f[1], domain, overwrite, filestore)
    if not resp:
        print(("\t\t\tNot overwriting {}".format(f[1])))
    return filestore


def download_directory(appl,
                       dp_path,
                       local_path,
                       domain='default',
                       recursive=True,
                       filestore=None,
                       ignore_errors=False):
    """
    _function_: `fs-sync:download_directory(self, dp_path, local_path, domain='default', recursive=True, filestore=None, ignore_errors=False)`

    This will copy the contents of dp_path to local_path.

    Returns: None

    Usage:

        :::python
        >>> dp = DataPower("localhost", "user:pass")
        >>> download_directory(dp, "local:", "/tmp", "default", True)

    Parameters:

    * `dp_path`: The directory/location on the appliance, you would
    like to copy locally
    * `local_path`: The base directory to copy the files to
    * `domain`: The domain from which to copy the files
    * `recursive`: Whether or not to recurse into sub-directories
    * `filestore`: The filestore of the location in which `dp_path`
    resides. If this is not passed in, the filestore will be
    retrieved from the appliance. This is to help when acting
    recursively so the filestore is retrieved only once
    * `ignore-errors`: If True, errors will be logged and presented to
    user on stdout, but no exception will be raised
    """
    logger = make_logger("fs-sync")
    dp_path = dp_path.replace("///", "/").rstrip("/")

    _path = dp_path.replace(":", "").strip("/")
    _path = _path.replace("/", os.path.sep)
    if _path not in local_path:
        local_path = os.path.join(local_path, _path)
    try:
        os.makedirs(local_path)
    except OSError:
        pass

    if filestore is None:
        location = '{}:'.format(dp_path.split(':')[0])
        try:
            filestore = appl.get_filestore(domain=domain,
                                           location=location)
        except TypeError:
            logger.error(
                "Error reading directory"
                ": %s, request: %s, response: %s" % (
                    dir, appl.request, appl.last_response.read()))
            print(("ERROR: while reading directory {}".format(location)))
            if ignore_errors:
                return ""
            else:
                raise
    files = appl.ls(dp_path,
                    domain=domain,
                    include_directories=recursive,
                    filestore=filestore)

    for file in files:
        logger.info("Getting file {}".format(file))
        if file.endswith("/"):
            _local_path = os.path.join(local_path,
                                       file[:-1].split("/")[-1])
            try:
                os.makedirs(_local_path)
            except:
                pass
            download_directory(appl,
                               file,
                               _local_path,
                               domain=domain,
                               filestore=filestore,
                               ignore_errors=ignore_errors)
            continue
        filename = os.path.join(local_path, file.split('/')[-1])
        with open(filename, 'wb') as fout:
            fname = '{}/{}'.format(dp_path, file)
            print(("\t\t\t{} -> {}".format(fname, filename)))
            try:
                fout.write(appl.getfile(domain=domain, filename=fname))
            except:
                logger.exception("An unhandled exception occurred")
                print(("ERROR: While downloading {} from {}:{}".format(fname,
                                                                      appl.hostname,
                                                                      domain)))
                if ignore_errors:
                    pass
                else:
                    raise

if __name__ == "__main__":
    try:
        cli.run()
    except:
        make_logger("error").exception(
            "An unhandled exception occurred see log for details")
        raise
