# -*- coding: utf-8 -*-
import os
import sys
from mast.cli import Cli
from mast.timestamp import Timestamp
from mast.datapower import datapower
from mast.logging import make_logger


def _exit(ret_code=-1):
    print "An error occurred, see log for details."
    sys.exit(ret_code)

cli = Cli()


@cli.command()
def to_dp(appliances=[], credentials=[],
          timeout=120, local_dir="",
          remote_dir="", domain="default",
          recursive=False, no_check_hostname=False,
          overwrite=False, create_dir=False):
    """Syncs files from local_dir to remote_dir in the specified
    domain. If the recursive flag is specified, then local_dir
    is recursed"""
    check_hostname = not no_check_hostname
    env = datapower.Environment(
        appliances,
        credentials,
        timeout,
        check_hostname=check_hostname)
    logger = make_logger("fs_sync")

    if not os.path.exists(local_dir):
        logger.error("{} does not exist or is not a directory")
        _exit()

    for appl in env.appliances:
        print appl.hostname
        print "\t{}".format(domain)
        files = []
        if recursive:
            for root, dirs, _files in os.walk(local_dir):
                __files = [os.path.join(root, f) for f in _files]
                files.extend(__files)
        else:
            files = [os.path.join(local_dir, f)
                     for f in os.listdir(local_dir)
                     if os.path.isfile(os.path.join(local_dir, f))]
        targets = ["/".join([remote_dir, f.replace(local_dir, "")])
                   for f in files]
        files = zip(files, targets)

        for f in files:
            print "\t\t{} -> {}".format(f[0], f[1])
            upload_file(appl, domain, f, overwrite, create_dir)


@cli.command()
def from_dp(appliances=[], credentials=[], timeout=120,
            location="", out_dir="tmp", Domain="",
            recursive=False, no_check_hostname=False):
    """This will get all of the files from a directory on the appliances
    in the specified domain."""
    check_hostname = not no_check_hostname
    env = datapower.Environment(
        appliances,
        credentials,
        timeout,
        check_hostname=check_hostname)

    for appliance in env.appliances:
        _out_dir = os.path.join(out_dir, appliance.hostname)
        if not os.path.exists(_out_dir) or not os.path.isdir(_out_dir):
            os.makedirs(_out_dir)
        appliance.copy_directory(
            location, _out_dir, Domain, recursive=recursive)


def upload_file(appl, domain, f, overwrite, create_dir):
    logger = make_logger("fs_sync")

    dirname = "/".join(f[1].split("/")[:-1])
    if create_dir:
        if not appl.directory_exists(dirname, domain):
            print "\t\tCreating Directory {}".format(dirname)
            appl.CreateDir(domain=domain, Dir=dirname)
    else:
        if not appl.directory_exists(dirname, domain):
            logger.error(
                "Directory {} does not exist in {} domain on {}".format(
                    dirname, domain, appl.hostname))
            _exit()
    try:
        resp = appl.set_file(f[0], f[1], domain, overwrite)
        if not resp:
            print "\t\t\tNot overwriting {}".format(f[1])
    except:
        logger.exception("An unhandled exception occurred.")
        print "Uable to upload file {} to {} - {} - {}".format(
            f[0], f[1], domain, appl.hostname)


if __name__ == "__main__":
    try:
        cli.run()
    except:
        make_logger("error").exception(
            "An unhandled exception occurred see log for details")
        raise
